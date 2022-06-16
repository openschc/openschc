from gen_base_import import b2hex
from compr_core import *
from compr_parser import *
from gen_rulemanager import *

import pprint
import binascii


class debug_protocol:
    def _log(*arg):
        print(*arg)

p = Parser(debug_protocol)

coap = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

print (b2hex(coap))

v = p.parse(coap, T_DIR_UP)  # or T_DIR_DW
pprint.pprint(v[0])

RM = RuleManager(log=debug_protocol)
RM.Add(file="../examples/configs/comp-rule-100.json")
RM.Print()

C = Compressor(debug_protocol)
D = Decompressor(debug_protocol)

r,dev_id = RM.FindRuleFromPacket(v[0], direction="UP")
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
