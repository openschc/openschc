# ---------------------------------------------------------------------------

from gen_base_import import *  # used for now for differing modules in py/upy
import net_sim_core
from gen_rulemanager import *
from stats.statsct import Statsct
from compr_core import *
from compr_parser import *
from gen_utils import dprint, dpprint

# --------------------------------------------------
# Main configuration
packet_loss_simulation = True

# --------------------------------------------------
# General configuration

l2_mtu = 72  # bits
data_size = 14  # bytes
SF = 12

simul_config = {
    "seed": 2,

    "log": True,
    "enable-print": False,
    "enable-trace": True,

    "record.enable": True,
    "record.directory": "recorded-test",
    "record.format": "pprint" # "pprint" or "json"
}

# ---------------------------------------------------------------------------
# Configuration packets loss

if packet_loss_simulation:
    # Configuration with packet loss in NoAck and ack-on-error
    loss_rate = 15  # in %
    collision_lambda = 0.1
    background_frag_size = 54
    loss_config = {"mode": "rate", "cycle": loss_rate}
    # loss_config = {"mode":"collision", "G":collision_lambda, "background_frag_size":background_frag_size}
else:
    # Configuration without packet loss in NoAck and ack-on-error
    loss_rate = None
    loss_config = None

# ---------------------------------------------------------------------------
# Init packet loss
if loss_config is not None:
    simul_config["loss"] = loss_config

# ---------------------------------------------------------------------------

def make_node(sim, rule_manager, devaddr=None, extra_config={}, role=None):
    extra_config["unique-peer"] = True  # XXX: change for core server
    node = net_sim_core.SimulSCHCNode(sim, extra_config, role)
    node.protocol.set_rulemanager(rule_manager)
    if devaddr is None:
        devaddr = node.id
    node.layer2.set_devaddr(devaddr)
    return node

# ---------------------------------------------------------------------------
# Statistic module
Statsct.initialize()
Statsct.log("Statsct test")
Statsct.set_packet_size(data_size)
Statsct.set_SF(SF)
# ---------------------------------------------------------------------------
devaddr1 = b"\xaa\xbb\xcc\xdd"
devaddr2 = b"\xaa\xbb\xcc\xee"
dprint("---------Rules Device -----------")
rm0 = RuleManager()
# rm0.add_context(rule_context, compress_rule1, frag_rule3, frag_rule4)
rm0.Add(device=devaddr1, file="../examples/configs/rule1.json")
rm0.Print()

dprint("---------Rules gw -----------")
rm1 = RuleManager()
# rm1.add_context(rule_context, compress_rule1, frag_rule4, frag_rule3)
rm1.Add(device=devaddr2, file="../examples/configs/rule1.json")
rm1.Print()

# ---------------------------------------------------------------------------
# Configuration of the simulation
Statsct.get_results()
sim = net_sim_core.Simul(simul_config)

node0 = make_node(sim, rm0, devaddr1, role="device") # SCHC device
node1 = make_node(sim, rm1, devaddr2, role="core-server")   # SCHC gw
sim.add_sym_link(node0, node1)
node0.layer2.set_mtu(l2_mtu)
node1.layer2.set_mtu(l2_mtu)

# ---------------------------------------------------------------------------
# Information about the devices

dprint("-------------------------------- SCHC device------------------------")
dprint("SCHC device L3={} L2={} RM={}".format(node0.layer3.L3addr, node0.id, rm0.__dict__))
dprint("-------------------------------- SCHC gw ---------------------------")
dprint("SCHC gw     L3={} L2={} RM={}".format(node1.layer3.L3addr, node1.id, rm1.__dict__))
dprint("-------------------------------- Rules -----------------------------")
dprint("rules -> {}, {}".format(rm0.__dict__, rm1.__dict__))
dprint("")

# ---------------------------------------------------------------------------
# Statistic configuration

Statsct.setSourceAddress(node0.id)
Statsct.setDestinationAddress(node1.id)

# --------------------------------------------------
# Message

coap = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

# ---------------------------------------------------------------------------
# Simnulation

#node0.protocol.layer3.send_later(1, node1.layer3.L3addr, coap)
node0.protocol.layer3.send_later(1, None, None, coap)
sim.run()

dprint('-------------------------------- Simulation ended -----------------------|')
# ---------------------------------------------------------------------------
# Results
dprint("")
dprint("")
dprint("-------------------------------- Statistics -----------------------------")

dprint('---- Sender Packet list ')
Statsct.print_packet_list(Statsct.sender_packets)
dprint('')

dprint('---- Receiver Packet list ')
Statsct.print_packet_list(Statsct.receiver_packets)
dprint('')

dprint('---- Packet lost Results (Status -> True = Received, False = Failed) ')
Statsct.print_ordered_packets()
dprint('')

dprint('---- Performance metrics')
params = Statsct.calculate_tx_parameters()
dprint('')

dprint("---- General result of the simulation {}".format(params))
