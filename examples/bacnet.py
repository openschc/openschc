# to save as a pcap: sudo tcpdump -i en0 -w test.pcap
# python3.9 -m pip install scapy
from scapy.all import *
import os
os.sys.path.append('../src')

import compr_parser as parser
from compr_core import *

import binascii

class debug_protocol:
    def _log(*arg):
        print (arg)

parse = parser.Parser(debug_protocol)

sequence = rdpcap("atomic-read-file-50.cap")

dst = "192.168.0.8"
src = "192.168.0.17"

for pkt in sequence:
    if pkt.haslayer(IP):
        if pkt[IP].fields['dst'] == "192.168.0.8":
            dir = T_DIR_UP
        else:
            dir = T_DIR_DW

        a, b, c = parse.parse(pkt=bytes(pkt)[18:], direction=dir, start="IPv6")
        print (a, b, c)
