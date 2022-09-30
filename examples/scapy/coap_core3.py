import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from scapy_connection import *
from gen_utils import dprint, sanitize_value
from compr_parser import Unparser
from scapy.layers.inet import IP
#from scapy.layers.inet6 import IPv6

import pprint
import binascii
import socket
import ipaddress

import cbor2 as cbor

# Create a Rule Manager and upload the rules.
rm = RM.RuleManager()
rm.Add(file="icmp3.json")
rm.Print()

unparser = Unparser()

def processPkt(pkt):
    """ called when scapy receives a packet, since this function takes only one argument,
    schc_machine and scheduler must be specified as a global variable.
    """
    scheduler.run(session=schc_machine)

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
                    uncomp_pkt = schc_machine.schc_recv(device_id=other_end, schc_packet=schc_pkt)                       
                    if uncomp_pkt != None:
                        uncomp_pkt[1].show()
                        send(uncomp_pkt[1], iface="he-ipv6")
                elif udp_dport == connector_port:
                    schc_msg, addr = connector.recvfrom(2000)
                    print (binascii.hexlify(schc_msg))
                    msg = cbor.loads(schc_msg)
                    print(msg)

                    other_end =""
                    techno = msg[1]
                    if techno == 1:
                        other_end += "lorawan:"
                        other_end +=  binascii.hexlify(msg[2]).decode("utf-8")
                        other_end += "@" + addr[0]+":"+str(addr[1])
                        
                        rm.FindRuleBySCHCPacket(
                    else:
                        print ("unknown technology")

                    print ("other_end = ", other_end)
                    
            elif ip_proto==41:
                schc_machine.schc_send(bytes(pkt)[34:])

# Start SCHC Machine
POSITION = T_POSITION_CORE

socket_port = 0x5C4C
connector_port = 33033
tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", socket_port))
connector = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
connector.bind(("0.0.0.0", connector_port))

lower_layer = ScapyLowerLayer(position=POSITION, socket=tunnel, other_end=None)
system = ScapySystem()
scheduler = system.get_scheduler()
schc_machine = SCHCProtocol(
    system=system,           # define the scheduler
    layer2=lower_layer,      # how to send messages
    role=POSITION,           # DEVICE or CORE
    verbose = True)         
schc_machine.set_rulemanager(rm)

sniff(prn=processPkt, iface=["ens3", "lo"]) # scappy cannot read multiple interfaces

