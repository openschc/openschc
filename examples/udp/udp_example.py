import sys, getopt
sys.path.append('/home/laurent/github/openschc-pr/src')

    
from net_udp_core import  *

# --------------------------------------------------

compression_rule = {
    "RuleID": 12,
    "RuleIDLength": 4,
    "Compression": []
}

frag_rule_noack = {
    "RuleID" : 12,
    "RuleIDLength" : 6,
    "Fragmentation" : {
        "FRMode": "noAck",
        "FRDirection": "UP"
    }
}

rule_set = [compression_rule.copy(), frag_rule_noack.copy()]

coap_ip_packet = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

# --------------------------------------------------
# Get UDP address and role from command line

parser = argparse.ArgumentParser()
parser.add_argument("role", choices=["device", "core", "core-server"])
args = parser.parse_args()

ip_address = ""
role = args.role
if role == "core":
    role = "core-server"

if role == "device":
    udp_src = (ip_address, 33300)
    udp_dst = (ip_address, 33333)
    rule_address = (ip_address, 33300)
else:
    assert role == "core-server"
    udp_src = (ip_address, 33333)
    udp_dst = (ip_address, 33300)
    rule_address = (ip_address, 33300)

# --------------------------------------------------
# Actually run SCHC

rule_manager = gen_rulemanager.RuleManager()
rule_manager.Add(dev_info=rule_set)
rule_manager.Print()


config = {}
upper_layer = UdpUpperLayer()
lower_layer = UdpLowerLayer(udp_src, udp_dst)
system = UdpSystem()
scheduler = system.get_scheduler()
schc_protocol = protocol.SCHCProtocol(
    config, system, layer2=lower_layer, layer3=upper_layer, role=role, unique_peer=True)
schc_protocol.set_rulemanager(rule_manager)

if args.role == "device": # XXX: fix addresses mismatches
    upper_layer.send_later(1, udp_src, coap_ip_packet)

sys.stdout.flush()
scheduler.run()


# --------------------------------------------------
