# C. A.

# Template for schc

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
from schcrecv import SCHCProtocolReceiver
from schcsend import SCHCProtocolSender
from fakerulemgr import rule_from_dict

raise RuntimeError("XXX: new simul. architecture in test_newschc.py")

rule_as_dict = {
    "rule-id-size": 6,
    "rule-id": 5,
    "dtag-size": 2,
    "window-size": 5,
    "fcn-size": 3,
    "mode": "ack-on-error",
    "tile-size": 30,
    "mic-algorithm": "crc32",

#    "rule-id": 3,
#    "ack-mode": "ack-after-recv-all1"
}

rule = rule_from_dict(rule_as_dict)

# XXX: create a real class SimulNode and Simul
def make_send_node(scheduler):
    config = {"a":0}
    mac = simlayer2.SimulLayer2(scheduler)
    protocol = SCHCProtocolSender(config, scheduler, mac)
    # protocol.rulemanager.add_rule(...) ???
    protocol.set_frag_rule(rule)
    return mac, protocol

def make_recv_node(scheduler):
    config = {}
    mac = simlayer2.SimulLayer2(scheduler)
    protocol = SCHCProtocolReceiver(config, scheduler, mac)
    # protocol.rulemanager.add_rule(...) ???
    protocol.rule_manager.set_frag_rule(rule)
    return mac, protocol

scheduler = simsched.SimulScheduler()
m0, p0 = make_send_node(scheduler)
m1, p1 = make_recv_node(scheduler)

m1.add_link(m0)
m0.add_link(m1)

print("mac_id:", m0.mac_id, m1.mac_id)

def make_send_packet(protocol, packet):
    protocol.send_packet(packet)

#scheduler.add_event(1, make_send_packet, (p0, bytearray(range(1, 8+1))))
scheduler.add_event(1, make_send_packet, (p0, bytearray(range(1, 2+1))))

scheduler.run()
