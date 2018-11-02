# C. A.

# Template for schc

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2

# XXX: create a real class SimulNode and Simul
def make_node(scheduler):
    config = {}
    mac = simlayer2.SimulLayer2(scheduler)
    protocol = schc.SCHCProtocol(config, scheduler, mac)
    return mac, protocol

scheduler = simsched.SimulScheduler()
m0, p0 = make_node(scheduler)
m1, p1 = make_node(scheduler)

m1.add_link(m0)
m0.add_link(m1)

print("mac_id:", m0.mac_id, m1.mac_id)

def make_send_packet(protocol, packet):
    protocol.send_packet(packet)

scheduler.add_event(1, make_send_packet, (p0, b"0000"))

scheduler.run()
