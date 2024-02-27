from re import A
import socket
import binascii

import sys
import tokenize
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

import gen_bitarray as ba

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(('0.0.0.0', 8888))

while True:
    data, addr = tunnel.recvfrom(1500)
    print (binascii.hexlify(data))

    schc_msg = ba.BitBuffer(data)

    schc_msg.display(format="bin")

    ruleID=schc_msg.get_bits(3)

    if ruleID == 1: # rule 1/3
        app_port = schc_msg.get_bits(16)
        mid = schc_msg.get_bits(16)
        token = schc_msg.get_bits(16)
        uri_idx = schc_msg.get_bits(2)

        uri = ["temp", "humi", "pres", None][uri_idx]

        print(app_port, mid, token, uri_idx, uri)
        if uri == "temp":
            pass
        else:
            schc_resp = ba.BitBuffer()
            schc_resp.add_bits(0b0000_0001, nb_bits=3) # ruleID
            schc_resp.display(format="bin")

            schc_resp.add_bits(app_port, nb_bits=16) # app port
            schc_resp.display(format="bin")

            schc_resp.add_bits(mid, nb_bits=16) # Message ID
            schc_resp.display(format="bin")

            schc_resp.add_bits(tokenize, nb_bits=16) # Token
            schc_resp.display(format="bin")


