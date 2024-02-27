from re import A
import socket
import binascii

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

import gen_bitarray as ba

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(('0.0.0.0', 8888))

while True:
    data, addr = tunnel.recvfrom(1500)
    print (binascii.hexlify(data))

    schc_msg = ba.BitBuffer(data)
    ruleID=schc_msg.get_bits(3)

    if ruleID == 1: # rule 1/3
        app_port = schc_msg.get_bits(16)
        mid = schc_msg.get_bits(16)
        token = schc_msg.get_bits(16)
        uri_idx = schc_msg.get_bits(2)

        uri = ["temp", "humi", "pres", None][uri_idx]

        print(app_port, mid, token, uri_idx, uri)

