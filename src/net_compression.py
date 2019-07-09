import os
import sys
sys.path.insert(0, '../..')
import binascii

# -----   SCHC ------


from rulemanager import *


# ----- scapy -----

from kamene.all import *

import ipaddress

def AnalyzePkt(packet):
    print(len(packet), binascii.unhexlify(packet))

    fields, data = packetParser.parser(bytes(packet), direction="dw")
    print("Fields = ", fields, data)
    
    rule =RM.FindRuleFromHeader(fields, "dw")
        
if __name__ == '__main__':

    print (sys.argv)

    RM = RuleManager()

    sniff (filter="ip", prn=AnalyzePkt, iface="enp0s5")
