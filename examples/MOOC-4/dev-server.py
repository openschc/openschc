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

    print (ruleID)

    