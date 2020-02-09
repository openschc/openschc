# PYTHONPATH must be set to openschc/src

import binascii
import pprint

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
    
rule_default_8bits = {
    "RuleID": 8,
    "RuleIDLength" : 8,
    "NoCompression" : []
}

RM = RuleManager()
RM.Add(dev_info=rule_default_8bits)
RM.Print()

r = RM.FindNoCompressionRule()
print (r)

class debug_protocol:
    def _log(*arg):
        print(*arg)

C = Compressor(debug_protocol)
result = C.no_compress (r, packet)

result.display()
result.display(format="bin")