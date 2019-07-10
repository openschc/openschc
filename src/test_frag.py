#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import RuleManager

from stats.statsct import Statsct

#---------------------------------------------------------------------------

l2_mtu = 56
data_size = 14

rule_context = {
    "devL2Addr": "*",
    "dstIID": "*"
}

compress_rule = {
    "ruleLength": 3,
    "ruleID": 5,
    "compression": {
        "rule_set": []
    }
}

frag_rule1 = {
    "ruleLength": 6,
    "ruleID": 1,
    "profile": { "L2WordSize": 8 },
    "fragmentation": {
        "FRMode": "ackOnError",
        "FRModeProfile": {
            "dtagSize": 2,
            "WSize": 5,
            "FCNSize": 3,
            "ackBehavior": "afterAll1",
            "tileSize": 9,
            "MICAlgorithm": "crc32",
            "MICWordSize": 8
        }
    }
}

frag_rule2 = {
    "ruleLength": 6,
    "ruleID": 2,
    "profile": { "L2WordSize": 8 },
    "fragmentation": {
        "FRMode": "ackOnError",
        "FRModeProfile": {
            "dtagSize": 2,
            "WSize": 5,
            "FCNSize": 3,
            "ackBehavior": "afterAll1",
            "tileSize": 9,
            "MICAlgorithm": "crc32",
            "MICWordSize": 8
        }
    }
}

frag_rule3 = {
    "ruleLength": 6,
    "ruleID": 1,
    "profile": {
        "L2WordSize": 8
    },
    "fragmentation": {
        "FRMode": "noAck",
        "FRModeProfile": {
            "dtagSize": 2,
            "FCNSize": 3,
            "MICAlgorithm": "crc32",
            "MICWordSize": 8
        }
    }
}

frag_rule4 = {
    "ruleLength": 6,
    "ruleID": 2,
    "profile": {
        "L2WordSize": 8
    },
    "fragmentation": {
        "FRMode": "noAck",
        "FRModeProfile": {
            "dtagSize": 2,
            "FCNSize": 3,
            "MICAlgorithm": "crc32",
            "MICWordSize": 8
        }
    }
}


#---------------------------------------------------------------------------

def make_node(sim, rule_manager, devaddr=None, extra_config={}):
    node = simul.SimulSCHCNode(sim, extra_config)
    node.protocol.set_rulemanager(rule_manager)
    if devaddr is None:
        devaddr = node.id
    node.layer2.set_devaddr(devaddr)
    return node

#---------------------------------------------------------------------------
Statsct.initialize()

rm0 = RuleManager()
rm0.add_context(rule_context, compress_rule, frag_rule3, frag_rule4)

rm1 = RuleManager()
rm1.add_context(rule_context, compress_rule, frag_rule4, frag_rule3)

#--------------------------------------------------

simul_config = {
    "log": True,
}
sim = simul.Simul(simul_config)

node0 = make_node(sim, rm0)                   # SCHC device
node1 = make_node(sim, rm1, devaddr=node0.id) # SCHC gw
sim.add_sym_link(node0, node1)
node0.layer2.set_mtu(l2_mtu)
node1.layer2.set_mtu(l2_mtu)

print("SCHC device L3={} L2={} RM={}".format(node0.layer3.L3addr, node0.id,
                                             rm0.__dict__))
print("SCHC gw     L3={} L2={} RM={}".format(node1.layer3.L3addr, node1.id,
                                             rm1.__dict__))

#--------------------------------------------------

payload = bytearray(range(1, 1+data_size))
node0.protocol.layer3.send_later(1, node1.layer3.L3addr, payload)

sim.run()

#---------------------------------------------------------------------------
