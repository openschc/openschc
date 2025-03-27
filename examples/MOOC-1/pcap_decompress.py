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
absolutePath = "/home/vicharak/projects/openschc/examples/MOOC-1/"

packets = rdpcap(absolutePath + 'trace_coap.pcap')

parser = Parser()
Unparser = Unparser()

RM = RuleManager()
RM.Add(file= absolutePath + "ipv6-sol-bi-fl.json")
RM.Print()

compress = Compressor()
decompress = Decompressor()

def show_diff(s1, s2):
    from termcolor import colored

    if len(s1) != len(s2):
        print("size is different")
        return
    
    differ = False
    for o, c in zip(s1, s2):
        #print(o, c)
        if o == c:
            print(colored(chr(o), "green"), end="")
        else:
            print(colored(chr(o), "red"), end="")  
            differ = True 
    print()         
    if differ:
        print (s2.decode()) 


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

            field_description = decompress.decompress(rule=rule, 
                                                  schc=SCHC_pkt, 
                                                direction=direction)
            print(field_description)
            SCHC_pkt.display(format="bin")
            data = SCHC_pkt.get_remaining_content()
            print ("payload:", binascii.hexlify(data))

            pkt = Unparser.unparse(header_d=field_description, 
                                   data=data, 
                                   direction=direction)

            show_diff(binascii.hexlify(bytes(packet)[14:]), 
                      binascii.hexlify(bytes(pkt)))
                      
 

