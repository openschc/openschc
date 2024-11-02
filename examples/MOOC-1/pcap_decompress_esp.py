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

# Load the rules containing the compression and the schc_header
RM = RuleManager()
RM.Add(file="ipv6-sol-bi-fl-esp.json")
RM.Print()

compress = Compressor()
decompress = Decompressor()


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

    # take UDP abd parse it
    ulp = packet[UDP]
    ulp.show()

    ulp_parsed =  parser.parse (bytes(ulp), 
                           direction, 
                           layers=["UDP"],
                           start="UDP")
    
    print (f"uld_parsed: {ulp_parsed}")
    print( "---" )
    if ulp_parsed[0] is not None:
        # packet parsed, find a matching rule.
        rule_ulp = RM.FindRuleFromPacket(pkt=ulp_parsed[0], 
                                     direction=direction, 
                                     failed_field=True)
        print ("Compression rule for UDP")
        print (rule_ulp)
        print( "---" )

        if rule_ulp:
### strat testinf udp compression
#            test_udp_pkt = compress.compress(rule=rule_ulp,
#                                         parsed_packet=ulp_parsed[0],
#                                         data= ulp_parsed[1],
#                                         direction=direction,
#                                         )
#            print( f"Printing UDP without SCHC" ) 
#            tt = "0140dc9a100cf751f5b9e3ab9b2b91730b1b5b61734b7c23a34b6b28/221"
#            print( test_udp_pkt.display() )
#            print( test_udp_pkt.display() == tt )
#            print ( tt )
#            print( "---" )
## stop testing udp compression

#                                         verbose=True,
#                                         append=SCHC_header) # append add to the buffer

            # matching rule found

            # form the SCHC pseudo header and compress it 

            pseudo_SCHC_header = {
                ("SCHC.NXT", 1): [b"\x11", 8] # [FieldID, Field Pos] : [value, size]
            }

            print("Looking for SCHC Header rule...")
            SCHC_header_rule = RM.FindRuleFromPacket(
                                    pkt=pseudo_SCHC_header,
                                    direction=direction,
                                    failed_field=True,
                                    schc_header=True
            )

            print("SCHC Header rule")
            print (SCHC_header_rule)
            print( "---" )

            print("Compress SCHC Header")
            SCHC_header = compress.compress(rule=SCHC_header_rule,
                                         parsed_packet=pseudo_SCHC_header,
                                         data=b'',
                                         direction=direction,
                                         verbose=True)    

            SCHC_pkt = compress.compress(rule=rule_ulp,
                                         parsed_packet=ulp_parsed[0],
                                         data= ulp_parsed[1],
                                         direction=direction,
                                         verbose=True,
                                         append=SCHC_header) # append add to the buffer
            
            print("Full compressed SCHC message:")
            SCHC_pkt.display(format="bin")
            print( "---" )
            SCHC_pkt.display()
            print( "---" )
            print( SCHC_pkt.get_content() )
            print( "===" )

            # Create IPv6 packet with SCHC protocol IPv6|SCHC

            packet[IPv6].nh = 0x5C # SCHC TBD
            packet[IPv6].payload = Raw(SCHC_pkt.get_content())

            print ("IPv6 containing SCHC")
            packet.show()

            # DO IPSEC
            e = sa.encrypt(packet[IPv6])
            print ("IPsec packet")
            e.show()

            # Find rule for outer ESP header
            esp_parsed =  parser.parse (bytes(e[ESP]), 
                        direction, 
                        layers=["ESP"],
                        start="ESP")
            print("Parsed ESP Header")
            print(esp_parsed)

            pseudo_SCHC_header = {
                ("SCHC.NXT", 1): [b"\x32", 8] # [FieldID, Field Pos] : [value, size]
            }    

            print("Looking for outer SCHC Header rule...")
            SCHC_header_rule = RM.FindRuleFromPacket(
                                    pkt=pseudo_SCHC_header,
                                    direction=direction,
                                    failed_field=True,
                                    schc_header=True
            )

            print("Outer SCHC Header rule")
            print (SCHC_header_rule)
  

            print("Compress SCHC Header")
            SCHC_header = compress.compress(rule=SCHC_header_rule,
                                         parsed_packet=pseudo_SCHC_header,
                                         data=b'',
                                         direction=direction,
                                         verbose=True)  
            
            print ("OUTER SCHC Header")
            SCHC_header.display(format="bin")

            compress.compress(rule=rule_ulp,
                                         parsed_packet=esp_parsed[0],
                                         data= esp_parsed[1],
                                         direction=direction,
                                         verbose=True,
                                         append=SCHC_header) # append add to the buffer                    

            print ("Compressed Outer Header")
            SCHC_header.display()

            e[IPv6].nh = 0x5C
            e[IPv6].payload = Raw(SCHC_header.get_content())

            print("Full compressed SCHC packet")
            e.show()
            hexdump(e)

            print("*****************************")
            print("****** DECOMPRESSION ********")
            print("*****************************")

            payload = e[Raw]
            print ("Received SCHC packet:", binascii.hexlify(bytes(payload)))
            
            rec_bbuf = gen_bitarray.BitBuffer(bytes(payload))

            SCHC_header_used = RM.FindSCHCHeaderRule()

            if SCHC_header_rule is not None:
                print("Sender added SCHC header")

            print( f"SCHC_pkt" )
            SCHC_header = decompress.decompress(rule=SCHC_header_rule,
                                                schc=SCHC_pkt, 
                                                direction=direction,
                                                schc_header=True)
            print ("SCHC Header")
            print (SCHC_header)

            ruleID = RM.FindRuleFromSCHCpacket(SCHC_pkt)
            print ("Outer Rule ID", ruleID)

            SCHC_packet = decompress.decompress(rule=ruleID,
                                                schc=SCHC_pkt, 
                                                direction=direction)
            
            print ("SCHC Packet")
            print(SCHC_packet)

            # replace SCHC proto by the one in the SCHC Header
            e[IPv6].nh = int.from_bytes(SCHC_header[('SCHC.NXT', 1)][0], "big")
            e[IPv6].show()

    0/0
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

                      
 

