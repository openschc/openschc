from scapy.all import *

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from compr_parser import Parser
from gen_parameters import *

import pprint
import binascii

# rdpcap comes from scapy and loads in our pcap file
packets = rdpcap('trace_coap.pcap')

parser = Parser()

# Let's iterate through every packet
for packet in packets:
    packet.show()

    if packet[Ether].src == "fa:16:3e:1e:cc:2c":
        direction = T_DIR_UP
    else:
        direction = T_DIR_DW

    print (binascii.hexlify(bytes(packet[IPv6])))
    parsed = parser.parse (bytes(packet[IPv6]), direction, layers=["IPv6", "UDP"])
    pprint.pprint (parsed)

