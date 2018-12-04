#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import sys
import schc
import schcmsg
from schctest import mic_crc32

#---------------------------------------------------------------------------

class ReassembleBase:

    def __init__(self, protocol, rule, remote_id, profile=None):
        self.protocol = protocol
        self.rule = rule
        self.remote_id = remote_id
        self.profile = profile
        self.tile_list = []

    def get_mic(self, extra_bits=0):
        mic_target = self.packet_bbuf.get_content()
        mic_target += b"\x00" * (roundup(
                extra_bits, self.rule["MICWordSize"])//self.rule["MICWordSize"])
        mic = mic_crc32.get_mic(mic_target)
        return mic.to_bytes(4, "big")

#---------------------------------------------------------------------------

class ReassemblerNoAck(ReassembleBase):

    def process_packet(self, bbuf, dtag):
        # XXX context should be passed from the lower layer.
        # XXX and pass the context to the parser.
        schc_frag_message = schcmsg.frag_receiver_rx(self.rule, bbuf)
        schc_frag_message.finalize(self.rule)

        print("parsed message:", schc_frag_message.__dict__,
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

    def process_packet(self, bbuf, dtag):
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        schc_frag.finalize(self.rule)

        print("parsed message:", schc_frag.__dict__,
              schc_frag.payload.__dict__)
        assert schc_frag.fcn is not None
        # truncate the tail bits of the tile.
        significant_bits_size = ((
            schc_frag.payload.count_added_bits()//self.rule["tileSize"])*
            self.rule["tileSize"])
        # append the payload to the tile list.
        self.tile_list.append(schc_frag.payload.get_bits_as_buffer(
                significant_bits_size))
        fcn_all_1 = schcmsg.get_fcn_all_1(self.rule)
        if schc_frag.fcn == fcn_all_1:
            print("ALL1 received")
            print("tile_list", self.tile_list)
            # XXX need to check whether all fragments hsve been received.
            # MIC calculation
            schc_packet = BitBuffer()
            for i in self.tile_list:
                schc_packet += i
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
            # XXX need finalize ?
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
