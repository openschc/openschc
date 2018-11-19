#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import sys
import schc
import schcmsg

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
