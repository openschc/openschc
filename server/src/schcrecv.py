#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy
from threading import Timer
import schc
import schcmsg
from schcbitmap import find_missing_tiles, sort_tile_list

#---------------------------------------------------------------------------

class ReassembleBase:

    def __init__(self, protocol, context, rule, dtag, sender_L2addr):
        self.protocol = protocol
        self.context = context
        self.rule = rule
        self.dtag = dtag
        self.sender_L2addr = sender_L2addr
        self.tile_list = []
        self.mic_received = None
        self.inactive_timer = 10
        self.event_id_inactive_timer = None
        # state:
        #   INIT:
        #   DONE: sent ACK success. only accept ACK REQ.
        self.state = "INIT"

    def get_mic(self, mic_target, extra_bits=0):
        assert isinstance(mic_target, bytearray)
        mic = get_mic(mic_target)
        print()
        print("----------------------[SCHC RECV]-----------------------")
        print("Recv MIC {}, base = {}".format(mic, mic_target))
        print("------------------------------------------------------")
        
        return mic.to_bytes(4, "big")

    def event_inactive(self):
        # sending sender abort.
        schc_frag = schcmsg.frag_receiver_tx_abort(self.rule, self.dtag)
        args = (schc_frag.packet.get_content(), self.protocol.layer2.mac_id,
                None, None)
        print("Sent Receiver-Abort.", schc_frag.__dict__)
        self.protocol.scheduler.add_event(0,
                                    self.protocol.layer2.send_packet, args)
        # XXX needs to release all resources.
        return

    def cancel_inactive_timer(self):
        print("cancel incative timer ", self.inactive_timer)
        if self.event_id_inactive_timer is None:
            return
        self.protocol.scheduler.cancel_event(self.event_id_inactive_timer)
        self.event_id_inactive_timer = None
        
#---------------------------------------------------------------------------

class ReassemblerNoAck(ReassembleBase):

    def receive_frag(self, bbuf, dtag):
        # XXX context should be passed from the lower layer.
        # XXX and pass the context to the parser.
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        
        print()
        print("----------------------[SCHC RECV]-----------------------")
        print("receiver frag received: ")
        print(schc_frag.__dict__)
        print("------------------------------------------------------")
        # XXX how to authenticate the message from the peer. without
        # authentication, any nodes can cancel the invactive timer.
        self.cancel_inactive_timer()
        
        #
        if schc_frag.abort == True:
            print("Received Sender-Abort.")
            # XXX needs to release all resources.
            return None, False, None
        self.tile_list.append(schc_frag.payload)
        #
        if schc_frag.fcn == schcmsg.get_fcn_all_1(self.rule):
            print("ALL1 received")
            # MIC calculation
            print("tile_list")
            for _ in self.tile_list:
                print(_)
            schc_packet = BitBuffer()
            for i in self.tile_list:
                schc_packet += i
            
            #schc_packet = bytearray(range(1, 100+1))
            mic_calced = self.get_mic(schc_packet.get_content())
            #mic_calced = self.get_mic(schc_packet)
            '''print()
            print("SCHC PACKET ", schc_packet)
            print()
            print("MIC calculado: ", mic_calced.hex())'''
            print()
            print("*****MIC recibido ",schc_frag.mic)
            print("*****MIC calculado ",mic_calced)
            
            if schc_frag.mic != mic_calced:
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag.mic.hex(), mic_calced.hex()))
                return None, False, None
            # decompression
            self.protocol.process_decompress(self.context, self.sender_L2addr,
                                             schc_packet)
            
            return schc_packet, False, None
        # set inactive timer.
        print("inactive timer ", self.inactive_timer)
        self.event_id_inactive_timer = self.protocol.scheduler.add_event(
                self.inactive_timer, self.event_inactive, tuple())
        #self.protocol.scheduler.run()
        #if len(self.protocol.scheduler.queue) == 1:
         #   self.protocol.scheduler.run()
        print("---", schc_frag.fcn)
        print("set timer ", self.inactive_timer)
        return None, False, None
#---------------------------------------------------------------------------

class ReassemblerAckOnError(ReassembleBase):

    # In ACK-on-Error, a fragment contains tiles belonging to different window.
    # A type of data structure holding tiles in each window is not suitable.  
    # So, here just appends a fragment into the tile_list like No-ACK.
    def receive_frag(self, bbuf, dtag):
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        print()
        print("----------------------[SCHC RECV]-----------------------")
        print("receiver frag received: ")
        print(schc_frag.__dict__)
        print("------------------------------------------------------")
        # XXX how to authenticate the message from the peer. without
        # authentication, any nodes can cancel the invactive timer.
        self.cancel_inactive_timer()
        
        #
        if schc_frag.abort == True:
            print("Received Sender-Abort.")
            # XXX needs to release all resources.
            return None, False, None
        if self.state == "DONE":
            print("XXX need sending ACK back.")
            return None, False, None
        # append the payload to the tile list.
        # padding truncation is done later. see below.
        
        nb_tiles = schc_frag.payload.count_added_bits()//self.rule.get("fragmentation").get("FRModeProfile").get("tileSize")
        # Note that nb_tiles is the number of tiles which is exact number of the
        # size of the tile.  the tile of which the size is less than the size
        # is not included.
        
        self.tile_list.append({
                "w-num": schc_frag.win,
                "t-num": schc_frag.fcn,
                "nb_tiles": nb_tiles,
                "raw_tiles":schc_frag.payload})
        self.tile_list = sort_tile_list(self.tile_list, self.rule.get("fragmentation").get("FRModeProfile").get("FCNSize"))
        print("MIC REC ",self.mic_received)
        if self.mic_received is not None:
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            if self.mic_received == mic_calced:
                answer = self.finish(schc_packet, schc_frag)
                return schc_packet, True, answer
            else:
                # XXX waiting for the fragments requested by ACK.
                # during MAX_ACK_REQUESTS
                print("waiting for more fragments.")
        elif schc_frag.fcn == schcmsg.get_fcn_all_1(self.rule):
            print("ALL1 received")
            self.mic_received = schc_frag.mic
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            if schc_frag.mic == mic_calced:
                answer = self.finish(schc_packet, schc_frag)
                #if the mic is okay
                return schc_packet, True, answer
            else:
                print()
                print("----------------------[SCHC recv]-----------------------")
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag.mic, mic_calced))
                print()
                print("tile_list ",self.tile_list)
                print("------------------------------------------------------")
                
                bit_list = find_missing_tiles(self.tile_list,self.rule.get("fragmentation").get("FRModeProfile").get("FCNSize"),
                                              schcmsg.get_fcn_all_1(self.rule))
                print("FCNsize: ",self.rule.get("fragmentation").get("FRModeProfile").get("FCNSize"),"schcmsg.get_fcn_all_1(self.rule)", schcmsg.get_fcn_all_1(self.rule))
                assert bit_list is not None
                print("bit_list: ",bit_list)
                print()
                for bl_index in range(len(bit_list)):
                    print("missing wn={} bitmap={}".format(bit_list[bl_index][0],
                                                           bit_list[bl_index][1]))
                    # XXX compress bitmap if needed.
                    # ACK failure message
                    schc_ack = schcmsg.frag_receiver_tx_all1_ack(
                            schc_frag.rule,
                            schc_frag.dtag,
                            win=bit_list[bl_index][0],
                            cbit=0,
                            bitmap=bit_list[bl_index][1])
                    print("ACK failure sent:", schc_ack.__dict__)
                    src_dev_id = self.protocol.layer2.mac_id
                    N = self.rule.get("fragmentation").get("FRModeProfile").get("FCNSize")
                    print("FNC SIZE ", N)
                    all1 =  (1<<N)-1  
                    print("all in 1 ",all1,"bit_list[bl_index][1] ", bit_list[bl_index][1])
                    bitHexa = bit_list[bl_index][1]._content.hex()
                    
                    bit=""
                    for n in range(0,len(bitHexa)):
                        bit+="0" 
                    print("hexa, ",bitHexa, "bit ",bit)
                    if bitHexa == bit:
                        answer = self.protocol.layer2.send_ack(schc_ack.packet.get_content(), src_dev_id)
                        return None, True, answer  
                    
                    

                    #args = (schc_ack.packet.get_content(), src_dev_id,None, None)
                    #self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet, args)
                    #self.protocol.scheduler.add_event(0, self.protocol.layer2.send_ack, args)
                      
                    # XXX need to keep the ack message for the ack request.
        # set inactive timer.
        self.event_id_inactive_timer = self.protocol.scheduler.add_event(
                self.inactive_timer, self.event_inactive, tuple())
        #self.protocol.scheduler.run()
        print("---", schc_frag.fcn)
        return None, False, None

    def finish(self, schc_packet, schc_frag):
        self.state = "DONE"
        # decompression
        #self.protocol.process_decompress(self.context, self.sender_L2addr,schc_packet)
        # ACK message
        schc_ack = schcmsg.frag_receiver_tx_all1_ack(schc_frag.rule,schc_frag.dtag,schc_frag.win,cbit=1)
        src_dev_id = self.protocol.layer2.mac_id        
        print()
        print("----------------------[SCHC recv]-----------------------")
        print("Sending ACK:", schc_ack.__dict__,"  src_dev_id ",src_dev_id)
        print("PACKET CONTENT: ", schc_ack.packet.get_content().hex())
        print("------------------------------------------------------")
        print()
        
        
        #args = (schc_ack.packet.get_content(), src_dev_id, None, None)
        #self.protocol.scheduler.add_event(0,self.protocol.layer2.send_packet,args)
        answer = self.protocol.layer2.send_ack(schc_ack.packet.get_content(), src_dev_id)
        #args = (schc_ack.packet.get_content(), src_dev_id)
        #self.protocol.scheduler.add_event(0,self.protocol.layer2.send_ack,args)
        return answer

        # XXX need to keep the ack message for the ack request.

    def get_mic_from_tiles_received(self):
        # MIC calculation.
        # The truncation of the padding should be done here
        # because the padding of the last tile must be included into the
        # MIC calculation.  However, the fact that the last tile is
        # received can be known after the All-1 fragment is received.
        assert len(self.tile_list) > 0
        print("tile_list:")
        for _ in self.tile_list:
            print()
        schc_packet = BitBuffer()
        
        if len(self.tile_list) > 1:
            for i in self.tile_list[:-2]:
                # it needs to copy the buffer as it will be reused later.
                tiles = i["raw_tiles"].copy().get_bits_as_buffer(
                    i["nb_tiles"]*self.rule.get("fragmentation").get("FRModeProfile").get("tileSize"))
                schc_packet += tiles
            # check the size of the padding in the All-1 fragment.
            if (self.tile_list[-1]["raw_tiles"].count_added_bits() <
                self.rule.get("profile").get("L2WordSize")):
                # the last tile exists in the fragment before the All-1
                # fragment and the payload has to add as it is.
                # the All-1 fragment doesn't need to taken into account
                # of the MIC calculation.
                schc_packet += self.tile_list[-2]["raw_tiles"]
            else:
                # the last tile exists in the All-1 fragment.
                # it needs to truncate the padding in the fragment before that.
                i = self.tile_list[-2]
                schc_packet += i["raw_tiles"].copy().get_bits_as_buffer(
                    i["nb_tiles"]*self.rule.get("fragmentation").get("FRModeProfile").get("tileSize"))
                schc_packet += self.tile_list[-1]["raw_tiles"]
        else:
            # len(self.tile_list) == 1
            # add into the packet as it is.
            schc_packet += self.tile_list[0]["raw_tiles"]
        # get the target of MIC from the BitBuffer.
        print("MIC calculation:")
        mic_calced = self.get_mic(schc_packet.get_content())
        return schc_packet, mic_calced

#---------------------------------------------------------------------------

        
