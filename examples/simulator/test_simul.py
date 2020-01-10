"""
An example of simulation using only basic rules
"""

# ---------------------------------------------------------------------------

import net_sim_builder

# --------------------------------------------------
# Rule as in documentation

compression_rule = {
    "RuleID": 12,
    "RuleIDLength": 4,
    "Compression": []
}

frag_rule_noack = {
    "RuleID" : 12,
    "RuleIDLength" : 6,
    "Fragmentation" : {
        "FRMode": "noAck"
    }
}
# ---------------------------------------------------------------------------

gateway_rules = [compression_rule.copy(), frag_rule_noack.copy()]
device_rules = [compression_rule.copy(), frag_rule_noack.copy()]

# --------------------------------------------------
# Message

coap_ip_packet = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

# ---------------------------------------------------------------------------

builder = net_sim_builder.SimulBuilder()
builder.create_device(device_rules)
builder.create_gateway(gateway_rules)
#helper.set_config(net_sim_helper.DEFAULT_SIMUL_CONFIG, net_sim_helper.DEFAULT_LOSS_CONFIG)
builder.create_simul()

# ---------------------------------------------------------------------------
# Simnulation

builder.make_device_send_data(clock=1, packet=coap_ip_packet)
builder.run_simul()

# ---------------------------------------------------------------------------
