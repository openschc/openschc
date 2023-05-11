#!/usr/bin/env python3
from scapy.all import *

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from compr_parser import Parser
from gen_parameters import *
from gen_rulemanager import RuleManager

import pprint

# rdpcap comes from scapy and loads in our pcap file
packets = rdpcap('trace_coap.pcap')

parser = Parser()

RM = RuleManager()
RM.Add(file="ipv6-sol-bi-fl.json")
RM.Print()

# Let's iterate through every packet
for packet in packets:
    #hexdump(packet[IPv6])
    #packet[IPv6].show()

    if packet[Ether].src == "fa:16:3e:1e:cc:2c":
        direction = T_DIR_DW
    elif packet[Ether].dst == "fa:16:3e:1e:cc:2c":
        direction = T_DIR_UP
    else: # skipping
        break

    print ("Packet direction ", direction)

    parsed = parser.parse (bytes(packet[IPv6]), 
                           direction, 
                           layers=["IPv6", "UDP"])
    pprint.pprint (parsed)

    if parsed[0] != None:
        rule = RM.FindRuleFromPacket(pkt=parsed[0], 
                                     direction=direction, 
                                     failed_field=True)
        
        print ("Rule for packet")
        pprint.pprint(rule)

