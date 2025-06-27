"""OpenSCHC Reception Functionality

"""
#---------------------------------------------------------------------------

from gen_base_import import *  # used for now for differing modules in py/upy

import frag_msg
from frag_bitmap import find_missing_tiles, sort_tile_list, find_missing_tiles_no_all_1, find_missing_tiles_mic_ko_yes_all_1, make_bit_list_mic_ko
from compr_core import *

from gen_utils import dtrace
import binascii

enable_statsct = True
if enable_statsct:
    from stats.statsct import Statsct

#---------------------------------------------------------------------------

"""
.. module:: frag_recv
    :platform: Code Running on MicroPython
    :synopsis: SCHC Reception Module

"""

class ReassembleBase:
    """This class is used as a common base for Reassembling packets

    """

    def __init__(self, protocol=None, context=None, rule=None, dtag=None, core_id=None, device_id=None):
        """
        Args :
            protocol : protocol
            context : context
            rule : rule can be either "comp" for compression, "fragSender" for fragmentation from sender and "fragReceiver" for fragmentation from receiver
            dtag : ?
            sender_L2addr : None or 'int' containing the sender's address

        """
        self.protocol = protocol

        if protocol.role == T_POSITION_CORE:
            sender_L2addr = device_id
        else: 
            sender_L2addr = core_id

        self.context = context
        self.rule = rule
        self.dtag = dtag
        self.sender_L2addr = sender_L2addr
        self.tile_list = []
        self.mic_received = None
        self.inactive_timer = 200 #last value 120
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
        self._last_receive_info = None # for logs

    def get_mic(self, mic_target, extra_bits=0):
        """This gets the mic

        This function gets the mic and display it in a 4 byte format

        """

        assert isinstance(mic_target, bytearray)
        mic = get_mic(mic_target).to_bytes(4, "big")
        dprint("Recv MIC {}, base = {}, lenght = {}".format(mic.hex(), mic_target, len(mic_target)))
        return mic

    def event_inactive(self):
        """ event_inactive

        // TODO : Redaction (here is frag_recv.py)


        """
        #if the ack-ok was received, no ACK REQ will be received,
        #check for state == "DONE" and return, this means that the ack-ok
        #was send, before the system returns after sending the ack-ok, now it
        #waits for one inactivity timer before closing session
        if self.state == "DONE":
            return

        if self.protocol.position == T_POSITION_CORE:
            dest = self._session_id[1]
        else:
            dest = self._session_id[0]

        # sending receiver abort.
        schc_frag = frag_msg.frag_receiver_tx_abort(self.rule, self.dtag)
        args = (schc_frag.packet.get_content(), dest)
        dprint("Sent Receiver-Abort.", schc_frag.__dict__, "Position:", self.protocol.position)
        dprint("Sent Receiver-Abort to: ", dest)
        dprint("----------------------- SCHC RECEIVER ABORT SEND  -----------------------")

        if enable_statsct:
            Statsct.set_msg_type("SCHC_RECEIVER_ABORT")
            Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))
        self.state = "ABORT"
        self.protocol.scheduler.add_event(0,
                                    self.protocol.layer2.send_packet, args)
        # XXX needs to release all resources.
        self.protocol.session_manager.delete_session(self._session_id)
        return

    def cancel_inactive_timer(self):
        """ cancel_inactive_timer

        // TODO : Redaction (here is frag_recv.py)

        """
        #print ("CANCEL Inactivity Timer", self.event_id_inactive_timer)
        if self.event_id_inactive_timer is None:
            return

        self.protocol.scheduler.cancel_event(self.event_id_inactive_timer)
        self.event_id_inactive_timer = None

    def get_session_type(self):
        return "reassembly"

    def get_state_info(self, **kw):
        return "<reassembly session>"

#---------------------------------------------------------------------------

class ReassemblerNoAck(ReassembleBase):
    """ ReassemblerNoAck class

    // Todo : Redaction

    """
    def receive_frag(self, bbuf, dtag, protocol, core_id=None, device_id=None, iface=None, verbose=True):
        """
        return 
        - None if fragmentation is not finished
        - False if the MIC is wrong
        - bytearray if fragmentation succeed 
        - False if abort is received
        
        """
        #dprint('state: {}, received fragment -> {}, rule-> {}'.format(self.state,
        #                                                             bbuf, self.rule))
        assert (T_FRAG in self.rule)
        
        if (protocol.position == T_POSITION_CORE and self.rule[T_FRAG][T_FRAG_DIRECTION] == T_DIR_DW) or\
            (protocol.position == T_POSITION_DEVICE and self.rule[T_FRAG][T_FRAG_DIRECTION] == T_DIR_UP):
            schc_abort = frag_msg.frag_sender_rx(self.rule, bbuf)
            if schc_abort.abort:
                print ("aborting, removing state")
                protocol.session_manager.delete_session(self._session_id)
                print(protocol.session_manager.session_table)
            return device_id, False
        else:        
            schc_frag = frag_msg.frag_receiver_rx(self.rule, bbuf)
            print("test")
            #dprint("receiver frag received:", schc_frag.__dict__)
            
            if verbose:
                if schc_frag.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] == 0:
                    w_dtag = '-'
                else:
                    w_dtag = schc_frag.dtag

                if schc_frag.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] == 0:
                    w_w = '-'
                else:
                    w_w = schc_frag.win

                all1 = 2**self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN]-1
                if schc_frag.fcn == all1:
                    w_fcn = "All-1"
                elif schc_frag.fcn == 0:
                    w_fcn = "All-0"
                else:
                    w_fcn = schc_frag.fcn

                if protocol.position == T_POSITION_CORE:
                    print ("|--{:3}--> r:{}/{} (noA) DTAG={} W={} FCN={}".format(
                        len(schc_frag.packet_bbuf._content),
                        schc_frag.rule[T_RULEID],
                        schc_frag.rule[T_RULEIDLENGTH],
                        w_dtag,
                        w_w,
                        w_fcn
                        ))
                elif protocol.position == T_POSITION_DEVICE:
                    print ("r:{}/{} (noA) DTAG={} W={} FCN={}|<--{:3}--".format(
                        schc_frag.rule[T_RULEID],
                        schc_frag.rule[T_RULEIDLENGTH],
                        w_dtag,
                        w_w,
                        w_fcn, 
                        len(schc_frag.packet_bbuf._content)                        
                        ))
                else:
                    print ("Unknown position to display fragment.")
            # XXX how to authenticate the message from the peer. without
            # authentication, any nodes can cancel the invactive timer.
            self.cancel_inactive_timer()
            dprint(schc_frag.__class__.__name__)
            #
            if schc_frag.abort == True:
                dprint("----------------------- Sender-Abort ---------------------------")
                # XXX needs to release all resources.
                return device_id, False
            self.tile_list.append(schc_frag.payload)
            #print (self.tile_list)
            #
            if schc_frag.fcn == frag_msg.get_fcn_all_1(self.rule):
                dprint("----------------------- Final Reassembly -----------------------")
                dprint("ALL1 received")
                # MIC calculation
                dprint("tile_list")
                for _ in self.tile_list:
                    dprint(_)
                schc_packet = BitBuffer()
                for i in self.tile_list:
                    schc_packet += i
                #dtrace (binascii.hexlify(schc_packet.get_content()))

                mic_calced = self.get_mic(schc_packet.get_content())
                if schc_frag.mic != mic_calced:
                    dtrace("ERROR: MIC mismatched. packet {} != result {}".format(
                            b2hex(schc_frag.mic), b2hex(mic_calced)))
                    self.state = 'ERROR_MIC_NO_ACK'
                    self.protocol.session_manager.delete_session(self._session_id)
                    return False
                else:
                    dtrace("SUCCESS: MIC matched. packet {} == result {}".format(
                        schc_frag.mic, mic_calced))
                    #return schc_packet.get_content()
                # decompression
                #print("----------------------- Decompression -----------------------")

                dev_id  = None 
                pkt = False
                rule = self.protocol.rule_manager.FindRuleFromSCHCpacket(schc=schc_packet, device=device_id)
                #print("debug: No-ack FindRuleFromSCHCpacket", rule, device_id)
                dev_id, pkt = self.protocol.decompress_only(schc_packet, rule, device_id, iface=iface)
                self.state = 'DONE_NO_ACK'
                self.protocol.session_manager.delete_session(self._session_id)
                #print('@', self.state)
                return dev_id, pkt  # all-1 return the packet reassembled and fragmented or False
            # set inactive timer.
            #self.event_id_inactive_timer = self.protocol.scheduler.add_event(
            #        self.inactive_timer, self.event_inactive, tuple())
            #dprint("---", schc_frag.fcn)
            return device_id, None


    def get_state_info(self, **kw):
        result = {
            "type": "reassembly",
            "mode": "no-ack"
        }
        return result

#---------------------------------------------------------------------------

class ReassemblerAckOnError(ReassembleBase):
    """ ReassemblerAckOnError class
    # In ACK-on-Error, a fragment contains tiles belonging to different window.
    # A type of data structure holding tiles in each window is not suitable.
    # So, here just appends a fragment into the tile_list like No-ACK.
    """

    def receive_frag(self, bbuf, dtag, protocol, core_id=None, device_id=None, iface=None, verbose=False):
        """
        return 
        - None if fragmentation is not finished
        - False if the MIC is wrong
        - True if ACK Success received
        - bytearray if fragmentation succeed 
        """
        self._last_receive_info = []
        print('state: {}, received fragment -> {}, rule-> {}'.format(self.state,
                                                                     bbuf, self.rule))
                                                                     
        assert (T_FRAG in self.rule)
        rule = self.rule

        if protocol.position == T_POSITION_CORE: 
            if rule[T_FRAG][T_FRAG_DIRECTION] == 'DW' : # ACK or Abort
                print('frag_recv.py ACK Received CORE')
                schc_frag = frag_msg.frag_sender_rx(self.rule, bbuf) 
        
        if protocol.position == T_POSITION_DEVICE:
            if rule[T_FRAG][T_FRAG_DIRECTION] == 'UP' : # ACK or Abort
                print('frag_recv.py ACK Received DEVICE')
                schc_frag = frag_msg.frag_sender_rx(self.rule, bbuf) 

        # Regular Fragment        
        schc_frag = frag_msg.frag_receiver_rx(self.rule, bbuf)
        
        print("receiver frag received:", schc_frag.__dict__)
        # XXX how to authenticate the message from the peer. without
        # authentication, any node can cancel the invactive timer.
        self.cancel_inactive_timer()
        if self.state == "ABORT":
            self._last_receive_info = [("state-abort",)]
            self.send_receiver_abort()
            return None # TODO
        #
        # input("")
        if schc_frag.abort == True:
            dprint("----------------------- Sender-Abort ---------------------------")
            # Statsct.set_msg_type("SCHC_SENDER_ABORT")
            # XXX needs to release all resources.
            self._last_receive_info = [("abort",)]
            return None  # TODO
        
        if schc_frag.ack_request == True:
            print("Received ACK-REQ")
            self._last_receive_info = [("ack-req",)]            
            # if self.state != "DONE":
            #     #this can happen when the ALL-1 is not received, so the state is
            #     #not done and the sender is requesting an ACK.
            #     # sending Receiver abort.
            #     schc_frag = frag_msg.frag_receiver_tx_abort(self.rule, self.dtag)
            #     args = (schc_frag.packet.get_content(), self._session_id[0])
            #     dprint("Sent Receiver-Abort.", schc_frag.__dict__)
            #     dprint("----------------------- SCHC RECEIVER ABORT SEND  -----------------------")

            #     if enable_statsct:
            #         Statsct.set_msg_type("SCHC_RECEIVER_ABORT")
            #         #Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))
            #     self.protocol.scheduler.add_event(0,
            #                                 self.protocol.layer2.send_packet, args)
            #     # XXX needs to release all resources.
            #     return
            dprint("XXX need sending ACK back.")
            self.state = 'ACK_REQ'
            # input('')
            self.resend_ack(schc_frag)
            return None

        info = self._last_receive_info
        self.fragment_received = True
        # append the payload to the tile list.
        # padding truncation is done later. see below.
        # nb_tiles = schc_frag.payload.count_added_bits()//self.rule["tileSize"]
        tile_size = self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_TILE]
        nb_tiles, last_tile_size = (
            schc_frag.payload.count_added_bits() // tile_size,
            schc_frag.payload.count_added_bits() % tile_size)
        info.append(("tile-info", {"nb-tiles":nb_tiles, "tile-size":tile_size,
                      "last-tile-size": last_tile_size}))
        dprint("---------nb_tiles: ", nb_tiles, " -----last_tile_size ", last_tile_size)
        tiles = [schc_frag.payload.get_bits_as_buffer(tile_size) for _ in range(nb_tiles)]
        dprint("---------tiles: ", tiles)

        # Note that nb_tiles is the number of tiles which is exact number of the
        # size of the tile.  the tile of which the size is less than the size
        # is not included.
        # The tile that is less than a tile size must be included, so a 1 can be added
        # in the bitmap when there is a tile in the all-1 message

        win = schc_frag.win
        fcn = schc_frag.fcn
        for tile_in_tiles in tiles:
            idx = tiles.index(tile_in_tiles)
            if tile_in_tiles.count_added_bits() % tile_size != 0:
                # tile found that is smaller than a normal tile
                dprint("tile found that is smaller than a normal tile")
                # nb_tiles = 1
            # tile should only be append if it is not in the list
            tile_in_list = False
            for tile in self.tile_list:
                if tile["w-num"] == win:
                    if tile["t-num"] == fcn - idx:
                        dprint("tile is already in tile list")
                        tile_in_list = True
                        info.append(("known-tile", idx, tile))
            if not tile_in_list:
                new_tile = ({
                    "w-num": win,
                    "t-num": fcn - idx,
                    "nb_tiles": 1,
                    "raw_tiles": tile_in_tiles})
                self.tile_list.append(new_tile)
                info.append(("new-tile", idx, new_tile))
                self.tile_list = sort_tile_list(self.tile_list, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])
            if (fcn - idx) == 0:
                win += 1
                fcn = self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN] << 1
                tiles = tiles[(idx + 1):]

        # !IMPORTANT: it's neccesary to change this condition for one more exact which consider the last tile size cases
        if last_tile_size > 8:
            last_tile = schc_frag.payload.get_bits_as_buffer(last_tile_size)
            dprint('---------tile:', last_tile)
            info.append(("last-tile", last_tile))
            tile_in_list = False
            for tile in self.tile_list:
                if tile["w-num"] == win:
                    if tile["t-num"] == 7: # XXX: why 7?
                        dprint("tile is already in tile list")
                        tile_in_list = True
                        info.append(("known-last-tile", None, tile))
            if not tile_in_list:
                new_tile = ({
                    "w-num": win,
                    "t-num": 7,
                    "nb_tiles": 1,
                    "raw_tiles": last_tile})
                self.tile_list.append(new_tile)
                info.append(("new-last-tile", None, new_tile))
                self.tile_list = sort_tile_list(self.tile_list, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])

        # if schc_frag.payload.count_added_bits()%self.rule["tileSize"] != 0:
        #     #tile found that is smaller than a normal tile
        #     dprint("tile found that is smaller than a normal tile")
        #     #nb_tiles = 1
        # #tile should only be append if it is not in the list
        # tile_in_list = False
        # for tile in self.tile_list:
        #     if tile["w-num"] == schc_frag.win:
        #         if tile["t-num"] == schc_frag.fcn:
        #             dprint("tile is already in tile list")
        #             tile_in_list = True
        # if not tile_in_list:
        #     self.tile_list.append({
        #             "w-num": schc_frag.win,
        #             "t-num": schc_frag.fcn,
        #             "nb_tiles": nb_tiles,
        #             "raw_tiles":schc_frag.payload})
        #     self.tile_list = sort_tile_list(self.tile_list, self.rule["FCNSize"])
        for tile in self.tile_list:
            dprint("w-num: {} t-num: {} nb_tiles:{}".format(
                tile['w-num'], tile['t-num'], tile['nb_tiles']))
        dprint("")
        # dprint("raw_tiles:{}".format(tile['raw_tiles']))
        # self.tile_list = sort_tile_list(self.tile_list, self.rule["WSize"])

        # self.tile_list.append({
        #         "w-num": schc_frag.win,
        #         "t-num": schc_frag.fcn,
        #         "nb_tiles": nb_tiles,
        #         "raw_tiles":schc_frag.payload})
        # self.tile_list = sort_tile_list(self.tile_list, self.rule["FCNSize"])
        # self.tile_list = sort_tile_list(self.tile_list, self.rule["WSize"])

        should_send_ack = False
        if self.mic_received is not None:
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            print('MIC calced?')
            if self.mic_received == mic_calced:
                info.append("mic-ok")
                args = self.finish(schc_packet, schc_frag, rule, core_id, device_id, self.protocol.role)
                print('MIC OK', args)
                return args
            else:
                # XXX waiting for the fragments requested by ACK.
                # during MAX_ACK_REQUESTS
                info.append("mic-not-ok")
                dprint("waiting for more fragments.")
                # XXX: do that only when necessary (one per window):
                #should_send_ack = True
        elif schc_frag.fcn == frag_msg.get_fcn_all_1(self.rule):
            # XXX: what if you receive two MICs?
            dprint("----------------------- ALL1 received -----------------------")
            self.all1_received = True
            Statsct.set_msg_type("SCHC_ALL_1")
            self.mic_received = schc_frag.mic
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            dprint("schc_frag.mic: {}, mic_calced: {}".format(schc_frag.mic, mic_calced))
            info.append(("mic-received", schc_frag.mic, mic_calced))
            if schc_frag.mic == mic_calced:
                dprint("SUCCESS: MIC matched. packet {} == result {}".format(
                    schc_frag.mic, mic_calced))
                info.append("mic-ok")
                self.mic_missmatched = False
                args = self.finish(schc_packet, schc_frag, rule, core_id, device_id, self.protocol.role)
                print("frag_recv.py: AckOnError args: ", args)
                return args
            else:
                self.mic_missmatched = True
                self.state = 'ERROR_MIC'
                info.append("mic-not-ok") # XXX: how do you leave ERROR state?
                dprint("----------------------- ERROR -----------------------")
                dprint("ERROR: MIC mismatched. packet {} != result {}".format(
                    b2hex(schc_frag.mic), b2hex(mic_calced)))
                should_send_ack = True

        if should_send_ack: #TODO, change session_id[0] to the corresponding core or device id
                bit_list = find_missing_tiles(self.tile_list,
                                              self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                                              frag_msg.get_fcn_all_1(self.rule))

                assert bit_list is not None
                schc_ack = self.create_ack_schc_ko(schc_frag)
                info.append(("mic-ack", bit_list))
                args = (schc_ack.packet.get_content(), self._session_id[0])
                self.protocol.scheduler.add_event(
                    0, self.protocol.layer2.send_packet, args)
                # XXX need to keep the ack message for the ack request.

        # XXX: maybe set timer in all cases (there are 'return's above)
        # set inactive timer.
        self.event_id_inactive_timer = self.protocol.scheduler.add_event(
            self.inactive_timer, self.event_inactive, tuple())
        dprint("---", schc_frag.fcn)

    def resend_ack(self, schc_frag):
        dprint("resend ack method")
        dprint(schc_frag.__dict__)
        if self.mic_received is not None:
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            dprint("schc_frag.mic: {}, mic_calced: {}".format(self.mic_received,mic_calced))
            if self.mic_received == mic_calced:
                self.state = "DONE"
        if self.state == "DONE":
            # ACK message
            schc_ack = frag_msg.frag_receiver_tx_all1_ack(
                schc_frag.rule,
                schc_frag.dtag,
                schc_frag.win,
                cbit=1)
            dprint("ACK success sent:", schc_ack.__dict__)
            if enable_statsct:
                Statsct.set_msg_type("SCHC_ACK_OK")
            dprint("----------------------- SCHC ACK OK SEND  -----------------------")
        else:
            if self.all1_received:
                dprint("all-1 received, building ACK")
                dprint('send ack before done {},{},{}'.format(self.tile_list,
                            self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN], frag_msg.get_fcn_all_1(self.rule)))
                schc_ack = self.create_ack_schc_ko(schc_frag)
            else:
                #special case when the ALL-1 message is lost: 2 cases:
                #1) the all-1 carries a tile (bit in bitmap)
                #2) the all-1 only carries the MIC (no bit in bitmap)
                if self.fragment_received is False:
                    dprint("no fragments received yet, abort")
                    self.send_receiver_abort()

                    return
                dprint("all-1 not received, building ACK")
                dprint('send ack before done {},{},{}'.format(self.tile_list,
                            self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN], frag_msg.get_fcn_all_1(self.rule)))
                for tile in self.tile_list:
                    dprint("w-num: {} t-num: {} nb_tiles:{}".format(
                        tile['w-num'],tile['t-num'],tile['nb_tiles']))
                    dprint("raw_tiles:{}".format(tile['raw_tiles']))


                bit_list = find_missing_tiles_no_all_1(self.tile_list,
                                                self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                                                frag_msg.get_fcn_all_1(self.rule))
                dprint('send ack before done {}'.format(bit_list))
                assert bit_list is not None
                if len(bit_list) == 0:
                    bit_list = find_missing_tiles_no_all_1(self.tile_list,
                                                self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                                                frag_msg.get_fcn_all_1(self.rule))
                for bl_index in range(len(bit_list)):
                    dprint("missing wn={} bitmap={}".format(bit_list[bl_index][0],
                                                            bit_list[bl_index][1]))
                    # XXX compress bitmap if needed.
                    # ACK failure message
                    schc_ack = frag_msg.frag_receiver_tx_all1_ack(
                            schc_frag.rule,
                            schc_frag.dtag,
                            win=bit_list[bl_index][0],
                            cbit=0,
                            bitmap=bit_list[bl_index][1])
                    if enable_statsct:
                        Statsct.set_msg_type("SCHC_ACK_KO")
                    dprint("----------------------- SCHC ACK KO SEND  -----------------------")

                    dprint("ACK failure sent:", schc_ack.__dict__)
        args = (schc_ack.packet.get_content(), self._session_id[0])
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet, args)
        # XXX need to keep the ack message for the ack request.

    def finish(self, schc_packet, schc_frag, rule, core_id, device_id, role):
        self.state = "DONE"
        dprint('state DONE -> {}'.format(self.state))

        # Define the other end for ACK send:

        if self.protocol.position == T_POSITION_CORE:
            other_end = device_id
        else :
            other_end = core_id

        #input('DONE')
        # decompression
        #self.protocol.process_decompress(schc_packet, self.sender_L2addr, direction="UP")

        comp_rule = self.protocol.rule_manager.FindRuleFromSCHCpacket(schc=schc_packet, device=device_id)
        #dprint("debug, frag_recv.py: AckOnError - finc comp_rule: ", comp_rule)
        dprint("debug, frag_recv.py: AckOnError device_id", device_id)
        dprint("debug, frag_recv.py: AckOnError schc_packet", schc_packet)
        argsfn = self.protocol.decompress_only(schc_packet, comp_rule, device_id)
        print ("frag_recv.py, device_id and decompressed packet: ", argsfn)

        # ACK message
        schc_ack = frag_msg.frag_receiver_tx_all1_ack(
                schc_frag.rule,
                schc_frag.dtag,
                schc_frag.win,
                cbit=1)

        dprint("ACK success sent:", schc_ack.__dict__)
        if enable_statsct:
            Statsct.set_msg_type("SCHC_ACK_OK")

        dprint("----------------------- SCHC ACK OK SEND  -----------------------")
        args = (schc_ack.packet.get_content(), other_end)
        dprint ("++ dbug: frag_recv.py: ACK args", args)
        #time.sleep(1)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet, args)
        # XXX need to keep the ack message for the ack request.
        #the ack is build everytime
        self.schc_ack = schc_ack
        # set inactive timer.
        #self.event_id_inactive_timer = self.protocol.scheduler.add_event(
        #        self.inactive_timer, self.event_inactive, tuple())
        #dprint("DONE, but in case of ACK REQ MUST WAIT ", schc_frag.fcn)

        print ("frag_recv.py, finish (MIC OK), core_id, device_id, : ", core_id, device_id)
        print ("frag_recv.py, finish (MIC OK), args: ", argsfn)
        return argsfn

    def get_mic_from_tiles_received(self):
        # MIC calculation.
        # The truncation of the padding should be done here
        # because the padding of the last tile must be included into the
        # MIC calculation.  However, the fact that the last tile is
        # received can be known after the All-1 fragment is received.
        if not self.tile_list: # All tiles before all-1 not received
            dprint("frag_recv - Unable to compute MIC: not tile received before All-1")
            return [], 0
        dprint("tile_list:")
        for _ in self.tile_list:
            dprint(_)
        schc_packet = BitBuffer()
        if len(self.tile_list) > 1:
            for i in self.tile_list[:-2]:
                # it needs to copy the buffer as it will be reused later.
                tiles = i["raw_tiles"].copy().get_bits_as_buffer(
                    i["nb_tiles"]*self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_TILE])
                schc_packet += tiles
            # check the size of the padding in the All-1 fragment.
            if (self.tile_list[-1]["raw_tiles"].count_added_bits() <
                self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE]):
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
                    i["nb_tiles"]*self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_TILE])
                schc_packet += self.tile_list[-1]["raw_tiles"]
        else:
            # len(self.tile_list) == 1
            # add into the packet as it is.
            schc_packet += self.tile_list[0]["raw_tiles"]
        # get the target of MIC from the BitBuffer.
        dprint("---MIC calculation:")
        mic_calced = self.get_mic(schc_packet.get_content())
        return schc_packet, mic_calced

    def send_receiver_abort(self):

        # Define destination based on possition

        if self.protocol.position == T_POSITION_DEVICE:
            dest = self._session_id[0] # core address
        else:
            dest = self._session_id[1] # device address

        # sending Receiver abort.
        self.state = "ABORT"
        schc_frag = frag_msg.frag_receiver_tx_abort(self.rule, self.dtag)
        args = (schc_frag.packet.get_content(), dest)
        dprint("Sent Receiver-Abort.", schc_frag.__dict__)
        dprint("----------------------- SCHC RECEIVER ABORT SEND  -----------------------")

        if enable_statsct:
            Statsct.set_msg_type("SCHC_RECEIVER_ABORT")
            #Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))
        self.protocol.scheduler.add_event(0,
                                    self.protocol.layer2.send_packet, args)

    def create_ack_schc_ko(self, schc_frag):
        """Create schc_ack packet in case of wrong RCS (C=0)
            return schc_ack packet
        """
        bit_list = find_missing_tiles_mic_ko_yes_all_1(self.tile_list,
                                                self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                                                frag_msg.get_fcn_all_1(self.rule))
        for tile in self.tile_list:
            dprint("w-num: {} t-num: {} nb_tiles:{}".format(
                tile['w-num'],tile['t-num'],tile['nb_tiles']))
            dprint("raw_tiles:{}".format(tile['raw_tiles']))
        dprint('send ack before done {}'.format(bit_list))
        assert bit_list is not None

        if bit_list:
            # Some tiles are actually missing, send ACK for first window with missing tiles
            dprint("missing wn={} bitmap={}".format(bit_list[0][0],
                                                    bit_list[0][1]))
                                                    # XXX compress bitmap if needed.
            # ACK failure message
            schc_ack = frag_msg.frag_receiver_tx_all1_ack(
                    schc_frag.rule,
                    schc_frag.dtag,
                    win=bit_list[0][0],
                    cbit=0,
                    bitmap=bit_list[0][1])
        elif not self.tile_list:
            dprint("No tile received before All-1, sending empty bitmap")
            # ACK failure message
            schc_ack = frag_msg.frag_receiver_tx_all1_ack(
                    schc_frag.rule,
                    schc_frag.dtag,
                    win=0,
                    cbit=0,
                    bitmap=BitBuffer([]))
        else:
            window_list = make_bit_list_mic_ko(self.tile_list,
                                        self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                                        frag_msg.get_fcn_all_1(self.rule))
            last_window = max(window_list.keys())

            # No tiles are detected missing, send ACK for last window
            dprint("No missing tiles, sending last window: wn={} bitmap={}".format(last_window,
                                                    BitBuffer(window_list[last_window])))
                                                    # XXX compress bitmap if needed.
            # ACK failure message
            schc_ack = frag_msg.frag_receiver_tx_all1_ack(
                    schc_frag.rule,
                    schc_frag.dtag,
                    win=last_window,
                    cbit=0,
                    bitmap=BitBuffer(window_list[last_window]))
        if enable_statsct:
            Statsct.set_msg_type("SCHC_ACK_KO")
        dprint("----------------------- SCHC ACK KO SEND  -----------------------")
        dprint("ACK failure sent:", schc_ack.__dict__)
        return schc_ack


    def get_state_info(self, **kw):
        r = self.rule["Fragmentation"]["FRModeProfile"]
        rule_info = {
            "ruleid": self.rule["RuleID"],
            "ruleid-size": self.rule["RuleIDLength"],
            "w-size": r["WSize"],
            "dtag-size": r["dtagSize"],
            "tile-size": r["tileSize"],
            "window-size": r["windowSize"]
        }
        result = {
            "type": "reassembly",
            "mode": "ack-on-error",
            "rule": rule_info,

            "state": self.state,

            "dtag": self.dtag,
            "sender": self.sender_L2addr,
            "tile-list": self.tile_list,
            "mic": self.mic_received,

            "inactive-timer": self.inactive_timer,
            "event-id-inactive": self.event_id_inactive_timer,
            "all1-received": self.all1_received,
            "mic_missmatched": self.mic_missmatched,
            "fragment-received": self.fragment_received,

            "recv-log": self._last_receive_info,
        }
        self._last_receive_info = None
        return result

#---------------------------------------------------------------------------
