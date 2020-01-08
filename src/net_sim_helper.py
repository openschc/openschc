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

DEFAULT_RADIO_CONFIG = {
    "l2_mtu": 72, # bits
    "data_size": 14, # bytes
    "SF": 12,
}

DEFAULT_LOSS_CONFIG = {
    "mode": "rate",
    "cycle": 15, # packet loss rate in %
}

DEFAULT_COLLISION_LOSS_CONFIG = {
    "mode": "collision",
    "G": 0.1, # collision_lambda
    "background_frag_size": 54,
}

DEFAULT_SIMUL_CONFIG = {
    "seed": 2,

    "log": True,
    "enable-print": True,
    "enable-trace": True,

    "record.enable": True,
    "record.directory": "recorded-test",
    "record.format": "pprint", # "pprint" or "json"
    "record.quiet": False,

    "radio": DEFAULT_RADIO_CONFIG,
}

# ---------------------------------------------------------------------------

# XXX: this should be removed
DEFAULT_MAC_ADDRESS_TABLE = {
    "device": b"\xaa\xbb\xcc\xdd",
    "gateway":  b"\xaa\xbb\xcc\xee"
}

# ---------------------------------------------------------------------------

class SimulHelper:
    def __init__(self):
        self.simul = None
        self.simul_config = None
        self.device_rule_manager = None
        self.gateway_rule_manager = None

    def create_gateway(self, rules):
        dprint("---------Rules gw -----------")
        rm1 = RuleManager()
        devaddr2 = DEFAULT_MAC_ADDRESS_TABLE["gateway"]
        rm1.Add(device=devaddr2, dev_info=rules)
        rm1.Print()
        self.gateway_rule_manager = rm1

    def create_device(self, rules):
        dprint("---------Rules Device -----------")
        rm0 = RuleManager()
        devaddr1 = DEFAULT_MAC_ADDRESS_TABLE["device"]
        rm0.Add(device=devaddr1, dev_info=rules)
        rm0.Print()
        self.device_rule_manager = rm0

    def make_device_send_data(self, clock, packet=None, packet_size=None):
        self.node0.protocol.layer3.send_later(
            clock, self.node1.layer3.L3addr, packet)

    def set_config(self, simul_config, loss_config=None):
        simul_config = simul_config.copy()
        if loss_config is not None:
            simul_config["loss"] = loss_config
        self.simul_config = simul_config
        # --------------------------------
        # Configuration of the simulation
        self.init_stat()
        Statsct.get_results()
        sim = net_sim_core.Simul(simul_config)
        self.sim = sim

        devaddr1 = DEFAULT_MAC_ADDRESS_TABLE["device"]
        devaddr2 = DEFAULT_MAC_ADDRESS_TABLE["gateway"]
        l2_mtu = simul_config["radio"]["l2_mtu"]

        rm0 = self.device_rule_manager
        rm1 = self.gateway_rule_manager
        node0 = self._make_schc_node(sim, rm0, devaddr1)  # SCHC device
        node1 = self._make_schc_node(sim, rm1, devaddr2)  # SCHC gw
        sim.add_sym_link(node0, node1)
        node0.layer2.set_mtu(l2_mtu)
        node1.layer2.set_mtu(l2_mtu)
        self.node0 = node0
        self.node1 = node1

        self.update_stat(node1, rm0, rm1, node0)

    def create_simul(self):
        if self.simul_config is None:
            self.set_config(DEFAULT_SIMUL_CONFIG.copy())

    def run_simul(self):
        self.sim.run()
        self.show_stat()

    def _make_schc_node(self, sim, rule_manager, devaddr=None, extra_config={}):
        node = net_sim_core.SimulSCHCNode(sim, extra_config)
        node.protocol.set_rulemanager(rule_manager)
        if devaddr is None:
            devaddr = node.id
        node.layer2.set_devaddr(devaddr)
        return node

    # ------------------------------

    def init_stat(self):
        # Statistic module
        radio_config = self.simul_config["radio"]
        Statsct.initialize(init_time=0)
        Statsct.log("Statsct test")
        Statsct.set_packet_size(radio_config["data_size"])
        Statsct.set_SF(radio_config["SF"])

    def update_stat(self, node1, rm0, rm1, node0):
        # ---------------------------------
        # Information about the devices
        dprint(32*"-"+" SCHC device------------------------")
        dprint("SCHC device L3={} L2={} RM={}".format(
            node0.layer3.L3addr, node0.id, rm0.__dict__))
        dprint(32*"-"+" SCHC gw ---------------------------")
        dprint("SCHC gw     L3={} L2={} RM={}".format(
            node1.layer3.L3addr, node1.id, rm1.__dict__))
        dprint(32*"-"+" Rules -----------------------------")
        dprint("rules -> {}, {}".format(rm0.__dict__, rm1.__dict__))
        dprint("")
        # ----------------------------------
        # Statistic configuration
        Statsct.setSourceAddress(node0.id)
        Statsct.setDestinationAddress(node1.id)

    def show_stat(self):
        dprint(32*'-'+' Simulation ended -----------------------|')
        # Results
        dprint("")
        dprint("")
        dprint(32*"-"+" Statistics -----------------------------")

        dprint('---- Sender Packet list ')
        Statsct.print_packet_list(Statsct.sender_packets)
        dprint('')

        dprint('---- Receiver Packet list ')
        Statsct.print_packet_list(Statsct.receiver_packets)
        dprint('')

        dprint('---- Packet lost Results '
               +'(Status -> True = Received, False = Failed) ')
        Statsct.print_ordered_packets()
        dprint('')

        dprint('---- Performance metrics')
        params = Statsct.calculate_tx_parameters()
        dprint('')

        dprint("---- General result of the simulation {}".format(params))

# ---------------------------------------------------------------------------
