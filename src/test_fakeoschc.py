# C. A.

# Template for schc

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
from fakeschcrecv import FakeSCHCProtocolReceiver
from fakeschcsend import FakeSCHCProtocolSender, rule_from_dict 

rule_as_dict = {
    # Header format
    "rule-id-size": 6,
    "dtag-size": 2,
    "window-size": 5,
    "fcn-size": 3,
    "mode": "ack-on-error",

    "tile-size": 30,
    "mic-algorithm": "crc32"
}

rule = rule_from_dict(rule_as_dict)

def make_recv_node(scheduler):
    config = {}
    mac = simlayer2.SimulLayer2(scheduler)
    protocol = FakeSCHCProtocolReceiver(config, scheduler, mac)
    # protocol.rulemanager.add_rule(...) ???
    protocol.set_frag_rule(rule)
    return mac, protocol

def make_send_node(scheduler):
    config = {}
    mac = simlayer2.SimulLayer2(scheduler)
    protocol = FakeSCHCProtocolSender(config, scheduler, mac)
    # protocol.rulemanager.add_rule(...) ???
    protocol.set_frag_rule(rule)
    return mac, protocol


scheduler = simsched.SimulScheduler()
m0, p0 = make_recv_node(scheduler)
m1, p1 = make_send_node(scheduler)

m1.add_link(m0)
m0.add_link(m1)

print("mac_id:", m0.mac_id, m1.mac_id)

def make_send_packet(protocol, packet):
    protocol.send_packet(packet)

#scheduler.add_event(1, make_send_packet, (p1, b"00000000"))  # XXX to change
p1.start_sending()

scheduler.run()
