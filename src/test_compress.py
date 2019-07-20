from schccomp import *
from comp_parser import *
from rulemanager import *

import json

import pprint
import binascii

# rule_base = json.loads(open("example/comp-rule-100.json").read())
# new_rule_set = []
# for i in rule_base["Compression"]: # rule_set entry has been removed
#     rule = {}
#     for k,v in i.items():
#         if isinstance(v, str):
#             rule[k.upper()] = v.upper()
#         else:
#             rule[k.upper()] = v
#     new_rule_set.append(rule)
#
# rule_base["compression"] = new_rule_set # rule_set has been removed
# context = { "comp": rule_base }

#pkt = open("test/icmpv6.dmp", "rb").read()
#input_bbuf = BitBuffer(pkt)

class debug_protocol:
    def _log(*arg):
        print(*arg)

p = Parser(debug_protocol)
#p.parse(pkt, T_DIR_UP)
#c = Compressor(debug_protocol)
#c.init()
#output_bbuf = c.compress(context, input_bbuf, "DW")

#print("---------------------------------------------------------------------------")

#d = Decompressor(debug_protocol)
#c.init()
#decoded_bbuf = d.decompress(context, output_bbuf, "DW")
#print("decoded :", decoded_bbuf)

#print("original:", input_bbuf)

coap = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

print (coap.hex())

v= p.parse(coap, T_DIR_UP)  # or T_DIR_DW
pprint.pprint(v[0])
# print(binascii.hexlify(v[1]))

RM = RuleManager(log=debug_protocol)
RM.Add(file="example/comp-rule-100.json")
RM.Print()

C = Compressor(debug_protocol)
D = Decompressor(debug_protocol)

r = RM.FindRuleFromPacket(v[0], direction="UP")
if r != None:
    print ("selected rule is ", r)
    schc_packet = C.compress(r, v[0], v[1], T_DIR_UP)

    print (schc_packet)
    schc_packet.display("bin")

    rbis = RM.FindRuleFromSCHCpacket(schc=schc_packet)

    if rbis != None:
        pbis = D.decompress(schc_packet, rbis, direction=T_DIR_UP)
        pprint.pprint (v[0])
        pprint.pprint(pbis)
