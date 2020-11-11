import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *
import binascii
import gen_rulemanager as RM
import compr_parser as parser
from compr_core import *

import pprint
import binascii

import socket


class debug_protocol:
    def _log(*arg):
        print (arg)

parse = parser.Parser(debug_protocol)
rm    = RM.RuleManager()
rm.Add(file="icmp.json")
rm.Print()

comp = Compressor(debug_protocol)
decomp = Decompressor(debug_protocol)

def processPkt(pkt):
    global parser
    global rm
    
    # look for a tunneled SCHC pkt

    e_type = pkt.getlayer(Ether).type
    if e_type == 0x0800:
        ip_proto = pkt.getlayer(IP).proto
        if ip_proto == 17:
            udp_dport = pkt.getlayer(UDP).dport
            if udp_dport == 8888: # tunnel SCHC msg to be decompressed
               print ("tunneled SCHC msg")
               
               schc_pkt, addr = tunnel.recvfrom(2000)
               print (binascii.hexlify(schc_pkt), addr)

               rule = rm.FindRuleFromSCHCpacket(schc_pkt)
               print (rule)

               

        
    elif pkt.getlayer(Ether).version == 0x86dd : # regular trafic to be compression

        pkt_fields, data, err = parse.parse( bytes(pkt), T_DIR_DW, layers=["IP", "ICMP"], start="IPv6")
        print (pkt_fields)

        if pkt_fields != None:
            rule, device = rm.FindRuleFromPacket(pkt_fields, direction=T_DIR_DW)
            if rule != None:
                schc_pkt = comp.compress(rule, pkt_fields, data, T_DIR_DW)
                if device.find("udp") == 0:
                    destination = (device.split(":")[1], int(device.split(":")[2]))
                    print (destination)
                    schc_pkt.display()
                    tunnel.sendto(schc_pkt._content, destination)
                else:
                    print ("unknown connector" + device)
    else:
     print (".", end="", flush=True)           
                    
        
# look at the IP address to define sniff behavior

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]

if ip_addr == "192.168.1.104":
    print("device role")
    send_dir = T_DIR_UP
    recv_dir = T_DIR_DW

    tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tunnel.bind(("0.0.0.0", 8888))

    sniff (filter="ip6 or port 23628 and not arp",
           prn=processPkt,
           iface="enp0s3")
    
elif ip_addr == "51.91.121.182": # tests.openschc.net
    print ("core role")
    send_dir = T_DIR_DW
    recv_dir = T_DIR_UP

    tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tunnel.bind(("0.0.0.0", 0x5C4C))
    
    sniff(prn=processPkt, iface="he-ipv6")

else:
    print ("Unknown host {}, please look at the code to configure it")

 
