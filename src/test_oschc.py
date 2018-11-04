# C. A.

# Template for schc

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2

rule = {
    "rule-id": 3,
    "mode": "ack-on-error",
    "dtag-size": 2,
    "window-size": 5,
    "fcn-size": 3,
    # MAX_WIND_FCN computed from "fcn-size"
    "tile-size": 30,
    "mic-algorithm": "crc32",
    "ack-after-recv-all1": True,
}
# XXX: make a namedtuple?

# XXX: create a real class SimulNode and Simul
def make_node(scheduler, role="sender"):
    config = {}
    mac = simlayer2.SimulLayer2(scheduler)
    protocol = schc.SCHCProtocol(config, scheduler, mac, role=role)
    # protocol.rulemanager.add_rule(...) ???
    protocol.set_frag_rule(rule)
    return mac, protocol

scheduler = simsched.SimulScheduler()
m0, p0 = make_node(scheduler)
m1, p1 = make_node(scheduler, role="receiver")

m1.add_link(m0)
m0.add_link(m1)

print("mac_id:", m0.mac_id, m1.mac_id)

def make_send_packet(protocol, packet):
    protocol.send_packet(packet)

#scheduler.add_event(1, make_send_packet, (p0, bytearray(range(1, 8+1))))
scheduler.add_event(1, make_send_packet, (p0, bytearray(range(1, 2+1))))

scheduler.run()
