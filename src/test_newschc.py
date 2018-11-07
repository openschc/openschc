# C. A.

# Template for schc

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from schcrecv import SCHCProtocolReceiver
from schcsend import SCHCProtocolSender
from fakeschcsend import rule_from_dict

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

#    "rule-id": 3,
#    "ack-mode": "ack-after-recv-all1"
}

#---------------------------------------------------------------------------

def make_node(sim, extra_config={}):
    node = simul.SimulSCHCNode(sim, extra_config)
    node.protocol.set_frag_rule(rule)
    # protocol.rulemanager.add_rule(...) ???
    return node

#---------------------------------------------------------------------------

rule = rule_from_dict(rule_as_dict)

simul_config = {
    "log": False
}
sim = simul.Simul(simul_config)

node0 = make_node(sim)
node1 = make_node(sim)
sim.add_sym_link(node0, node1)

print("mac_id:", node0.id, node1.id)
#node0.protocol.layer3.send_later(1, bytearray(range(1, 2+1)))
node0.protocol.layer3.send_later(1, bytearray(range(1, 8+1)))

sim.run()
