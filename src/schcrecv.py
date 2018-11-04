# C.A.

from base_import import *  # used for now for differing modules in py/upy

import sys
import schc
import schcmsg

# temporary class before merging after hackathon
class SCHCProtocolReceiver(schc.SCHCProtocol):

    def event_receive_packet(self, other_mac_id, packet):
        print("schc recv [mac%s] -> SCHC[mac:%s] %s"
              % (other_mac_id, self.layer2.mac_id, packet))

        buffer = BitBuffer(packet)
        message = schcmsg.frag_receiver_rx(self.rule, buffer)
        message.finalize(self.rule)
        print(message.__dict__, message.payload.__dict__)
        sys.exit(0)
