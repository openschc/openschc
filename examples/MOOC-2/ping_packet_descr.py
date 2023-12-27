import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

from compr_parser import Parser
from gen_parameters import *

import pprint

# Create a Rule Manager and upload the rules.

P = Parser()

def processPkt(pkt):
    """ called when scapy receives a packet, since this function takes only one argument,
    schc protocol must be specified as a global variable.
    """

    if pkt[Ether].type == 0x86dd and pkt[IPv6].nh == 0x3A: #ICMPv6
        pkt_desc = P.parse(pkt=bytes(pkt), direction=T_DIR_DW)
        pprint.pprint(pkt_desc)


    # if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
    #     e_type = pkt.getlayer(Ether).type
    #     if e_type == 0x0800:
    #         ip_proto = pkt.getlayer(IP).proto
    #         if ip_proto == 17:
    #             udp_dport = pkt.getlayer(UDP).dport
    #             if udp_dport == socket_port: # tunnel SCHC msg to be decompressed
    #                 print ("tunneled SCHC msg")                    
    #                 schc_pkt, addr = tunnel.recvfrom(2000)
    #                 other_end = "udp:"+addr[0]+":"+str(addr[1])
    #                 print("other end =", other_end)
    #                 r = schc_machine.schc_recv(other_end, schc_pkt)
    #                 print (r)
    #         elif ip_proto==41:
    #             schc_machine.schc_send(bytes(pkt)[34:])



sniff(prn=processPkt, iface="eth1") # scappy cannot read multiple interfaces




 
