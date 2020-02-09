# PYTHONPATH must be set to openschc/src

import binascii
import pprint

"""
This is a no_compression test, ie the packet is sent no compressed with a 
non aligned ruleID of 7 bits. 

"""

from gen_rulemanager import RuleManager
from compr_parser import Parser
from compr_core import Compressor

enable_debug_print = True

"""
6                                       # IPv6 version
00                                      # DiffServ
12345                                   # Flow Label
0039                                    # Payload Length
11                                      # Next Header (UDP)
33                                      # Hop Limit
2001 1222 8905 0470 0000 0000 0000 0057 # Device address
2001 41d0 57d7 3100 0000 0000 0000 0401 # Application address
1634                                    # Device port
1633                                    # Application port
0039                                    # UDL length
7a6e                                    # UDP checksum
5102                                    # CoAP Header NON TLK=1
00a0                                    # Message ID
20                                      # Token
b4 7465 6d70                            # Option Path /temp
d1ea 02                                 # Option Server No Response (4&5 allowed)
ff                                      # end option
981f19074b210503010500220622200600250301220401030300220304010122030a05 # CBOR
"""
packet_src = "6 00 12345 0039 11 33 20011222890504700000000000000057 200141d057d731000000000000000401\
            1634 1633 0039 7a6e\
            5102 00a0 20 b474656d70 d1ea02 ff\
            981f19074b210503010500220622200600250301220401030300220304010122030a05".replace (" ", "")

packet = binascii.unhexlify(packet_src)
print (packet)
    
rule_compress_all = {
    "RuleID": 8,
    "RuleIDLength" : 8,
    "Compression" : [
      {"FID": "IPV6.VER", "TV": 6, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.TC",  "TV": 0, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.FL",  "TV": 0, "MO": "ignore","CDA": "not-sent"},
      {"FID": "IPV6.LEN",          "MO": "ignore","CDA": "compute-length"},
      {"FID": "IPV6.NXT", "TV": 17, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.HOP_LMT", "TV" : 255,"MO": "ignore","CDA": "not-sent"},
      {"FID": "IPV6.DEV_PREFIX","TV": "2001:1222:8905:0470::/64" , "MO": "equal","CDA": "not-sent"},
      {"FID": "IPV6.DEV_IID", "TV": "::57","MO": "equal","CDA": "not-sent"},
      {"FID": "IPV6.APP_PREFIX","TV":  "2001:41d0:57d7:3100::/64", "MO": "equal","CDA": "not-sent"},
      {"FID": "IPV6.APP_IID", "TV": "::0401","MO": "equal","CDA": "not-sent"},
      {"FID": "UDP.DEV_PORT",  "TV": 5684,"MO": "equal",  "CDA": "not-sent"},
      {"FID": "UDP.APP_PORT",  "TV": 5683,"MO": "equal",  "CDA" : "not-sent"},
      {"FID": "UDP.LEN",       "TV": 0,   "MO": "ignore","CDA": "compute-length"},
      {"FID": "UDP.CKSUM",     "TV": 0,  "MO": "ignore","CDA": "compute-checksum"},
    ]
}

RM = RuleManager()
RM.Add(dev_info=rule_compress_all)
RM.Print()

class debug_protocol:
    def _log(*arg):
        print(*arg)

P = Parser(debug_protocol)
headers, data = P.parse(packet, direction="UP", layers=["IPv6", "UDP"])

pprint.pprint(headers)
print (binascii.hexlify(data))


rule = RM.FindRuleFromPacket(headers, direction="UP")
print (rule)

C = Compressor(debug_protocol)
result = C.compress (rule, headers, data, direction="UP")

result.display()
result.display(format="bin")