import socket
import cbor2 as cbor
import random
import time
import struct
import binascii

CORE_SCHC = ("10.0.0.21", 0x5C4C)
MID_LENGTH=3
KNOWN_URI = ["/temp", "/humi", "/pres"]

MID = 1

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", 8888))

def coap_send_measurement(value, uri):
    global MID

    if uri not in KNOWN_URI:
        print("unknown URI")
        return None
    
    if type(value) is not bytes: # not cbor
        value = cbor.dumps(value)

    uri_idx = KNOWN_URI.index(uri)
    print ("MID", MID, "URI", uri, "(index:", uri_idx, ")", "value", binascii.hexlify(value) )

    schc_residue = (0x00 & 0b0000_0111) << 5 | \
                   (MID & 0b0000_0111) << 2 | \
                   (uri_idx) & 0b0000_0011
    
    if MID == 0b0000_0111:
        MID = 1
    else:
        MID += 1
    
    schc_pkt = struct.pack("!B", schc_residue) + value
    print (binascii.hexlify(schc_pkt))
    tunnel.sendto(schc_pkt, CORE_SCHC)

temp = humi = pres = 0

while True:
    m = random.randint(0,2)
    if m == 0:
        temp += random.randint (-5, +5)
        coap_send_measurement(temp, "/temp")
    elif m == 1:
        humi += random.randint (-10, +10)
        coap_send_measurement(humi, "/humi")
    elif m == 2:
        pres += random.randint (-10, +10)
        coap_send_measurement(pres, "/pres")

    time.sleep(random.randint(1, 7))
