"""Simple device generating periodically SCHC rules"""

import socket
import select
import struct
import time 
import binascii

socket_port = 8888
tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", socket_port))


ruleID = 100 # CoAP simple message

MID = 1
while True:

    rs = select.select([tunnel], [], [], 30)

    print(rs)
    if rs[0]:
        data, addr = rs[0][0].recvfrom (2000)
        print (binascii.hexlify(data), addr)
        continue

    SCHCmsg = struct.pack("!BB", ruleID, MID) + b'\x00'

    if MID == 255:
        MID = 1
    else:
        MID += 1
    

    tunnel.sendto(SCHCmsg, ("51.91.121.182", 0x5C4C))
    print ("send ", binascii.hexlify(SCHCmsg))


