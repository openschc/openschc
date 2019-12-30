"""
.. module:: simul
   :platform: Python

A set of helper function to create a simulation more easily.
XXX: this is moved from test_simul.py, with the intent of cleaning later
"""

from gen_base_import import *  # used for now for differing modules in py/upy
import net_sim_core
from gen_rulemanager import *
from stats.statsct import Statsct
from compr_core import *
from compr_parser import *
from gen_utils import dprint, dpprint

# ---------------------------------------------------------------------------
# Default config

# --------------------------------------------------
# Main configuration
packet_loss_simulation = False

# --------------------------------------------------
# General configuration

l2_mtu = 72  # bits
data_size = 14  # bytes
SF = 12

default_simul_config = {
    "seed": 2,

    "log": True,
    "enable-print": True,
    "enable-trace": True,

    "record.enable": True,
    "record.directory": "recorded-test",
    "record.format": "pprint", # "pprint" or "json"
    "record.quiet": False,
}

# --------------------------------------------------
# Configuration packets loss

if packet_loss_simulation:
    # Configuration with packet loss in noAck and ack-on-error
    loss_rate = 15  # in %
    collision_lambda = 0.1
    background_frag_size = 54
    loss_config = {"mode": "rate", "cycle": loss_rate}
    # loss_config = {"mode":"collision", "G":collision_lambda, "background_frag_size":background_frag_size}
else:
    # Configuration without packet loss in noAck and ack-on-error
    loss_rate = None
    loss_config = None

# ---------------------------------------------------------------------------
# Init packet loss
if loss_config is not None:
    default_simul_config["loss"] = loss_config

devaddr1 = b"\xaa\xbb\xcc\xdd"
devaddr2 = b"\xaa\xbb\xcc\xee"

# ---------------------------------------------------------------------------

def make_node(sim, rule_manager, devaddr=None, extra_config={}):
    node = net_sim_core.SimulSCHCNode(sim, extra_config)
    node.protocol.set_rulemanager(rule_manager)
    if devaddr is None:
        devaddr = node.id
    node.layer2.set_devaddr(devaddr)
    return node

#  ^^^ XXX: All the above needs refactoring
# ---------------------------------------------------------------------------

class SimulHelper:
    def __init__(self):
        self.simul = None
        self.simul_config = None
        self.device_rule_manager = None
        self.gateway_rule_manager = None

    def pre_init(self):
        # Statistic module
        Statsct.initialize()
        Statsct.log("Statsct test")
        Statsct.set_packet_size(data_size)
        Statsct.set_SF(SF)

    def post_run(self):
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

    def create_gateway(self, rules):
        dprint("---------Rules gw -----------")
        rm1 = RuleManager()
        rm1.Add(device=devaddr2, dev_info=rules)
        rm1.Print()
        self.gateway_rule_manager = rm1

    def create_device(self, rules):
        dprint("---------Rules Device -----------")
        rm0 = RuleManager()
        rm0.Add(device=devaddr1, dev_info=rules)
        rm0.Print()
        self.device_rule_manager = rm0

    def make_device_send_data(self, clock, packet):
        self.node0.protocol.layer3.send_later(clock, self.node1.layer3.L3addr, packet)

    def set_config(self, simul_config):
        self.simul_config = simul_config
        # --------------------------------
        # Configuration of the simulation
        Statsct.get_results()
        sim = net_sim_core.Simul(simul_config)
        self.sim = sim

        rm0 = self.device_rule_manager
        rm1 = self.gateway_rule_manager
        node0 = make_node(sim, rm0, devaddr1)  # SCHC device
        node1 = make_node(sim, rm1, devaddr2)  # SCHC gw
        sim.add_sym_link(node0, node1)
        node0.layer2.set_mtu(l2_mtu)
        node1.layer2.set_mtu(l2_mtu)
        self.node0 = node0
        self.node1 = node1

        # ---------------------------------
        # Information about the devices

        dprint("-------------------------------- SCHC device------------------------")
        dprint("SCHC device L3={} L2={} RM={}".format(node0.layer3.L3addr, node0.id, rm0.__dict__))
        dprint("-------------------------------- SCHC gw ---------------------------")
        dprint("SCHC gw     L3={} L2={} RM={}".format(node1.layer3.L3addr, node1.id, rm1.__dict__))
        dprint("-------------------------------- Rules -----------------------------")
        dprint("rules -> {}, {}".format(rm0.__dict__, rm1.__dict__))
        dprint("")

        # ----------------------------------
        # Statistic configuration

        Statsct.setSourceAddress(node0.id)
        Statsct.setDestinationAddress(node1.id)

    def create_simul(self):
        self.pre_init()
        if self.simul_config is None:
            self.set_config(default_simul_config.copy())

    def run_simul(self):
        self.sim.run()
        self.post_run()

# ---------------------------------------------------------------------------
