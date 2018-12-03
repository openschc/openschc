#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import sys
import schc
import schcmsg
from schctest import mic_crc32

#---------------------------------------------------------------------------

class ReassemblerNoAck:
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
            mic_calced = mic_crc32.get_mic(schc_packet.get_content()).to_bytes(4, "big")
            if schc_frag_message.mic == mic_calced:
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag_message.mic, mic_calced))
                return
            # decompression
            self.protocol.process_received_packet(self.remote_id, schc_packet)
            return
        print("---", schc_frag_message.fcn)

#---------------------------------------------------------------------------

class ReassemblerAckOnError:
    def __init__(self, protocol, rule, profile=None):
        self.protocol = protocol
        self.rule = rule
        self.profile = profile

        self.pending_tile_list = []

    def process_packet(self, raw_packet):
        buffer = BitBuffer(raw_packet)
        message = schcmsg.frag_receiver_rx(self.rule, buffer)
        message.finalize(self.rule)

        print("parsed message:", message.__dict__, message.payload.__dict__)
        assert message.fcn is not None
        fcn_all_1 = schcmsg.get_fcn_all_1(self.rule)
        if message.fcn == fcn_all_1:
            print("ALL1 received")
            # XXX need to check whether all fragments hsve been received.
            cbit = 1 # XXX
            schc_ack = schcmsg.frag_receiver_tx_all1_ack(message.rule,
                                                         message.dtag,
                                                         message.win,
                                                         cbit=cbit)
            # XXX need finalize ?
            print("ack message:", schc_ack.packet.get_content())
            src_dev_id = self.protocol.layer2.mac_id
            args = (schc_ack.packet.get_content(), src_dev_id, None, None)
            self.protocol.scheduler.add_event(0,
                                              self.protocol.layer2.send_packet,
                                              args)
        print("---", message.fcn)

#---------------------------------------------------------------------------
