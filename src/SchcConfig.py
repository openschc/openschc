"""Schc configuration
This file configure a schc simulation for clients and server
"""
from gen_base_import import *
import net_sim_core
import gen_rulemanager


class SchcConfig:
    def __init__(self, configuration, roleSend=None):
        """
        Initialize Schc Configuration class
        :param configuration: Contain all configuration done in ClientServerSimul.py file
        :param roleSend: Contain the role which will be configured
        """
        self.configuration = configuration
        self.roleSend = roleSend
        self.rule = []
        self.node0 = None
        self.sim = None
        self.rule_comp = None
        self.rule_manager = None
        self.devaddr = None
        self.setAddress()
        self.configRuleManager()

    def setAddress(self):
        if self.configuration['role'] == "client":
            self.devaddr = b"\xaa\xbb\xcc\xdd"
        elif self.configuration['role'] == "server":
            self.devaddr = b"\xaa\xbb\xcc\xee"

    def configRuleManager(self):
        """
        This method set the compression and fragmentation rules in client and server
        """
        self.rule_comp = self.configuration['rule_name_file']
        self.rule_manager = gen_rulemanager.RuleManager()
        self.rule_manager.Add(device=self.devaddr, file=self.rule_comp, compression=self.configuration['mode_with_compression'])

    def configSim(self):
        """
        Method to configure a schc simulation, setting some important configurations and creating a node in the network
        with a sequence of rules associated
        """
        # packets loss and log Configuration
        simul_config = {
            "log": True,
        }

        # Configuration packets loss
        if self.configuration['packet_loss_simulation']:
            # Configuration with packet loss in noAck and ack-on-error
            loss_rate = 15  # in %
            collision_lambda = 0.1
            background_frag_size = 54
            loss_config = {"mode": "rate", "cycle": loss_rate}
            # loss_config = {"mode":"collision", "G":collision_lambda, "background_frag_size":background_frag_size}
        else:
            # Configuration without packet loss in noAck and ack-on-error
            loss_config = None

        if loss_config is not None:
            simul_config["loss"] = loss_config

        # Simul and node instance
        self.sim = net_sim_core.Simul(simul_config)
        self.node0 = self.make_node(self.sim, self.rule_manager, self.devaddr)
        self.node0.layer2.set_mtu(self.configuration['l2_mtu'])
        self.node0.layer2.set_role(self.configuration['role'], self.roleSend)

        print("-------------------------------- SCHC ", self.configuration['role'], " ------------------------")
        print("SCHC device L3={} L2={} RM={}".format(self.node0.layer3.L3addr, self.node0.id,
                                                     self.rule_manager.Print()))

    def make_node(self, sim, rule_manager, devaddr=None, extra_config={}):
        """
        Method to create a node with its rules
        :param sim: Simul instance
        :param rule_manager: Rule manager instance
        :param devaddr: device address
        :param extra_config: extra information to configure node instance
        :return node: node instance
        """
        node = net_sim_core.SimulSCHCNode(sim, extra_config)
        node.protocol.set_rulemanager(rule_manager)
        if devaddr is None:
            devaddr = node.id
        node.layer2.set_devaddr(devaddr)
        return node

    def config_packet(self):
        """
        Method to set a payload to send from client to server
        :return payload: message to send from client
        """
        if self.configuration['payload_name_file'] != "":
            fileToSend = self.configuration['payload_name_file']
            file = open(fileToSend, 'r')  # 1400 bytes
            payload = file.read().encode()
            print("Payload size:", len(payload), "bytes")
            print("Payload: {}".format(b2hex(payload)))
            print("")
        else:
            payload = bytearray(
                b"""`\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x162\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\x82  &Ehello""")
            print("Payload size:", len(payload), "bytes")
            print("Payload: {}".format(b2hex(payload)))
            print("")
        return payload


