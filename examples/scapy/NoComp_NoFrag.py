import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from scapy_connection import *
from gen_utils import dprint, sanitize_value

import pprint
import binascii
import socket
import ipaddress

rm = RM.RuleManager()
#rm.Add(file="icmp1.json")
#rm.Add(file="icmp2.json")
#rm.Print()

# Start SCHC Machine
POSITION = T_POSITION_CORE
system = ScapySystem()

socket_port = 0x5C4C
tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", socket_port))

lower_layer = ScapyLowerLayer(position=POSITION, socket=tunnel, other_end=None)
scheduler = system.get_scheduler()


schc_protocol = SCHCProtocol(
    system=system,           # define the scheduler
    layer2=lower_layer,      # how to send messages
    role=POSITION,           # DEVICE or CORE
    verbose = True)         
schc_protocol.set_rulemanager(rm)

pkt = IPv6(dst="2001:db8::c0:ffee") / ICMPv6EchoRequest()
schc_protocol.rule_manager.Add(
    dev_info={"RuleID": 22, "RuleIDLength": 8, "NoCompression": []},
)
schc_protocol.schc_recv((bytes([22]) + raw(pkt)))