#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import RuleManager

from stats.statsct import Statsct

#---------------------------------------------------------------------------
# Rules
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
            "WSize":3, # Number of tiles per window
            "FCNSize": 3, # 2^3-2 .. 0 number of sequence de each tile
            "ackBehavior": "afterAll1",
            "tileSize": 392, # size of each tile -> 9 bits or 392 bits
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
            "WSize": 3, # Number of tiles per window
            "FCNSize": 3, # 2^3-2 .. 0 number of sequence de each tile
            "ackBehavior": "afterAll1",
            "tileSize": 392, # size of each tile -> e.g. 9 bits or 392 bits
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

#--------------------------------------------------
# Main configuration

ack_on_error = True
packet_loss_simulation = True
payload_file_simulation = False # Configure the rules, l2_mtu and SF to support the use of a 1400 bytes file

#--------------------------------------------------
# General configuration

l2_mtu = 408 # bits
data_size = 255 # bytes
SF = 12

simul_config = {
    "log": True,
}

#---------------------------------------------------------------------------
# Configuration packets loss
 
if packet_loss_simulation:
    # Configuration with packet loss in noAck and ack-on-error
    loss_rate = 15 # in %
    collision_lambda = 0.1
    background_frag_size = 54
    loss_config = {"mode":"rate", "cycle":loss_rate}
    #loss_config = {"mode":"collision", "G":collision_lambda, "background_frag_size":background_frag_size}
else:
    # Configuration without packet loss in noAck and ack-on-error
    loss_rate = None
    loss_config = None 

#---------------------------------------------------------------------------
# Init packet loss
if loss_config is not None:
    simul_config["loss"] = loss_config
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
Statsct.log("Statsct test")
Statsct.set_packet_size(data_size)
Statsct.set_SF(SF)

#---------------------------------------------------------------------------
# Fragmentation mode 

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

#---------------------------------------------------------------------------
# Configuration of the simulation
Statsct.get_results() 
sim = simul.Simul(simul_config)

devaddr = b"\xaa\xbb\xcc\xdd"
node0 = make_node(sim, rm0, devaddr)                   # SCHC device
node1 = make_node(sim, rm1, devaddr) # SCHC gw
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

#device rule
print("-------------------------------- Device Rule -----------------------------")  
for rule1 in rm0.__dict__:
    print(rm0.__dict__[rule1])
    for info in rm0.__dict__[rule1]:
        print("info -> {}".format(info))
        Statsct.set_device_rule(info)

#gw rule
print("-------------------------------- gw Rule -----------------------------")  
for rule1 in rm1.__dict__:
    print(rm1.__dict__[rule1])
    for info in rm1.__dict__[rule1]:
        print("info -> {}".format(info))
        Statsct.set_gw_rule(info)
#---------------------------------------------------------------------------
# Statistic configuration
       
Statsct.setSourceAddress(node0.id)
Statsct.setDestinationAddress(node1.id)

#--------------------------------------------------
# Payload (information in a file or bytearray of "datasize" bytes)

fileToSend = "testfile_large.txt"

if payload_file_simulation:
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

Statsct.addInfo('real_packet', payload)
Statsct.addInfo('real_packet_size', len(payload))

sim.run()

print('-------------------------------- Simulation ended -----------------------|')
#---------------------------------------------------------------------------
# Results
print("")
print("")
print("-------------------------------- Statistics -----------------------------")         

print('---- Sender Packet list ')
Statsct.print_packet_list(Statsct.sender_packets)
print('')

print('---- Receiver Packet list ')
Statsct.print_packet_list(Statsct.receiver_packets)
print('')

print('---- Packet lost Results (Status -> True = Received, False = Failed) ')
Statsct.print_ordered_packets()
print('')

print('---- Performance metrics')
params = Statsct.calculate_tx_parameters()
print('')

print("---- General result of the simulation {}".format(params))