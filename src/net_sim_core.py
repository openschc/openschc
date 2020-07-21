"""
.. module:: simul
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from gen_base_import import *
from net_sim_sched import SimulScheduler as Scheduler
from net_sim_layer2 import SimulLayer2
from net_sim_loss import PacketLossModel
import net_sim_record
from gen_utils import dprint
import gen_utils


try:
    import utime as time
except ImportError:
    import time

import types
import random

import protocol
from frag_send import FragmentAckOnError
from frag_recv import ReassemblerAckOnError
from stats.statsct import Statsct

#---------------------------------------------------------------------------

enable_statsct = True

Link = namedtuple("Link", "from_id to_id delay")

SimulNode = SimulLayer2

class SimulLayer3:
    # Using prefix 2001:DB8::/32, as it is reserved for documentation (see RFC 3849):
    __v6addr_prefix = "2001:0db8:85a3:0000:0000:0000:0000:000"
    __v6addr_base = 0

    def __init__(self, sim):
        self.sim = sim
        self.protocol = None
        self.L3addr = SimulLayer3.__get_unique_addr() #XXX: remove

    def send_later(self, rel_time, dst_l2_address, dst_l3_address, raw_packet):
        self._log("send-later Devaddr={} Packet={}".format(
                dst_l2_address, dst_l3_address, b2hex(raw_packet)))
        self.sim.scheduler.add_event(
            rel_time, self.protocol.schc_send,
            (dst_l2_address, dst_l3_address, raw_packet,))

    # XXX need to confirm whether this should be here or not.
    def recv_packet(self, dev_L2addr, raw_packet):
        """ Two lines below commented"""
        # self._log("recv-from-L2 Devaddr={} Packet={}".format(
        #         dev_L2addr, b2hex(raw_packet.get_content())))
        # XXX do more work

    def _set_protocol(self, protocol): # called by SCHCProtocol
        self.protocol = protocol

    def _log(self, message):
        self.protocol.system.log("L3", message)

    @classmethod
    def __get_unique_addr(cls):
        assert cls.__v6addr_base < 10 # XXX: should never be larger than 10
        result = "{}{}".format(cls.__v6addr_prefix, cls.__v6addr_base)
        cls.__v6addr_base += 1
        return result

#---------------------------------------------------------------------------

class SimulNode: # object
    pass

class SimulSCHCNode(SimulNode):
    def __init__(self, sim, extra_config={}, role="undefined"):
        self.sim = sim
        self.config = sim.simul_config.get("node-config", {}).copy() # XXX: remove?
        self.config.update(extra_config)
        unique_peer = self.config.get("unique-peer", True) # XXX:remove default

        self.layer2 = SimulLayer2(sim)
        self.layer3 = SimulLayer3(sim)
        self.protocol = protocol.SCHCProtocol(
            self.config, self, self.layer2, self.layer3, role, unique_peer)
        self.id = self.layer2.mac_id
        self.sim._add_node(self)

    def event_receive(self, sender_id, packet):
        self._log("----------------------- RECEIVED PACKET -----------------------")
        self._log("recv from {}".format(sender_id))
        self.layer2.event_receive_packet(sender_id, packet)

    def get_scheduler(self):
        return self.sim.scheduler

    def _log(self, message):
        self.log("node", message)

    def log(self, name, message):
        self.sim.log(name, "@{} {}".format(self.layer2.mac_id, message))

    def get_state_info(self, **kw):
        result = {
            "protocol": self.protocol.get_state_info(**kw)
        }
        return result

    def get_init_info(self, **kw):
        result = {
            "protocol": self.protocol.get_init_info(**kw)
        }
        result["config"] = self.config.copy()
        result["id"] = self.id
        return result


class SimulNullNode(SimulNode):
    pass

#---------------------------------------------------------------------------

PACKET_PER_SECOND = 1
PROPAGATION_DELAY = 0 # XXX: if >0, the callback gets called too late

class Channel:
    def __init__(self, sim):
        self.sim = sim
        self.node_time_table = {}

    def transmit_packet(self, src_id, packet, callback, callback_args):
        clock = self.sim.scheduler.get_clock()
        available_time = self.node_time_table.get(src_id, clock)
        available_time = max(available_time, clock)
        available_time += 1/PACKET_PER_SECOND
        self.node_time_table[src_id] = available_time
        delivery_rel_time = (available_time + PROPAGATION_DELAY) - clock
        #callback(*callback_args)
        self.sim.scheduler.add_event(delivery_rel_time, callback, callback_args)

# ---------------------------------------------------------------------------

NO_LOSS_CONFIG = {"mode": "cycle"} # no cycle size, corresponds to no loss

class Simul:
    def __init__(self, simul_config = {}):
        self.simul_config = simul_config
        self.node_table = {}
        self.link_set = set()
        self.event_id = 0
        self.scheduler = Scheduler()
        self.log_file = None
        self.observer = None
        self.channel = Channel(self)
        self.init_from_config()

    def init_from_config(self):
        self.scheduler.add_event(0, self._notify_start, ())
        if self.simul_config.get("seed") is not None:
            random.seed(self.simul_config["seed"])
        self.frame_loss = PacketLossModel(
                **self.simul_config.get("loss", NO_LOSS_CONFIG))

        with_dprint = bool(self.simul_config.get("enable-print", True))
        gen_utils.set_debug_output(with_dprint)
        if not self.simul_config.get("enable-trace", True):
            gen_utils.set_trace_function(None)

        record_dir_name = self.simul_config.get("record.directory")
        should_record = bool(self.simul_config.get("record.enable", False))
        if (record_dir_name is not None) and should_record:
            record_quiet = bool(self.simul_config.get("record.quiet"))
            obs = net_sim_record.SimulRecordingObserver(self)
            self.set_observer(obs)
            obs.start_record(record_dir_name, record_quiet) # XXX: should be at sim start.

    def _notify_start(self):
        pass # just used for recording (initial event)

    def set_log_file(self, filename):
        self.log_file = open(filename, "w")

    def log(self, name, message):
        if not self.simul_config.get("log", False):
            return
        line = "{} [{}] ".format(self.scheduler.get_clock(), name) + message
        dprint(line)
        if self.log_file is not None:
            self.log_file.write(line+"\n")
        if self.observer is not None:
            self.observer.record_log(line)

    def set_observer(self, observer):
        assert self.observer is None
        self.observer = observer
        self.scheduler.set_observer(observer.sched_observer_func)

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
                    callback=None, callback_args=tuple(), with_hack=False):
        if self.channel is None:
            return self.deliver_packet(
                packet, src_id, dst_id, callback, callback_args, with_hack)
        else:
            return self.channel.transmit_packet(
                src_id, packet, self.deliver_packet,
                (packet, src_id, dst_id, callback, callback_args, with_hack))

    def deliver_packet(self, packet, src_id, dst_id=None,
                    callback=None, callback_args=tuple(), with_hack=False):
        self._log("----------------------- SEND PACKET -----------------------")
        lost = self.frame_loss.is_lost(len(packet))
        if not lost:
            self._log("----------------------- OK -----------------------")
            self._log("send-packet {}->{} {}".format(src_id, dst_id, packet))
            if enable_statsct:
                Statsct.log("send-packet {}->{} {}".format(src_id, dst_id, packet))
                clock = self.scheduler.get_clock()
                Statsct.add_packet_info(clock, packet, src_id, dst_id, True)
            # if dst_id == None, it is a broadcast
            link_list = self.get_link_by_id(src_id, dst_id)
            if not with_hack:
                count = 0
                for link in link_list:
                    count += self.send_packet_on_link(link, packet)
            else:
                count = 1
                self._send_packetX_hack() # [CA] should be removed
        else:
            self._log("----------------------- KO -----------------------")
            self._log("packet was lost {}->{}".format(src_id, dst_id))
            if enable_statsct:
                Statsct.log("packet was lost {}->{} {}".format(src_id, dst_id, packet))
                clock = self.scheduler.get_clock()
                Statsct.add_packet_info(clock, packet, src_id, dst_id, False)
            count = 0
        #
        if self.observer is not None:
            info = {"src":src_id, "dst":dst_id, "packet":packet,
                    "clock": clock, "count":count, "lost":lost,
                    "event-id": self.scheduler._get_event_id() }
            self.observer.record_packet(info)

        if callback != None: #XXX: should called by channel after delay
            args = callback_args+(count,) # XXX need to check. - CA:
            # [CA] the 'count' is now passed as 'status' in:
            #  SimulLayer2._event_sent_callback(self, transmit_callback, status
            # the idea is that is transmission fails, at least you can pass
            # count == 0 (status == 0), and you can do something there.
            # (in general case, some meta_information need to be sent)

            #args = callback_args
            callback(*args)
        return count

    # XXX: this method should be removed, and object oriented style should be used:
    # [CA] didn't understood the logic here, so kept as is:
    def _send_packetX_hack(self):
            self.ACK_SUCCESS = "ACK_SUCCESS" # XXX: this should not be here
            self.ACK_FAILURE = "ACK_FAILURE"
            self.RECEIVER_ABORT = "RECEIVER_ABORT"
            self.SEND_ALL_1 = "SEND_ALL_1"
            self.WAITING_FOR_ACK = "WAITING_FOR_ACK"
            self.ACK_TIMEOUT = "ACK_TIMEOUT"

            count = 1
            # for link in link_list:
            #     count += self.send_packet_on_link(link, packet)
            note_table_list = list(self.node_table.items())[-1][1]
            #self.node_table[0].protocol.layer2.clientSend.send(packet)

            note_table_list.protocol.layer2.roleSend.send(packet) # XXX: should not be changed

            try:
                number_tiles_send = \
                    note_table_list.protocol.fragment_session.session_list[0]["session"].current_number_tiles_sent()
                state = note_table_list.protocol.fragment_session.session_list[0]["session"].state
                dprint("STATE : ", state)
                dprint("Lenght queue", len(self.scheduler.queue))
                if (state == self.SEND_ALL_1 or state == self.ACK_FAILURE or state == self.ACK_TIMEOUT) \
                        and number_tiles_send == 0:
                    dprint("------------------------------- RECEIVE PACKET ------------------------------")
                    message = note_table_list.protocol.layer2.roleSend.Receive() # XXX: should not be here
                    dprint("Message from Server", message)
                    note_table_list.protocol.layer2.event_receive_packet(note_table_list.id, message)
                    # note_table_list1.protocol.fragment_session.session_list[0]["session"].state = 'START'
            except:
                dprint("Not fragment state")

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
        if self.observer is not None:
            self.observer.record_initial_state()
        self.scheduler.run()
        if self.observer is not None:
            self.observer.stop_record()

    # ---------- Introspection for recording

    def get_state_info(self, **kw):
        helpers = self._get_sanitize_helpers()
        queue = self.scheduler._get_queue_content(helpers)
        result = {
            "node_table": {
                node_id: node.get_state_info(**kw)
                for node_id, node in self.node_table.items()
            },
            "queue": [self._filter_event(event) for event in queue]
        }
        return result

    def _filter_event(self, event):
        import inspect
        (abs_time, event_id, callback, args) = event
        result = {"clock":abs_time, "event-id": event_id}
        result["callback"] = self._filter_value(callback)
        result["args"] = tuple(self._filter_value(x) for x in args)
        return result

    def __sanitize_SimulLayer2(self, instance, info):
        info["node-id"] = instance.protocol.get_system().id
        return info

    def __sanitize_frag(self, instance, info):
        info["node-id"] = instance.protocol.get_system().id
        return info

    def __sanitize_protocol(self, instance, info):
        info["node-id"] = instance.get_system().id
        return info

    def _get_sanitize_helpers(self):
        helpers = {
            SimulLayer2.__name__: self.__sanitize_SimulLayer2,
            FragmentAckOnError.__name__: self.__sanitize_frag,
            ReassemblerAckOnError.__name__: self.__sanitize_frag,
            protocol.SCHCProtocol.__name__: self.__sanitize_protocol
        }
        return helpers

    def _filter_value(self, value):
        helpers = self._get_sanitize_helpers()
        result = gen_utils.sanitize_value(value, helpers)
        return result

    def get_init_info(self, **kw):
        # avoid difference in recording, just because of dir name:
        simul_config = self.simul_config.copy()
        simul_config["record.directory"] = "<here>"

        result = {
            "links": [link_as_dict(link) for link in self.link_set],
            "simul_config": simul_config,
            "node_table": {
                node_id: node.get_init_info(**kw)
                for node_id, node in self.node_table.items()
            }
        }
        return result

#---------------------------------------------------------------------------

def link_as_dict(link):
    return {"to": link.to_id, "from": link.from_id, "delay": link.delay}

#---------------------------------------------------------------------------
