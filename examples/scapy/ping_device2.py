import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from scapy_connection import *
from gen_utils import dprint, sanitize_value
from gen_bitarray import *
from compr_parser import Unparser

import pprint
import binascii
import socket
import ipaddress


# Create a Rule Manager and upload the rules.
rm = RM.RuleManager()
rm.Add(file="icmp2.json")
rm.Print()

#Unparser
unparser = Unparser()

def create_echoreply(pkt,src,dst):
    print("packet decompresed: ", pkt)
    #packet_bbuf = BitBuffer(pkt)
    #print("IPV6.VER : ", pkt[('IPV6.FL', 1)])
    IPv6(bytes(pkt)[0:]).show2()

    
    #print(dst)
    #print(src)
    #print("len",len(pkt))

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
                    schc_bbuf = BitBuffer(schc_pkt)
                    rule = rm.FindRuleFromSCHCpacket(schc=schc_bbuf, device=device_id)
                    if rule[T_RULEID] == 6 and rule[T_RULEIDLENGTH]== 3:
                        print ("ping")
                        tunnel.sendto(schc_pkt, addr)
                    else:
                        r = schc_machine.schc_recv(device_id=device_id, schc_packet=schc_pkt)
                        if r is not None: #The schc machine has ressembled and decompressed the packet
                           print ("ping_device.py, r=", r)
                           schc_pkt_dec = r[1]
                           print(len(schc_pkt_dec))
                           create_echoreply(schc_pkt_dec, ip, addr)
                           #schc_machine.schc_send(r[1])
            elif ip_proto==41:
                schc_machine.schc_send(bytes(pkt)[34:])
                pkt.show2()

# Start SCHC Machine
POSITION = T_POSITION_DEVICE

from requests import get

ip = get('https://api.ipify.org').text

socket_port = 8888
tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", socket_port))

device_id = 'udp:'+ip+":"+str(socket_port)
print ("device_id is", device_id)


lower_layer = ScapyLowerLayer(position=POSITION, socket=tunnel, other_end=None)
system = ScapySystem()
scheduler = system.get_scheduler()
schc_machine = SCHCProtocol(
    system=system,           # define the scheduler
    layer2=lower_layer,      # how to send messages
    role=POSITION,           # DEVICE or CORE
    verbose = True)         
schc_machine.set_rulemanager(rm)

sniff(prn=processPkt, iface="ens3") # scappy cannot read multiple interfaces




 
