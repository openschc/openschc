#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import *

from stats.statsct import Statsct

from schccomp import *
from comp_parser import *

import json
import pprint
import binascii
#---------------------------------------------------------------------------
rule_context = {
    "devL2Addr": "*",
    "dstIID": "*"
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
devaddr1 = b"\xaa\xbb\xcc\xdd"
devaddr2 = b"\xaa\xbb\xcc\xee"
print("---------Rules Device -----------")
rm0 = RuleManager()
#rm0.add_context(rule_context, compress_rule1, frag_rule3, frag_rule4)
rm0.Add(device = devaddr1, file="example/comp-rule-100.json")
rm0.Print()

print("---------Rules gw -----------")
rm1 = RuleManager()
#rm1.add_context(rule_context, compress_rule1, frag_rule4, frag_rule3)
rm1.Add(device = devaddr2, file="example/comp-rule-100.json")
rm1.Print()

#--------------------------------------------------
# General configuration

l2_mtu = 404 # bits
data_size = 14 # bytes

simul_config = {
    "log": True,
}

#---------------------------------------------------------------------------
# Packets loss

#loss_rate = 2 # in %
loss_rate = None 

#loss_config = {"mode":"rate", "cycle":loss_rate}
loss_config = None

if loss_config is not None:
    simul_config["loss"] = loss_config

#---------------------------------------------------------------------------
# Configuration of the simulation

sim = simul.Simul(simul_config)

node0 = make_node(sim, rm0, devaddr1)                   # SCHC device
node1 = make_node(sim, rm1, devaddr2) # SCHC gw
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
# Message

coap = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

#---------------------------------------------------------------------------
# Simnulation

node0.protocol.layer3.send_later(1, node1.layer3.L3addr, coap)

sim.run()

#---------------------------------------------------------------------------

