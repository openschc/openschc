#!/usr/bin/env python3
from scapy.all import *

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from compr_parser import Parser, Unparser
from gen_parameters import *
from gen_rulemanager import RuleManager
from compr_core import Compressor, Decompressor

import pprint
import binascii

# rdpcap comes from scapy and loads in our pcap file
packets = rdpcap('trace_coap.pcap')

parser = Parser()
Unparser = Unparser()

RM = RuleManager()
RM.Add(file="ipv6-sol.json")
RM.Print()

compress = Compressor()
decompress = Decompressor()

def show_diff(s1, s2):
    from termcolor import colored

    print(s1.decode())
    print(s2.decode())

    if len(s1) != len(s2):
        print("size is different")
        return
    
    for o, c in zip(s1, s2):
        #print(o, c)
        if o == c:
            print(colored(chr(o), "green"), end="")
        else:
            print(colored(chr(o), "red"), end="")   
    print()         

def calculate_checksum(data):
    # Ensure the data length is even
    if len(data) % 2 != 0:
        data += b'\x00'

    # Calculate the checksum
    checksum = 0
    
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word
        print (hex(word), hex(checksum))

    while checksum > 0xFFFF:
        checksum = (checksum >> 16) + (checksum & 0xffff)
        #checksum += checksum >> 16
        print (hex(checksum))

    checksum = ~checksum & 0xffff

    return checksum

# Let's iterate through every packet
for packet in packets:
    #hexdump(packet[IPv6])
    #packet[IPv6].show()

    if packet[Ether].src == "fa:16:3e:1e:cc:2c":
        direction = T_DIR_DW
    elif packet[Ether].dst == "fa:16:3e:1e:cc:2c":
        direction = T_DIR_UP
    else: # skipping
        break

    print ("Packet direction ", direction)

    parsed = parser.parse (bytes(packet[IPv6]), 
                           direction, 
                           layers=["IPv6", "UDP"])
    pprint.pprint (parsed)

    if parsed[0] != None:
        rule = RM.FindRuleFromPacket(pkt=parsed[0], 
                                     direction=direction, 
                                     failed_field=True)
        
        print ("Rule for packet")
        pprint.pprint(rule)

        if rule:
            SCHC_pkt = compress.compress(rule=rule,
                                         parsed_packet=parsed[0],
                                         data= parsed[1],
                                         direction=direction,
                                         verbose=True)
            
            print("SCHC packet in hex")
            SCHC_pkt.display()

            print("SCHC packet in binary")
            SCHC_pkt.display(format="bin")

            field_description = decompress.decompress(rule=rule, schc=SCHC_pkt, direction=direction)
            print(field_description)
            SCHC_pkt.display(format="bin")
            data = SCHC_pkt.get_remaining_content()
            print ("payload:", binascii.hexlify(data))

            pkt = Unparser.unparse(header_d=field_description, data=data, direction=direction)

            show_diff(binascii.hexlify(bytes(packet)[14:]), # remote Ethernet header
                      binascii.hexlify(bytes(pkt)))
                      
            hexdump(pkt)
            print (hex(calculate_checksum(bytes(pkt))))

            hexdump(bytes(packet)[14:])
            print (hex(calculate_checksum(bytes(packet)[14:])))

 

