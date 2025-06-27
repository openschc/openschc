"""
.. module:: simul
   :platform: Python

A set of builder/helper functions to create a simulation more easily.
XXX: one iteration if cleaning is still needed.
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

class SimulBuilder:
    def __init__(self):
        self.simul = None
        self.simul_config = None
        self.device_rule_manager = None
        self.core_rule_manager = None

    def create_core(self, rules):
        dprint("---------Rules gw -----------")
        rm1 = RuleManager()
        devaddr2 = DEFAULT_MAC_ADDRESS_TABLE["gateway"]
        rm1.Add(device=devaddr2, dev_info=rules)
        rm1.Print()
        self.core_rule_manager = rm1
        self.core_node = self._make_schc_node(self.sim, rm1, devaddr2, role="core-server")
        return self.core_node

    def create_device(self, rules):
        dprint("---------Rules Device -----------")
        rm0 = RuleManager()
        devaddr1 = DEFAULT_MAC_ADDRESS_TABLE["device"]
        rm0.Add(device=devaddr1, dev_info=rules)
        rm0.Print()
        self.device_rule_manager = rm0
        self.device_node = self._make_schc_node(self.sim, rm0, devaddr1, role="device")
        return self.device_node

    def make_device_send_data(self, clock, packet=None, packet_size=None):
        self.device_node.protocol.layer3.send_later(
            clock, None, None, packet)
        # XXX: remove:
        #self.device_node.protocol.layer3.send_later(
        #    clock, self.core_node.layer3.L3addr, packet)

    def set_config(self, simul_config, loss_config=None):
        simul_config = simul_config.copy()
        if loss_config is not None:
            simul_config["loss"] = loss_config
        self.simul_config = simul_config

    def _prepare_run(self):
        devaddr1 = DEFAULT_MAC_ADDRESS_TABLE["device"]
        devaddr2 = DEFAULT_MAC_ADDRESS_TABLE["gateway"]
        l2_mtu = self.simul_config["radio"]["l2_mtu"]

        self.sim.add_sym_link(self.core_node, self.device_node)
        self.core_node.layer2.set_mtu(l2_mtu)
        self.device_node.layer2.set_mtu(l2_mtu)

        self.update_stat(self.core_node, self.device_rule_manager,
                         self.core_rule_manager, self.device_node)

    def create_simul(self):
        if self.simul_config is None:
            self.set_config(DEFAULT_SIMUL_CONFIG.copy())
        self.init_stat()
        Statsct.get_results()
        sim = net_sim_core.Simul(self.simul_config)
        self.sim = sim

    def run_simul(self):
        self._prepare_run()
        self.sim.run()
        self.show_stat()

    def _make_schc_node(self, sim, rule_manager, devaddr=None, extra_config={},
                        role="undefined"):
        extra_config["unique-peer"] = True # XXX: change for core server
        node = net_sim_core.SimulSCHCNode(sim, extra_config, role)
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
