#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import sys
import schc
import schcmsg
from schctest import mic_crc32

#---------------------------------------------------------------------------

class ReassembleBase:

    def __init__(self, protocol, rule, dtag, remote_id, profile=None):
        self.protocol = protocol
        self.rule = rule    # XXX must be immutable.
        self.dtag = dtag    # XXX must be immutable.
        self.remote_id = remote_id
        self.profile = profile
        self.tile_list = []

    def get_mic(self, extra_bits=0):
        mic_target = self.packet_bbuf.get_content()
        mic_target += b"\x00" * (roundup(
                extra_bits, self.rule["MICWordSize"])//self.rule["MICWordSize"])
        mic = mic_crc32.get_mic(mic_target)
        return mic.to_bytes(4, "big")

    def cancel_timer(self):
        # XXX cancel timer registered.
        pass

#---------------------------------------------------------------------------

class ReassemblerNoAck(ReassembleBase):

    def receive_frag(self, bbuf, dtag):
        # XXX context should be passed from the lower layer.
        # XXX and pass the context to the parser.
        schc_frag_message = schcmsg.frag_receiver_rx(self.rule, bbuf)

        print("receive_frag:", schc_frag_message.__dict__,
              schc_frag_message.payload.__dict__)
        assert schc_frag_message.fcn is not None
        self.tile_list.append(schc_frag_message.payload)
        fcn_all_1 = schcmsg.get_fcn_all_1(self.rule)
        if schc_frag_message.fcn == fcn_all_1:
            print("ALL1 received")
            # MIC calculation
            schc_packet = BitBuffer()
            for i in self.tile_list:
                schc_packet += i
            mic_target = schc_packet.get_content()
            mic_calced = mic_crc32.get_mic(mic_target)
            print("Recv MIC {}, base = {}".format(mic_calced, mic_target))
            if schc_frag_message.mic != mic_calced:
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag_message.mic, mic_calced))
                return
            # decompression
            self.protocol.process_received_packet(self.remote_id, schc_packet)
            return
        print("---", schc_frag_message.fcn)

#---------------------------------------------------------------------------

class ReassemblerAckOnError(ReassembleBase):

    def receive_frag(self, bbuf, dtag):
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        print("receive_frag:", schc_frag.__dict__,
              schc_frag.payload.__dict__)
        assert schc_frag.fcn is not None
        # append the payload to the tile list.
        # padding truncation is done later. see below.
        nb_tiles = schc_frag.payload.count_added_bits()//self.rule["tileSize"]
        self.tile_list.append({
                "w-num": schc_frag.win,
                "t-num": schc_frag.fcn,
                "nb_tiles": nb_tiles,
                "raw_tiles":schc_frag.payload}) # XXX needs to copy() ?
        if schc_frag.fcn == schcmsg.get_fcn_all_1(self.rule):
            # XXX need to check whether all fragments hsve been received.
            print("ALL1 received")
            print("tile_list", self.tile_list)
            # MIC calculation.
            # The truncation of the padding should be done here
            # because the padding of the last tile must be included into the MIC
            # calculation.  However, the fact that the last tile is received
            # can be known after the All-1 fragment is received.
            schc_packet = BitBuffer()
            for i in self.tile_list[:-2]:
                tiles = i["raw_tiles"].get_bits_as_buffer(
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
                schc_packet += i["raw_tiles"].get_bits_as_buffer(
                    i["nb_tiles"]*self.rule["tileSize"])
                schc_packet += self.tile_list[-1]["raw_tiles"]
            # get the target of MIC from the BitBuffer.
            mic_target = schc_packet.get_content()
            mic_calced = mic_crc32.get_mic(mic_target)
            print("Recv MIC {}, base = {}".format(mic_calced, mic_target))
            if schc_frag.mic != mic_calced:
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag.mic, mic_calced))
                return
            # decompression
            self.protocol.process_received_packet(self.remote_id, schc_packet)
            # ACK message
            schc_ack = schcmsg.frag_receiver_tx_all1_ack(
                    schc_frag.rule,
                    schc_frag.dtag,
                    schc_frag.win,
                    cbit=1)
            print("ack message:", schc_ack.packet.get_content())
            src_dev_id = self.protocol.layer2.mac_id
            args = (schc_ack.packet.get_content(), src_dev_id, None, None)
            self.protocol.scheduler.add_event(0,
                                              self.protocol.layer2.send_packet,
                                              args)
            # XXX need to keep the ack message for the ack request.
            return
        print("---", schc_frag.fcn)

#---------------------------------------------------------------------------
