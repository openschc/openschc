#!/usr/bin/env python3
from scapy.all import *

# rdpcap comes from scapy and loads in our pcap file
packets = rdpcap('trace_coap.pcap')

for packet in packets:
    packet.show()

    hexdump(packet)

    print ("="*40)