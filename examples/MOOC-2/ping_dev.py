import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')
import gen_rulemanager as RM
from gen_parameters import *


rm = RM.RuleManager()
rm.Add(file="icmp-bi.json")
rm.Print()

import socket
import binascii

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind (("0.0.0.0", 8888)) # same port as in the DeviceID

deviceID = "udp:10.0.0.20:8888"

while True:
    SCHC_pkt, sender = tunnel.recvfrom(1000)
    print ("SCHC Packet:", binascii.hexlify(SCHC_pkt), "from", sender)
    rule = rm.FindRuleFromSCHCpacket(SCHC_pkt, devide=deviceID)
    if rule:
        print ("Rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
    else:
        print ("rule not found")






 
