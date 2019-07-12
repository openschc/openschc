#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import RuleManager

from stats.statsct import Statsct

#---------------------------------------------------------------------------
# RULES
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
            "WSize": 7, # Number of tiles per window
            "FCNSize": 3, # 2^3-2 .. 0 number of sequence de each tile
            "ackBehavior": "afterAll1",
            "tileSize": 9, # size of each tile -> 9 bits or 392 bits
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
            "WSize": 7, # Number of tiles per window
            "FCNSize": 3, # 2^3-2 .. 0 number of sequence de each tile
            "ackBehavior": "afterAll1",
            "tileSize": 9, # size of each tile -> e.g. 9 bits or 392 bits
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
# Statistic module
Statsct.initialize()
#---------------------------------------------------------------------------
# Fragmentation mode 

ack_on_error = True
#no-ack
rm0 = RuleManager()
rm0.add_context(rule_context, compress_rule, frag_rule3, frag_rule4)

rm1 = RuleManager()
rm1.add_context(rule_context, compress_rule, frag_rule4, frag_rule3)
#ack-on-error
if ack_on_error:  

    rm0 = RuleManager()
    rm0.add_context(rule_context, compress_rule, frag_rule1, frag_rule2)

    rm1 = RuleManager()
    rm1.add_context(rule_context, compress_rule, frag_rule2, frag_rule1)


#--------------------------------------------------
# General configuration

l2_mtu = 56 # bits
data_size = 14 # bytes

simul_config = {
    "log": True,
}

#---------------------------------------------------------------------------
# Packets loss

loss_rate = 2 # in %
#loss_rate = None 

loss_config = {"mode":"rate", "cycle":loss_rate}
#loss_config = None

if loss_config is not None:
    simul_config["loss"] = loss_config
#---------------------------------------------------------------------------
# Configuration of the simulation

sim = simul.Simul(simul_config)

node0 = make_node(sim, rm0)                   # SCHC device
node1 = make_node(sim, rm1, devaddr=node0.id) # SCHC gw
sim.add_sym_link(node0, node1)
node0.layer2.set_mtu(l2_mtu)
node1.layer2.set_mtu(l2_mtu)

#---------------------------------------------------------------------------
# Information about the devices

print("-------------------------------- SCHC device------------------------")
print("SCHC device L3={} L2={} RM={}".format(node0.layer3.L3addr, node0.id,
                                            rm0.__dict__))
print("-------------------------------- SCHC gw ---------------------------")
print("SCHC gw     L3={} L2={} RM={}".format(node1.layer3.L3addr, node1.id,
                                            rm1.__dict__))
print("-------------------------------- Rules -----------------------------")                                              
print("rules -> {}, {}".format(rm0.__dict__, rm1.__dict__))
print("")

#--------------------------------------------------
# Payload (information in a file or bytearray of "datasize" bytes)

test_file = False
fileToSend = "testfile_large.txt"

if test_file:
    file = open(fileToSend, 'r') # 1400 bytes   
    payload = file.read().encode()    
    print("Payload size:", len(payload),"bytes")
    print("Payload: {}".format(b2hex(payload)))
    print("")
else:                      
    payload = bytearray(range(1, 1+data_size)) # 14 bytes 
    print("Payload size:", len(payload)) 
    print("Payload: {}".format(b2hex(payload)))
    print("")
#---------------------------------------------------------------------------
# Simnulation

node0.protocol.layer3.send_later(1, node1.layer3.L3addr, payload)

sim.run()

#---------------------------------------------------------------------------
