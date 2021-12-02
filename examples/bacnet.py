# to save as a pcap: sudo tcpdump -i en0 -w test.pcap
# python3.9 -m pip install scapy
from scapy.all import *
import os
os.sys.path.append('../src')

import compr_parser as parser
from compr_core import *
import gen_rulemanager as RM

import binascii

class debug_protocol:
    def _log(*arg):
        print (arg)

parse = parser.Parser(debug_protocol)
compressor = Compressor(debug_protocol)
#decompressor = Decompressor(debug_protocol)

sequence = rdpcap("atomic-read-file-50.cap")

dst = "192.168.0.8"
src = "192.168.0.17"

rm = RM.RuleManager()
rm.Add(file="ipv4.json")
rm.Print()

# for pkt in sequence:
#     if pkt.haslayer(IP):
#         if pkt[IP].fields['dst'] == "192.168.0.8":
#             dir = T_DIR_UP
#         else:
#             dir = T_DIR_DW
#
#         a, b, c = parse.parse(pkt=bytes(pkt)[14:], layers=["IPv4", "UDP"], direction=dir, start="IPv4")
#         r, d = rm.FindRuleFromPacket(a, direction=dir, failed_field=False)
#         #print (a, b, c)
#         #print(d)
#         if r:
#             schc_pkt = compressor.compress(r, a, b, direction=dir)
#             print (len(schc_pkt._content), len(bytes(pkt)[14:]))
#             #print ("{} {}".format(len(schc_pkt._content)), '=')
#             #r2 = rm.FindRuleFromSCHCpacket(schc_pkt, "udp:90.27.174.128:8888")
#             #print (r2)
#             #orig = decompressor.decompress(schc_pkt, r2, direction=dir)
#             #print (orig)

