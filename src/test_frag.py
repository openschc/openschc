#---------------------------------------------------------------------------

import random
random.seed(1)

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
    "RuleIDLength": 3,
    "RuleID": 5,
    "Compression": {
        "rule_set": []
    }
}

frag_rule1 = {
    "RuleIDLength": 6,
    "RuleID": 1,
    "profile": { "L2WordSize": 8 },
    "Fragmentation": {
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
    "RuleIDLength": 6,
    "RuleID": 2,
    "profile": { "L2WordSize": 8 },
    "Fragmentation": {
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
    "RuleIDLength": 6,
    "RuleID": 1,
    "profile": {
        "L2WordSize": 8
    },
    "Fragmentation": {
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
    "RuleIDLength": 6,
    "RuleID": 2,
    "profile": {
        "L2WordSize": 8
    },
    "Fragmentation": {
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
#packet_loss_simulation = True
packet_loss_simulation = False
payload_file_simulation = False # Configure the rules, l2_mtu and SF to support the use of a 1400 bytes file
payload_coap = True

#--------------------------------------------------
# General configuration

l2_mtu = 408 # bits
data_size = 255 # bytes
SF = 12

simul_config = {
    "log": True,
}
if not payload_coap:
    simul_config.update({"node-config": { "debug-fragment": True }})
    print("Please keep in mind compresion will not be done.")

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

compress_rule = None

#no-ack
rm0 = RuleManager()
rm0.add_context(rule_context, compress_rule, frag_rule3, frag_rule4)

rm1 = RuleManager()
rm1.add_context(rule_context, compress_rule, frag_rule4, frag_rule3)
<<<<<<< HEAD
#ack-on-error
if ack_on_error:  
    
    rm0 = RuleManager()
    rm0.add_context(rule_context, compress_rule, frag_rule1, frag_rule2)
=======
>>>>>>> 8c5bbc0... Petite correction Mode NoACK

    rm1 = RuleManager()
    rm1.add_context(rule_context, compress_rule, frag_rule2, frag_rule1)

rm0.Add(file="example/comp-rule-100.json")
rm1.Add(file="example/comp-rule-100.json")

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
    if rm0.__dict__[rule1] is None:
        continue
    print(rm0.__dict__[rule1])
    for info in rm0.__dict__[rule1]:
        print("info -> {}".format(info))
        Statsct.set_device_rule(info)

#gw rule
print("-------------------------------- gw Rule -----------------------------")  
for rule1 in rm1.__dict__:
    if rm0.__dict__[rule1] is None:
        continue
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

if payload_coap:
    #payload = bytes.fromhex("60123456001e111efe800000000000000000000000000001fe80000000000000000000000000000216321633001e0000410200010ab3666f6f0362617206414243443d3d466b3d65746830ff8401822020264568656c6c6f")
    from binascii import a2b_hex
    payload = a2b_hex("60123456001e111efe800000000000000000000000000001fe80000000000000000000000000000216321633001e0000410200010ab3666f6f0362617206414243443d3d466b3d65746830ff8401822020264568656c6c6f")

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
