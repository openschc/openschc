from schccomp import *
from comp_parser import *

import json

rule_base = json.loads(open("example/comp-rule-100.json").read())
new_rule_set = []
for i in rule_base["compression"]["rule_set"]:
    rule = {}
    for k,v in i.items():
        if isinstance(v, str):
            rule[k.upper()] = v.upper()
        else:
            rule[k.upper()] = v
    new_rule_set.append(rule)

rule_base["compression"]["rule_set"] = new_rule_set
context = { "comp": rule_base }

pkt = open("test/icmpv6.dmp", "rb").read()
input_bbuf = BitBuffer(pkt)

class debug_protocol:
    def _log(*arg):
        print(*arg)

p = Parser(debug_protocol)
p.parse(pkt, T_DIR_UP)
c = Compressor(debug_protocol)
c.init()
output_bbuf = c.compress(context, input_bbuf, "DW")

print("---------------------------------------------------------------------------")

d = Decompressor(debug_protocol)
c.init()
decoded_bbuf = d.decompress(context, output_bbuf, "DW")
print("decoded :", decoded_bbuf)

print("original:", input_bbuf)

coap = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

print ("And CoAP")
v= p.parse(coap, T_DIR_UP)
print (v)
