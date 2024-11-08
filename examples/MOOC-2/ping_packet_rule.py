import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')
from compr_parser import Parser
from gen_rulemanager import RuleManager
from gen_parameters import *

from scapy.all import *

import pprint

P = Parser()
RM = RuleManager()
RM.Add(file="icmp-single.json")
RM.Print()

def processPkt(pkt):
     if pkt[Ether].type == 0x86dd and pkt[IPv6].nh == 0x3A: #ICMPv6
        pkt_desc = P.parse(pkt=bytes(pkt)[14:], direction=T_DIR_DW)
        if pkt_desc[2] is None: # No parsing error
            rule = RM.FindRuleFromPacket(pkt_desc[0], T_DIR_DW, True)
            print (rule)

sniff(prn=processPkt, iface=["eth1", "lo"]) 
