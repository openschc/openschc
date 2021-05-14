import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *
import scapy.contrib.coap as scapy_coap


import gen_rulemanager as RM
import compr_parser as parser
from compr_core import *
from protocol import SCHCProtocol

from scapy_connection import *

from gen_utils import dprint, sanitize_value


import sched

import protocol

import pprint
import binascii

import socket
import ipaddress

import time, datetime


class debug_protocol:
    def _log(*arg):
        print (arg)

parse = parser.Parser(debug_protocol)
rm    = RM.RuleManager()
rm.Add(file="icmp.json")
rm.Print()

comp = Compressor(debug_protocol)
decomp = Decompressor(debug_protocol)

def send_scapy(fields, pkt_bb, rule=None):
    raise ValueError ("should not be here")

    
def send_tunnel(pkt, dest):
    print ("send tunnel")
    print (dest, pkt)
    print (pkt.display())


def processPkt(pkt):
    global parser
    global rm
    global event_queue
    global SCHC_machine
    

    scheduler.run(session=schc_protocol, period=10)

    # look for a tunneled SCHC pkt

    if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
        e_type = pkt.getlayer(Ether).type
        if e_type == 0x0800:
            ip_proto = pkt.getlayer(IP).proto
            if ip_proto == 17:
                udp_dport = pkt.getlayer(UDP).dport
                if udp_dport == socket_port: # tunnel SCHC msg to be decompressed
                    print ("tunneled SCHC msg")                    
                    schc_pkt, addr = tunnel.recvfrom(2000)
                    other_end = "udp:"+addr[0]+":"+str(addr[1])
                    print("other end =", other_end)
                    r = schc_protocol.schc_recv(other_end, schc_pkt)
                    print (r)
            elif ip_proto==41:
                schc_protocol.schc_send(bytes(pkt)[34:])
    elif IP in pkt and pkt.getlayer(IP).version == 6 : # regular IPv6trafic to be compression
        schc_protocol.schc_send(bytes(pkt))
    else:
     print (".", end="", flush=True)           
                    
        
# look at the IP address to define sniff behavior

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]

# Start SCHC Machine
POSITION = T_POSITION_CORE

device_id = None
socket_port = 0x5C4C
other_end = None # defined by the rule


tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", 0x5C4C))

config = {}
upper_layer = ScapyUpperLayer()
lower_layer = ScapyLowerLayer(position=POSITION, socket=tunnel, other_end=other_end)
system = ScapySystem()
scheduler = system.get_scheduler()
schc_protocol = protocol.SCHCProtocol(
    config=config, system=system, 
    layer2=lower_layer, layer3=upper_layer, 
    role=POSITION, unique_peer=False)
schc_protocol.set_position(POSITION)
schc_protocol.set_rulemanager(rm)


#sniff(prn=processPkt, iface=["he-ipv6", "ens3"]) # scappy cannot read multiple interfaces
sniff(prn=processPkt, iface="ens3") # scappy cannot read multiple interfaces




 
