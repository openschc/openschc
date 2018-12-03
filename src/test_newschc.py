#---------------------------------------------------------------------------

# Template for schc simulation
import sys

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import RuleManager

with open("example/fragment-rule-002.json") as fd:
    rule = json.loads(fd.read())

#---------------------------------------------------------------------------

rule_manager = RuleManager()
rule_manager.add(rule)

# The fragments for the 72 bits payload in this rule expected:
#     b'\x01\x02\x03\x04\x05\x06\x07\x08\x09'/72

#
# tile-size is 30
#
#   |<----- Header ---->|
# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 4567
# b: 000101 01 00000 110 0000 0001 0000 0010 0000 0011 0000 0100
# B: 0x15      0x06      0x01      0x02      0x03      0x04
# DEBUG: send_frag: b'\x15\x06\x01\x02\x03\x04'/48
#
# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 4567
# b: 000101 01 00000 101 0000 0001 0100 0001 1000 0001 1100 0000
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
#   |<----- Header ---->|
# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 4567 0123 4567
# b: 000101 01 00000 110 0000 0001 0000 0010 0000 0011 0000 0100 0000 0000
# B: 0x15      0x06      0x01      0x02      0x03      0x04      0x00
# DEBUG: send_frag: b'\x15\x06\x01\x02\x03\x04\x00'/56

# n: 012345 67 01234 567 0123 4567 0123 4567 0123 4567 0123 4567 0123 4567
# b: 000101 01 00000 110 0010 1000 0011 0000 0011 1000 0100 0000 0100 0000
# B: 0x15      0x01      0x28      0x30      0x38      0x40      0x40
# DEBUG: send_frag: b'\x15\x01\x28\x30\x38\x40\x40'/56

# n: 012345 67 01234 567 01234567 01234567 01234567 01234567 01 234567
# b: 000101 01 00001 111 xxxxxxxx xxxxx( MIC )xxxxx xxxxxxxx 01 000000
# B: 0x15      0x0f      ...                                 0x40
# DEBUG: send_frag: b'\x15\x0f\xc5\xf5\xbe\x65\x40'/56

#---------------------------------------------------------------------------

def make_node(sim, rule_manager, extra_config={}):
    node = simul.SimulSCHCNode(sim, extra_config)
    node.protocol.set_rulemanager(rule_manager)
    return node

#---------------------------------------------------------------------------

simul_config = {
    "log": True,
#    "loss": { "mode": "cycle", "cycle": 2 }
}
sim = simul.Simul(simul_config)

node0 = make_node(sim, rule_manager)
node1 = make_node(sim, rule_manager)
sim.add_sym_link(node0, node1)

print("mac_id:", node0.id, node1.id)
payload = bytearray(range(1, 9+1))
node0.protocol.layer3.send_later(1, node1.id, payload)

sim.run()

#---------------------------------------------------------------------------
