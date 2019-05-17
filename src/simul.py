"""
.. module:: simul
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from base_import import *
from simsched import SimulScheduler as Scheduler
from simlayer2 import SimulLayer2
from cond_true import ConditionalTrue

import schc

from stats.statsct import Statsct

Link = namedtuple("Link", "from_id to_id delay")

SimulNode = SimulLayer2

class SimulLayer3:
    __v6addr_prefix = "2001:0db8:85a3:0000:0000:0000:0000:000"
    __v6addr_base = 0

    def __init__(self, sim):
        self.sim = sim
        self.protocol = None
        self.L3addr = SimulLayer3.__get_unique_addr()

    def send_later(self, rel_time, dst_L3addr, raw_packet):
        self._log("send-later Devaddr={} Packet={}".format(
                dst_L3addr, b2hex(raw_packet)))
        self.sim.scheduler.add_event(
            rel_time, self.protocol.schc_send,
            (dst_L3addr, raw_packet,))

    # XXX need to confirm whether this should be here or not.
    def recv_packet(self, dev_L2addr, raw_packet):
        """ receive a packet from L2 and process it. """
        self._log("recv-from-L2 Devaddr={} Packet={}".format(
                dev_L2addr, b2hex(raw_packet.get_content())))
        # XXX do more work

    def _set_protocol(self, protocol): # called by SCHCProtocol
        self.protocol = protocol

    def _log(self, message):
        self.protocol.system.log("L3", message)

    @classmethod
    def __get_unique_addr(cls):
        result = "{}{}".format(cls.__v6addr_prefix, cls.__v6addr_base)
        cls.__v6addr_base += 1
        return result

class SimulNode: # object
    pass

class SimulSCHCNode(SimulNode):
    def __init__(self, sim, extra_config={}):
        self.sim = sim
        self.config = sim.simul_config.get("node-config", {}).copy()
        self.config.update(extra_config)

        self.layer2 = SimulLayer2(sim)
        self.layer3 = SimulLayer3(sim)
        self.protocol = schc.SCHCProtocol(
            self.config, self, self.layer2, self.layer3)
        self.id = self.layer2.mac_id
        self.sim._add_node(self)

    def event_receive(self, sender_id, packet):
        self._log("recv from {}".format(sender_id))
        self.layer2.event_receive_packet(sender_id, packet)

    def get_scheduler(self):
        return self.sim.scheduler

    def _log(self, message):
        self.log("node", message)

    def log(self, name, message):
        self.sim.log(name, "@{} {}".format(self.layer2.mac_id, message))


class SimulNullNode(SimulNode):
    pass


class Simul:
    def __init__(self, simul_config = {}):
        self.simul_config = simul_config
        self.node_table = {}
        self.link_set = set()
        self.event_id = 0
        self.scheduler = Scheduler()
        self.log_file = None
        self.frame_loss = ConditionalTrue(
                **self.simul_config.get("loss", {"mode":"cycle"}))

    def set_log_file(self, filename):
        self.log_file = open(filename, "w")

    def log(self, name, message): # XXX: put Soichi type of logging
        if not self.simul_config.get("log", False):
            return
        line = "{} [{}] ".format(self.scheduler.get_clock(), name) + message
        print(line)
        if self.log_file != None:
            self.log_file.write(line+"\n")

    def _log(self, message):
        self.log("sim", message)

    # XXX:optimize
    def get_link_by_id(self, src_id=None, dst_id=None):
        result = []
        for link in sorted(self.link_set):
            if (     ((src_id is None) or (link.from_id == src_id))
                 and ((dst_id is None) or (link.to_id == dst_id))):
                result.append(link)
        return result

    def send_packet(self, packet, src_id, dst_id=None,
                    callback=None, callback_args=tuple() ):
        if not self.frame_loss.check():
            self._log("send-packet {}->{} {}".format(src_id, dst_id, packet))
            Statsct.log("send-packet {}->{} {}".format(src_id, dst_id, packet))
            Statsct.add_packet_info(packet,src_id,dst_id, True)
            # if dst_id == None, it is a broadcast
            link_list = self.get_link_by_id(src_id, dst_id)
            count = 0
            for link in link_list:
                count += self.send_packet_on_link(link, packet)
        else:
            self._log("packet was lost {}->{}".format(src_id, dst_id))
            Statsct.log("packet was lost {}->{} {}".format(src_id, dst_id, packet))            
            Statsct.add_packet_info(packet,src_id,dst_id, False)
            count = 0
        #
        if callback != None:
            args = callback_args+(count,) # XXX need to check. - CA:
            # [CA] the 'count' is now passed as 'status' in:
            #  SimulLayer2._event_sent_callback(self, transmit_callback, status
            # the idea is that is transmission fails, at least you can pass
            # count == 0 (status == 0), and you can do something there.
            # (in general case, some meta_information need to be sent)

            #args = callback_args
            callback(*args)
        return count

    def send_packet_on_link(self, link, packet):
        node_to = self.node_table[link.to_id]
        node_to.event_receive(link.from_id, packet)
        return 1   # 1 -> one packet was sent

    def add_link(self, from_node, to_node, delay=1):
        """Create a link from from_id to to_id.
        Transmitted packets on the link will have a the specified delay
        before being received"""
        assert (from_node.id in self.node_table
                and to_node.id in self.node_table)
        link = Link(from_id=from_node.id, to_id=to_node.id, delay=delay)
        # XXX: check not another link there with same from_id, same to_id
        self._log("add-link {}->{}".format(from_node.id, to_node.id))
        self.link_set.add(link)

    def add_sym_link(self, from_node, to_node, delay=1):
        """Create a symmetrical link between the two nodes, by creating two
        unidirectional links"""
        self.add_link(from_node, to_node, delay)
        self.add_link(to_node, from_node, delay)

    # don't call: automatically called by Node(...)
    def _add_node(self, node):
        """Internal: add a node in the node_table
        (automatically called by Node constructor)"""
        assert node.id not in self.node_table
        self.node_table[node.id] = node

    def run(self):
        self.scheduler.run()

#---------------------------------------------------------------------------
