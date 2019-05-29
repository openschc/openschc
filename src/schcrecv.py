"""OpenSCHC Reception Functionality

"""
#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg
from schcbitmap import find_missing_tiles, sort_tile_list, find_missing_tiles_no_all_1, find_missing_tiles_mic_ko_yes_all_1

enable_statsct = True
if enable_statsct:
    from stats.statsct import Statsct

#---------------------------------------------------------------------------

"""
.. module:: schcrecv
    :platform: Code Running on MicroPython
    :synopsis: SCHC Reception Module

"""

class ReassembleBase:
    """This class is used as a common base for Reassembling packets

    """

    def __init__(self, protocol, context, rule, dtag, sender_L2addr):
        """
        
        Args :
            protocol : protocol
            context : context
            rule : rule can be either "comp" for compression, "fragSender" for fragmentation from sender and "fragReceiver" for fragmentation from receiver
            dtag : ?
            sender_L2addr : None or 'int' containing the sender's address
     
                
        """
        self.protocol = protocol
        self.context = context
        self.rule = rule
        self.dtag = dtag
        self.sender_L2addr = sender_L2addr
        self.tile_list = []
        self.mic_received = None
        self.inactive_timer = 200
        self.event_id_inactive_timer = None
        # state:
        #   INIT:
        #   DONE: sent ACK success. only accept ACK REQ.
        #   ALL-1: All-1 messages has been received
        #   ABORT: receiver abort send, reject any message with abort
        self.state = "INIT"
        self.schc_ack = None
        self.all1_received = False
        self.mic_missmatched = False

        self.fragment_received = False
        


    def get_mic(self, mic_target, extra_bits=0):
        """This gets the mic
        
        This function gets the mic and display it in a 4 byte format
        
        """

        assert isinstance(mic_target, bytearray)
        mic = get_mic(mic_target)
        print("Recv MIC {}, base = {}, lenght = {}".format(mic, mic_target, len(mic_target)))
        return mic.to_bytes(4, "big")

    def event_inactive(self):
        """ event_inactive
        
        // TODO : Redaction (here is schcrecv.py)
        
        
        """
        #if the ack-ok was received, no ACK REQ will be received,
        #check for state == "DONE" and return, this means that the ack-ok
        #was send, before the system returns after sending the ack-ok, now it 
        #waits for one inactivity timer before closing session
        if self.state == "DONE":
            return

        # sending Receiver abort.
        schc_frag = schcmsg.frag_receiver_tx_abort(self.rule, self.dtag)
        args = (schc_frag.packet.get_content(), self.context["devL2Addr"])
        print("Sent Receiver-Abort.", schc_frag.__dict__)
        print("----------------------- SCHC RECEIVER ABORT SEND  -----------------------")

        if enable_statsct:
            Statsct.set_msg_type("SCHC_RECEIVER_ABORT")
            #Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
        self.state = "ABORT"
        self.protocol.scheduler.add_event(0,
                                    self.protocol.layer2.send_packet, args)
        # XXX needs to release all resources.
        return

    def cancel_inactive_timer(self):
        """ cancel_inactive_timer
        
        // TODO : Redaction (here is schcrecv.py)
        
        """
        if self.event_id_inactive_timer is None:
            return
        self.protocol.scheduler.cancel_event(self.event_id_inactive_timer)
        self.event_id_inactive_timer = None

#---------------------------------------------------------------------------

class ReassemblerNoAck(ReassembleBase):
    """ ReassemblerNoAck class
    
    // Todo : Redaction
    
    """
    def receive_frag(self, bbuf, dtag):
        # XXX context should be passed from the lower layer.
        # XXX and pass the context to the parser.
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        print("receiver frag received:", schc_frag.__dict__)
        # XXX how to authenticate the message from the peer. without
        # authentication, any nodes can cancel the invactive timer.
        self.cancel_inactive_timer()
        #
        if schc_frag.abort == True:
            print("Received Sender-Abort.")
            # XXX needs to release all resources.
            return
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
            mic_calced = self.get_mic(schc_packet.get_content())
            if schc_frag.mic != mic_calced:
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag.mic, mic_calced))
                return
            # decompression
            self.protocol.process_decompress(self.context, self.sender_L2addr,
                                             schc_packet)
            return
        # set inactive timer.
        self.event_id_inactive_timer = self.protocol.scheduler.add_event(
                self.inactive_timer, self.event_inactive, tuple())
        print("---", schc_frag.fcn)

#---------------------------------------------------------------------------

class ReassemblerAckOnError(ReassembleBase):
    """ ReassemblerAckOnError class
    
    Todo : Redaction
    
    """
    # In ACK-on-Error, a fragment contains tiles belonging to different window.
    # A type of data structure holding tiles in each window is not suitable.  
    # So, here just appends a fragment into the tile_list like No-ACK.
    
    def receive_frag(self, bbuf, dtag):
        
        print('state: {}, recieved fragment -> {}, rule-> {}'.format(self.state,
                                bbuf, self.rule))
        
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        print("receiver frag received:", schc_frag.__dict__)
        # XXX how to authenticate the message from the peer. without
        # authentication, any nodes can cancel the invactive timer.
        self.cancel_inactive_timer()
        if self.state == "ABORT":
            self.send_receiver_abort()
            return
        #
        #input("")
        if schc_frag.abort == True:
            print("Received Sender-Abort.")
            #Statsct.set_msg_type("SCHC_SENDER_ABORT")
            # XXX needs to release all resources.
            return
          
        if schc_frag.ack_request == True:
            print("Received ACK-REQ")
            # if self.state != "DONE":
            #     #this can happen when the ALL-1 is not received, so the state is
            #     #not done and the sender is requesting an ACK.
            #     # sending Receiver abort.
            #     schc_frag = schcmsg.frag_receiver_tx_abort(self.rule, self.dtag)
            #     args = (schc_frag.packet.get_content(), self.context["devL2Addr"])
            #     print("Sent Receiver-Abort.", schc_frag.__dict__)
            #     print("----------------------- SCHC RECEIVER ABORT SEND  -----------------------")

            #     if enable_statsct:
            #         Statsct.set_msg_type("SCHC_RECEIVER_ABORT")
            #         #Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
            #     self.protocol.scheduler.add_event(0,
            #                                 self.protocol.layer2.send_packet, args)
            #     # XXX needs to release all resources.
            #     return
            print("XXX need sending ACK back.")
            #input('')
            self.resend_ack(schc_frag)
            return
        
        self.fragment_received = True
        # append the payload to the tile list.
        # padding truncation is done later. see below.
        nb_tiles = schc_frag.payload.count_added_bits()//self.rule["tileSize"]
        # Note that nb_tiles is the number of tiles which is exact number of the
        # size of the tile.  the tile of which the size is less than the size
        # is not included.
        # The tile that is less than a tile size must be included, so a 1 can be added
        # in the bitmap when there is a tile in the all-1 message
        if schc_frag.payload.count_added_bits()%self.rule["tileSize"] != 0:
            #tile found that is smaller than a normal tile
            print("tile found that is smaller than a normal tile")
            nb_tiles = 1
        self.tile_list.append({
                "w-num": schc_frag.win,
                "t-num": schc_frag.fcn,
                "nb_tiles": nb_tiles,
                "raw_tiles":schc_frag.payload})
        #self.tile_list = sort_tile_list(self.tile_list, self.rule["FCNSize"])
        self.tile_list = sort_tile_list(self.tile_list, self.rule["WSize"])

        if self.mic_received is not None:
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            if self.mic_received == mic_calced:
                self.finish(schc_packet, schc_frag)
                return
            else:
                # XXX waiting for the fragments requested by ACK.
                # during MAX_ACK_REQUESTS
                print("waiting for more fragments.")
        elif schc_frag.fcn == schcmsg.get_fcn_all_1(self.rule):
            print("----------------------- ALL1 received -----------------------")
            self.all1_received = True
            #Statsct.set_msg_type("SCHC_ALL_1")
            self.mic_received = schc_frag.mic
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            print("schc_frag.mic: {}, mic_calced: {}".format(schc_frag.mic,mic_calced))
            if schc_frag.mic == mic_calced:
                self.mic_missmatched = False
                self.finish(schc_packet, schc_frag)
                return
            else:
                self.mic_missmatched = True
                print("----------------------- ERROR -----------------------")
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag.mic, mic_calced))
                bit_list = find_missing_tiles_mic_ko_yes_all_1(self.tile_list,
                                              self.rule["FCNSize"],
                                              schcmsg.get_fcn_all_1(self.rule))
                
                assert bit_list is not None
                if len(bit_list) == 0:
                    #When the find_missing_tiles functions returns an empty array
                    #but we know something is missing because the MIC calculation is wrong
                    #this can happen when the first fragments are lost for example
                    print("bit list empty but the mic missmatched")
                    #if tiles are missing, then the packet is larger, should send a bitmap
                    #that considers the max_fcn and the tiles received
                    bit_list = find_missing_tiles_mic_ko_yes_all_1(self.tile_list,
                                                self.rule["FCNSize"],
                                                schcmsg.get_fcn_all_1(self.rule))
                    #print("new bit list, should it work???")
                    #input("")
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
                    if enable_statsct:
                        Statsct.set_msg_type("SCHC_ACK_KO")
                    print("----------------------- SCHC ACK KO SEND  -----------------------")

                    print("ACK failure sent:", schc_ack.__dict__)
                    args = (schc_ack.packet.get_content(),
                            self.context["devL2Addr"])
                    self.protocol.scheduler.add_event(
                            0, self.protocol.layer2.send_packet, args)
                    # XXX need to keep the ack message for the ack request.
        # set inactive timer.
        self.event_id_inactive_timer = self.protocol.scheduler.add_event(
                self.inactive_timer, self.event_inactive, tuple())
        print("---", schc_frag.fcn)

    def resend_ack(self, schc_frag):
        print("resend ack method")
        print(schc_frag.__dict__)
        if self.mic_received is not None:
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            print("schc_frag.mic: {}, mic_calced: {}".format(self.mic_received,mic_calced))
            if self.mic_received == mic_calced:
                self.state = "DONE"
        if self.state == "DONE":
            # ACK message
            schc_ack = schcmsg.frag_receiver_tx_all1_ack(
                schc_frag.rule,
                schc_frag.dtag,
                schc_frag.win,
                cbit=1)
            print("ACK success sent:", schc_ack.__dict__)
            if enable_statsct:
                Statsct.set_msg_type("SCHC_ACK_OK")
            print("----------------------- SCHC ACK OK SEND  -----------------------")
        else:
            if self.all1_received:
                print("all-1 received, building ACK")
                print('send ack before done {},{},{}'.format(self.tile_list,
                            self.rule["FCNSize"], schcmsg.get_fcn_all_1(self.rule)))
                bit_list = find_missing_tiles_mic_ko_yes_all_1(self.tile_list,
                                                self.rule["FCNSize"],
                                                schcmsg.get_fcn_all_1(self.rule))
                print('send ack before done {}'.format(bit_list))
                assert bit_list is not None
                if len(bit_list) == 0:
                    #When the find_missing_tiles functions returns an empty array
                    #but we know something is missing because the MIC calculation is wrong
                    #this can happen when the first fragments are lost
                    print("bit list empty")
                    bit_list = find_missing_tiles_mic_ko_yes_all_1(self.tile_list,
                                                self.rule["FCNSize"],
                                                schcmsg.get_fcn_all_1(self.rule))
                    print("new bit list, should it work???")

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
                    if enable_statsct:
                        Statsct.set_msg_type("SCHC_ACK_KO")
                    print("----------------------- SCHC ACK KO SEND  -----------------------")

                    print("ACK failure sent:", schc_ack.__dict__)
            else:
                #special case when the ALL-1 message is lost: 2 cases:
                #1) the all-1 carries a tile (bit in bitmap)
                #2) the all-1 only carries the MIC (no bit in bitmap)
                if self.fragment_received is False:
                    print("no fragments received yet, abort")
                    self.send_receiver_abort()
                
                    return
                print("all-1 not received, building ACK")
                print('send ack before done {},{},{}'.format(self.tile_list,
                            self.rule["FCNSize"], schcmsg.get_fcn_all_1(self.rule)))
                bit_list = find_missing_tiles_no_all_1(self.tile_list,
                                                self.rule["FCNSize"],
                                                schcmsg.get_fcn_all_1(self.rule))
                print('send ack before done {}'.format(bit_list))
                assert bit_list is not None
                if len(bit_list) == 0:
                    bit_list = find_missing_tiles_no_all_1(self.tile_list,
                                                self.rule["FCNSize"],
                                                schcmsg.get_fcn_all_1(self.rule))
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
                    if enable_statsct:
                        Statsct.set_msg_type("SCHC_ACK_KO")
                    print("----------------------- SCHC ACK KO SEND  -----------------------")

                    print("ACK failure sent:", schc_ack.__dict__)




        args = (schc_ack.packet.get_content(), self.context["devL2Addr"])
        self.protocol.scheduler.add_event(0,
                                            self.protocol.layer2.send_packet,
                                            args)
        # XXX need to keep the ack message for the ack request.
    def finish(self, schc_packet, schc_frag):
        self.state = "DONE"
        print('state DONE -> {}'.format(self.state))
        #input('DONE')
        # decompression
        self.protocol.process_decompress(self.context, self.sender_L2addr,
                                         schc_packet)
        # ACK message
        schc_ack = schcmsg.frag_receiver_tx_all1_ack(
                schc_frag.rule,
                schc_frag.dtag,
                schc_frag.win,
                cbit=1)
        print("ACK success sent:", schc_ack.__dict__)
        if enable_statsct:
            Statsct.set_msg_type("SCHC_ACK_OK")
        print("----------------------- SCHC ACK OK SEND  -----------------------")
        args = (schc_ack.packet.get_content(), self.context["devL2Addr"])
        self.protocol.scheduler.add_event(0,
                                            self.protocol.layer2.send_packet,
                                            args)
        # XXX need to keep the ack message for the ack request.
        #the ack is build everytime
        self.schc_ack = schc_ack
        # set inactive timer.
        #self.event_id_inactive_timer = self.protocol.scheduler.add_event(
        #        self.inactive_timer, self.event_inactive, tuple())
        #print("DONE, but in case of ACK REQ MUST WAIT ", schc_frag.fcn)

    def get_mic_from_tiles_received(self):
        # MIC calculation.
        # The truncation of the padding should be done here
        # because the padding of the last tile must be included into the
        # MIC calculation.  However, the fact that the last tile is
        # received can be known after the All-1 fragment is received.
        assert len(self.tile_list) > 0
        print("tile_list:")
        for _ in self.tile_list:
            print(_)
        schc_packet = BitBuffer()
        if len(self.tile_list) > 1:
            for i in self.tile_list[:-2]:
                # it needs to copy the buffer as it will be reused later.
                tiles = i["raw_tiles"].copy().get_bits_as_buffer(
                    i["nb_tiles"]*self.rule["tileSize"])
                schc_packet += tiles
            # check the size of the padding in the All-1 fragment.
            if (self.tile_list[-1]["raw_tiles"].count_added_bits() <
                self.rule["L2WordSize"]):
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
                    i["nb_tiles"]*self.rule["tileSize"])
                schc_packet += self.tile_list[-1]["raw_tiles"]
        else:
            # len(self.tile_list) == 1
            # add into the packet as it is.
            schc_packet += self.tile_list[0]["raw_tiles"]
        # get the target of MIC from the BitBuffer.
        print("MIC calculation:")
        mic_calced = self.get_mic(schc_packet.get_content())
        return schc_packet, mic_calced

    def send_receiver_abort(self):
        # sending Receiver abort.
        self.state = "ABORT"
        schc_frag = schcmsg.frag_receiver_tx_abort(self.rule, self.dtag)
        args = (schc_frag.packet.get_content(), self.context["devL2Addr"])
        print("Sent Receiver-Abort.", schc_frag.__dict__)
        print("----------------------- SCHC RECEIVER ABORT SEND  -----------------------")

        if enable_statsct:
            Statsct.set_msg_type("SCHC_RECEIVER_ABORT")
            #Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
        self.protocol.scheduler.add_event(0,
                                    self.protocol.layer2.send_packet, args)
#---------------------------------------------------------------------------
