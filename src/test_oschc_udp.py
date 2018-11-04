# C. A.

# Template for schc

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import udp_wrapper

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
    sim = udp_wrapper.udp_wrapper(scheduler, bind_addr=("127.0.0.1", 9998))
    protocol = schc.SCHCProtocol(config, scheduler, sim, role=role)
    # protocol.rulemanager.add_rule(...) ???
    protocol.set_frag_rule(rule)
    return sim, protocol

scheduler = simsched.SimulScheduler()
sim0, p0 = make_node(scheduler)
#m1, p1 = make_node(scheduler, role="receiver")

sim0.add_link(("127.0.0.1", 9999))

print("my iid:", sim0.iid)

def make_send_packet(protocol, packet):
    protocol.send_packet(packet)

#scheduler.add_event(1, make_send_packet, (p0, bytearray(range(1, 8+1))))
scheduler.add_event(1, make_send_packet, (p0, bytearray(range(1, 2+1))))

scheduler.run()
