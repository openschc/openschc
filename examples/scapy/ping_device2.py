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

# Create a ICMPv6 Echo Reply from Echo Request
def create_echoreply(pkt):
    print("packet decompresed: ", pkt)
    ECHO_REQUEST = IPv6(bytes(pkt))
    
    IPv6Header = IPv6 (
        version= ECHO_REQUEST.version ,
        tc     = ECHO_REQUEST.tc,
        fl     = ECHO_REQUEST.fl,
        nh     = ECHO_REQUEST.nh,
        hlim   = ECHO_REQUEST.hlim,
        src    = ECHO_REQUEST.dst, 
        dst    = ECHO_REQUEST.src
    ) 

    ICMPv6Header = ICMPv6EchoReply(
        id = ECHO_REQUEST.id,
        seq =  ECHO_REQUEST.seq,
        data = ECHO_REQUEST.data)

    Echoreply = IPv6Header / ICMPv6Header
    dprint("Echo reply", Echoreply.show())
    return Echoreply

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
                        # None when the reassambly + decompressing process is not finished and [device_id, decompressed packet in bytes] when All-1
                        r = schc_machine.schc_recv(device_id=device_id, schc_packet=schc_pkt) 
                        if r is not None: #The SCHC machine has reassembled and decompressed the packet
                           dprint ("ping_device.py, r =", r)
                           schc_pkt_decompressed = r[1]
                           pkt_reply = create_echoreply(schc_pkt_decompressed)                     
                           uncomp_pkt = schc_machine.schc_send(bytes(pkt_reply))
                           print(uncomp_pkt)
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




 
