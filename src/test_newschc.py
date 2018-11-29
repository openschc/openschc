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
    "tile-size": 30,
    "mic-algorithm": "crc32",
}

rule = rule_from_dict(rule_as_dict)

# The fragments for the 64 bits payload in this rule expected:
#   |<----- Header ---->|
# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 45 67
# b: 000101 01 00000 110 0000 0001 0000 0010 0000 0011 0000 01 00
# B: 0x15      0x06      0x01      0x02      0x03      0x04

# n: 012345 67 01234 567 01 2345 6701 2345 6701 2345 6701 2345 67
# b: 000101 01 00000 101 00 0000 0101 0000 0110 0000 0111 0000 00
# B: 0x15      0x05      0x01      0x41      0x81      0xc0

# n: 012345 67 01234 567 0123 4567
# b: 000101 01 00000 100 1000 0000
# B: 0x15      0x04      0x80

# n: 012345 67 01234 567 01234567 01234567 01234567 01234567
# b: 000101 01 00000 111 xxxxxxxx xxxxx( MIC )xxxxx xxxxxxxx
# B: 0x15      0x07      ...

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
payload = bytearray(range(1, 8+1))
node0.protocol.layer3.send_later(1, payload)

sim.run()

#---------------------------------------------------------------------------
