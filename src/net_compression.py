import os
import sys
sys.path.insert(0, '../..')
import binascii
import pprint

# -----   SCHC ------


from gen_rulemanager import *
from compr_parser import *
from gen_utils import dprint, dpprint


# ----- scapy -----

from kamene.all import *

import ipaddress

class debug_protocol:
    def _log(*arg):
        dprint(*arg)

P = Parser(debug_protocol)
RM = RuleManager()

def AnalyzePkt(packet):
    global RM
    
    dprint(len(packet), "".join(["%02x"%_ for _ in bytes(packet)]))

    withoutL2 = bytes(packet)

    print ("".join(["%02x"%_ for _ in withoutL2]))
    try:
        fields, data = P.parse(withoutL2, direction=T_DIR_DW)
    except:
        print ("not a parsable packet")
        return
        
    dpprint(fields)
    dprint(data)
    
    rule,dev_id = RM.FindRuleFromPacket(fields, direction=T_DIR_DW)
    pprint.pprint (rule)

    if rule == None:
        return
    
    if "Action" in rule:
        if rule[T_ACTION] == T_ACTION_PPING:
            print ("proxy ping")

            print (hex(fields[(T_IPV6_DEV_PREFIX, 1)][0]))
            print (hex(fields[(T_IPV6_DEV_IID, 1)][0]))
            print (hex(fields[(T_IPV6_APP_PREFIX, 1)][0]))
            print (hex(fields[(T_IPV6_APP_IID, 1)][0]))

            IPv6Src = (fields[(T_IPV6_DEV_PREFIX, 1)][0]<< 64) + fields[(T_IPV6_DEV_IID, 1)][0]
            IPv6Dst = (fields[(T_IPV6_APP_PREFIX, 1)][0]<< 64) + fields[(T_IPV6_APP_IID, 1)][0]


            IPv6SrcStr = ipaddress.IPv6Address(IPv6Src)
            IPv6DstStr = ipaddress.IPv6Address(IPv6Dst)

            IPv6Header = IPv6 (
                version = fields[(T_IPV6_VER, 1)][0],
                tc      = fields[(T_IPV6_TC,  1)][0],
                fl      = fields[(T_IPV6_FL,  1)][0],
                nh      = fields[(T_IPV6_NXT, 1)][0],
                hlim    = 30,
                src     = IPv6SrcStr.compressed,
                dst     = IPv6DstStr.compressed
                )

            txt = "SCHC device is alive"

            Echo = ICMPv6EchoReply(
                id  = fields[(T_ICMPV6_IDENT, 1)][0],
                seq = fields[(T_ICMPV6_SEQNB, 1)][0],
                data = data
                #data = txt.encode() + data[len(txt):]
            )

            myMessage = IPv6Header / Echo
            myMessage.show()
            send (myMessage, iface="he-ipv6")
    else:
        pass  #should compresss
        
if __name__ == '__main__':

    print (sys.argv)

    RM = RuleManager()
    RM.Add(file="example/comp-rule-100.json")

    sniff (filter="ip6", prn=AnalyzePkt, iface="he-ipv6")
