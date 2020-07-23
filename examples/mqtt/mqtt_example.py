# coding: utf-8
from net_mqtt_core import *
import argparse
from LNS_ttn_v2 import LNS_TTN_V2

# --------------------------------------------------
import gen_utils

gen_utils.set_debug_output(True)

compression_rule = {
    "RuleID": 8,
    "RuleIDLength": 8,
    "Compression": [
        {"FID": "IPV6.VER", "TV": 6, "MO": "equal", "CDA": "not-sent"},
        {"FID": "IPV6.TC", "TV": 0, "MO": "equal", "CDA": "not-sent"},
        {"FID": "IPV6.FL", "TV": 0, "MO": "ignore", "CDA": "not-sent"},
        {"FID": "IPV6.LEN", "MO": "ignore", "CDA": "compute-length"},
        {"FID": "IPV6.NXT", "TV": 17, "MO": "equal", "CDA": "not-sent"},
        {"FID": "IPV6.HOP_LMT", "TV": 255, "MO": "ignore", "CDA": "not-sent"},
        {
            "FID": "IPV6.DEV_PREFIX",
            "TV": "2001:1222:8905:0470::/64",
            "MO": "equal",
            "CDA": "not-sent",
        },
        {"FID": "IPV6.DEV_IID", "TV": "::57", "MO": "equal", "CDA": "not-sent"},
        {
            "FID": "IPV6.APP_PREFIX",
            "TV": "2001:41d0:57d7:3100::/64",
            "MO": "equal",
            "CDA": "not-sent",
        },
        {"FID": "IPV6.APP_IID", "TV": "::0401", "MO": "equal", "CDA": "not-sent"},
        {"FID": "UDP.DEV_PORT", "TV": 5684, "MO": "equal", "CDA": "not-sent"},
        {"FID": "UDP.APP_PORT", "TV": 5683, "MO": "equal", "CDA": "not-sent"},
        {"FID": "UDP.LEN", "TV": 0, "MO": "ignore", "CDA": "compute-length"},
        {"FID": "UDP.CKSUM", "TV": 0, "MO": "ignore", "CDA": "compute-checksum"},
    ],
}

frag_rule_noack = {
    "RuleID": 12,
    "RuleIDLength": 8,
    "Fragmentation": {
        "FRMode": "noAck",
        "FRDirection": "DW",
        "FRModeProfile": {
            "FCNSize": 0,
            "dtagSize": 0,
            "WSize": 0,
            "L2WordSize": 8,
            "windowSize": 0,
        },
    },
}

frag_rule_noack = {
    "RuleID": 12,
    "RuleIDLength": 8,
    "Fragmentation": {"FRMode": "noAck", "FRDirection": "DW", "FRModeProfile": {},},
}

rule_set = [compression_rule.copy(), frag_rule_noack.copy()]

coap_ip_packet = bytearray(
    b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello"""
)

# --------------------------------------------------
# Get UDP address and role from command line

parser = argparse.ArgumentParser()
parser.add_argument("device_id", help="TTN v2 device ID")
args = parser.parse_args()

# --------------------------------------------------
# LoRaWAN/MQTT config
lns = LNS_TTN_V2(
    args.device_id,
    "eu.thethings.network",
    8883,
    "APP ID",
    "APP TOKEN",
    True,
)

# --------------------------------------------------
# Actually run SCHC

rule_manager = gen_rulemanager.RuleManager()
rule_manager.Add(device=args.device_id, dev_info=rule_set)
rule_manager.Print()

config = {}
upper_layer = UdpUpperLayer()
lower_layer = MqttLowerLayer(device_id=args.device_id, lns=lns)
system = MqttSystem()
scheduler = system.get_scheduler()
schc_protocol = protocol.SCHCProtocol(
    config,
    system,
    layer2=lower_layer,
    layer3=upper_layer,
    role="core-server",
    unique_peer=True,
)
schc_protocol.set_rulemanager(rule_manager)

scheduler.run()

# --------------------------------------------------
