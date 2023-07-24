#!/usr/bin/env python3
from scapy.all import *

sa = SecurityAssociation(ESP, spi=0xdeadbeef, crypt_algo='AES-CBC',
                         crypt_key=b'sixteenbytes key')

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from compr_parser import Parser, Unparser
from gen_parameters import *
from gen_rulemanager import RuleManager
from compr_core import Compressor, Decompressor
import gen_bitarray

import pprint
import binascii

# rdpcap comes from scapy and loads in our pcap file
packets = rdpcap('trace_coap.pcap')

parser = Parser()
Unparser = Unparser()

RM = RuleManager()
RM.Add(file="ipv6-sol-bi-fl-esp.json")
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

    # do ESP

    ulp = packet[UDP]
    ulp.show()

    ulp_parsed =  parser.parse (bytes(ulp), 
                           direction, 
                           layers=["UDP"],
                           start="UDP")
    
    print (ulp_parsed)

    if ulp_parsed[0] is not None:
        rule_ulp = RM.FindRuleFromPacket(pkt=ulp_parsed[0], 
                                     direction=direction, 
                                     failed_field=True)
        print (rule_ulp)

        if rule_ulp:
            SCHC_pkt = compress.compress(rule=rule_ulp,
                                         parsed_packet=ulp_parsed[0],
                                         data= ulp_parsed[1],
                                         direction=direction,
                                         verbose=True)
            
            SCHC_pkt.display(format="bin")
            SCHC_pkt.display()

            packet[IPv6].nh = 0x5C # SCHC TBD
            packet[IPv6].payload = Raw(SCHC_pkt.get_content())

            packet.show()

    e = sa.encrypt(packet[IPv6])

    e.show()


    parsed = parser.parse (bytes(e[IPv6]), 
                           direction, 
                           layers=["IPv6"])
    pprint.pprint (parsed)


    if parsed[0] != None:
        rule = RM.FindRuleFromPacket(pkt=parsed[0], 
                                     direction=direction, 
                                     failed_field=True)
        
        SCHC_header = {('SCHC.NEXT', 1): [b'\x11', 8]}
        
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


            print ('-'*5,"DECOMPRESSION", '-'*5)

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

            pkt.show()

            # Big Hack
            # esp = bytes(pkt[Raw])
            # pkt[IPv6].payload = ESP(spi= int.from_bytes(esp[0:4], "big"),
            #                        seq=int.from_bytes(esp[4:8], "big"),
            #                        data=esp[8:])
            # pkt[IPv6].plen = len(esp)


            # pkt.show()
            # e.show()

            # d = sa.decrypt(pkt)

            e.show()

            d = sa.decrypt(e)

            d.show()

            if d[IPv6].nh == 0x5C: #SCHC payload
                rSCHC_pkt = bytes(d[Raw])

                print (rSCHC_pkt)

                rSCHC_bbuf = gen_bitarray.BitBuffer(rSCHC_pkt)

                rRule = RM.FindRuleFromSCHCpacket(schc=rSCHC_bbuf)   
                print (rRule)         

                rPacket = decompress.decompress(rule=rRule, schc=rSCHC_bbuf, direction=direction)
                rData = rSCHC_bbuf.get_remaining_content()

                print (rPacket, data)

                      
 

