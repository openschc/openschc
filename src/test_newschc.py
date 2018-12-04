#---------------------------------------------------------------------------

# Template for schc simulation
import sys

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import RuleManager

config = "example/fragment-rule-001.json"
#config = "example/fragment-rule-002.json"

#---------------------------------------------------------------------------

with open(config) as fd:
    rule = json.loads(fd.read())

rule_manager = RuleManager()
rule_manager.add(rule)

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
