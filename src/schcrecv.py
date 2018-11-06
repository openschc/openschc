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

        #fcn = schcmsg.get_all_1(rule)
        #print("ALL1")

        sys.exit(0)



#---------------------------------------------------------------------------

# temporary class before merging after hackathon
class SCHCProtocolReceiver(schc.SCHCProtocol):
    def __init__(self, *args, **kwargs):
        schc.SCHCProtocol.__init__(self, *args, **kwargs)
        self.session = ReassemblerAckOnError(self, None) # XXX:hack

    def set_frag_rule(self, rule): #XXX: hack
        schc.SCHCProtocol.set_frag_rule(self, rule)
        self.session.rule = rule

    def find_session(self, peer_piid):
        return self.session

    def event_receive_packet(self, peer_iid, raw_packet):
        print("schc recv [mac%s] -> SCHC[mac:%s] %s"
              % (peer_iid, self.layer2.mac_id, raw_packet))

        session = self.find_session(peer_iid)
        session.process_packet(raw_packet)

    '''
    def event_receiver_receive_packet(self, peer_iid, raw_packet):
        print("schc recv [mac%s] -> SCHC[mac:%s] %s"
              % (peer_iid, self.layer2.mac_id, raw_packet))

        session = self.find_session(peer_iid)
        session.process_packet(raw_packet)
    '''

#---------------------------------------------------------------------------
