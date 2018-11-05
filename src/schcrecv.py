# C.A.

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
        print("---", message.fcn)

#---------------------------------------------------------------------------

# temporary class before merging after hackathon
class SCHCProtocolReceiver(schc.SCHCProtocol):
    def __init__(self, *args, **kwargs):
        schc.SCHCProtocol.__init__(self, *args, **kwargs)
        self.session = ReassemblerAckOnError(self, None) # XXX:hack

    def set_frag_rule(self, rule): #XXX: hack
        schc.SCHCProtocol.set_frag_rule(self, rule)
        self.session.rule = rule

    def find_session(self, device_id):
        return self.session

    def event_receiver_receive_packet(self, device_id, raw_packet):
        #print("schc recv [mac%s] -> SCHC[mac:%s] %s"
        #      % (peer_iid, self.layer2.mac_id, raw_packet))

        session = self.find_session(device_id)
        session.process_packet(raw_packet)

#---------------------------------------------------------------------------

# TODO:


# 2340    smaller than the preceding ones.  WINDOW_SIZE MUST be equal to
# 2341    MAX_WIND_FCN + 1.
