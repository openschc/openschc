#---------------------------------------------------------------------------

# Template for schc simulation

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from fakerulemgr import rule_from_dict

#---------------------------------------------------------------------------

#XXX: move
rule_as_dict = {
    "rule-id-size": 6,
    "rule-id": 5,
    "dtag-size": 2,
    "window-size": 5,
    "fcn-size": 3,
    "mode": "ack-on-error",
    #"tile-size": 30,
    "tile-size": 7,
    "mic-algorithm": "crc32",
    "mic-word-size": 8,
    "l2-word-size": 8,
}

rule = rule_from_dict(rule_as_dict)

# The fragments for the 72 bits payload in this rule expected:
#     b'\x01\x02\x03\x04\x05\x06\x07\x08\x09'/72

#
# tile-size is 30
#
#   |<----- Header ---->|
# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 45 67
# b: 000101 01 00000 110 0000 0001 0000 0010 0000 0011 0000 01 00
# B: 0x15      0x06      0x01      0x02      0x03      0x04
# DEBUG: send_frag: b'\x15\x06\x01\x02\x03\x04'/48
#
# n: 012345 67 01234 567 01 2345 6701 2345 6701 2345 6701 2345 67
# b: 000101 01 00000 101 00 0000 0101 0000 0110 0000 0111 0000 00
# B: 0x15      0x05      0x01      0x41      0x81      0xc0
# DEBUG: send_frag: b'\x15\x05\x01\x41\x81\xc0'/48
#
# n: 012345 67 01234 567 0123 4567 0123 4567
# b: 000101 01 00000 100 1000 0000 1001 0000
# B: 0x15      0x04      0x80      0x90
# DEBUG: send_frag: b'\x15\x04\x80\x90'/32
#
# n: 012345 67 01234 567 01234567 01234567 01234567 01234567
# b: 000101 01 00000 111 xxxxxxxx xxxxx( MIC )xxxxx xxxxxxxx
# B: 0x15      0x07      ...
# DEBUG: send_frag: b'\x15\x07\xc5\xf5\xbe\x65'/48

#
# tile-size is 7
#
#
# The fragments for the 64 bits payload in this rule expected:
#   |<----- Header ---->|
# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 45 67
# b: 0001 0101 0000 0110 0000 0001 0000 0010 0000 0011 0000 0100 000 0 0000
# B: 0x15      0x06      0x01      0x02      0x03      0x04      0x00
# DEBUG: send_frag: b'\x15\x06\x01\x02\x03\x04\x00'/56

# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 45 67
# b: 0001 0101 0000 0110 0010 1000 0011 0000 0011 1000 0100 0000 010 00000
# B: 0x15      0x01      0x28      0x30      0x38      0x40      0x40
# DEBUG: send_frag: b'\x15\x01\x28\x30\x38\x40\x40'/56

# n: 012345 67 01234 567 01234567 01234567 01234567 01234567 01 234567
# b: 000101 01 00001 111 xxxxxxxx xxxxx( MIC )xxxxx xxxxxxxx 01 000000
# B: 0x15      0x0f      ...                                 0x40
# DEBUG: send_frag: b'\x15\x0f\xc5\xf5\xbe\x65\x40'/56

#---------------------------------------------------------------------------

def make_node(sim, extra_config={}):
    global rule
    node = simul.SimulSCHCNode(sim, extra_config)
    node.protocol.set_frag_rule(rule)
    # protocol.rulemanager.add_rule(...) ???
    return node

#---------------------------------------------------------------------------

simul_config = {
    "log": True,
#    "loss": { "mode": "cycle", "cycle": 2 }
}
sim = simul.Simul(simul_config)

node0 = make_node(sim)
node1 = make_node(sim)
sim.add_sym_link(node0, node1)

print("mac_id:", node0.id, node1.id)
payload = bytearray(range(1, 9+1))
node0.protocol.layer3.send_later(1, payload)

sim.run()

#---------------------------------------------------------------------------
