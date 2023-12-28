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
import netifaces as ni

addr = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

PORT = 8888
deviceID = "udp:"+addr+":"+str(PORT)

print("device ID is", deviceID)

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind (("0.0.0.0", PORT)) # same port as in the DeviceID

while True:
    SCHC_pkt, sender = tunnel.recvfrom(1000)
    print ("SCHC Packet:", binascii.hexlify(SCHC_pkt), 
                          "from", sender)
    rule = rm.FindRuleFromSCHCpacket(schc=SCHC_pkt, device=deviceID)
    if rule: # Echo Request Rule
        print ("Rule {}/{}".format(rule[T_RULEID],
                                   rule[T_RULEIDLENGTH]))
        if rule[T_RULEID] == 6 and rule[T_RULELENGTH] == 3:
            tunnel.sendto(SCHC_pkt, sender)
        else:
            print ("Not the Echo Request rule")
    else:
        print ("rule not found")






 
