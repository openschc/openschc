#!/usr/bin/env python3
from scapy.all import *


import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')


import binascii
import typing
import compr_core
import compr_parser
import gen_rulemanager
import gen_bitarray
## import all openschc symbols
from gen_parameters import *

def show( v_name, v ):
  t = type( v )
  if t in [ bytes, bytearray ]:
    v = binascii.hexlify( v, sep=' ' )
  print (f"{v_name} [{type(v)}]: {v}\n---\n")



#type Parsed = tuple[ dict, bytes, None]

class Kompressor:

  def __init__( self, compression_rule_file,\
          direction=T_DIR_DW, 
          verbose=True ):
    self.RM = gen_rulemanager.RuleManager()
    self.RM.Add( file=compression_rule_file )
    self.direction = direction
    self.verbose = True
    self.compressor = compr_core.Compressor()
    self.decompressor = compr_core.Decompressor()
    ## Parser / UnParser are implemneted by openSCHC
    self.parser = compr_parser.Parser()
    self.unparser = compr_parser.Unparser()
    self.next_header = None

#  def parse( self, byte_packet:bytes ) -> Parsed:
  def parse( self, byte_packet:bytes ):
    """ parses the byte packets into SCHC structure

    The SCHC structure is needed to 1) find the rule and 2) 
    build the SCHC packet
    """
    pass

  def schc( self, byte_packet ) -> bytes:

    parsed_packet = self.parse( byte_packet )
    if parsed_packet[0] is None:
      raise ValueError( f"Unexpected parsed_packet[0]: {parsed_packet}")  
      return parsed_packet[1]

    packet_rule = self.RM.FindRuleFromPacket(\
            pkt=parsed_packet[0], # header 
            direction=direction, 
            failed_field=True)
    if not packet_rule:
      raise ValueError( f"Unexpected packet_rule: {packet_rule}")  
      return parsed_packet[1]
    byte_next_header = int.to_bytes( self.next_header, 1, byteorder='big' )  
    parsed_SCHC_hdr = { ("SCHC.NXT", 1): [ byte_next_header, 8] }
    if self.verbose is True:
      show( 'parsed_SCHC_hdr', parsed_SCHC_hdr )
    SCHC_hdr_rule = self.RM.FindRuleFromPacket(
                            pkt=parsed_SCHC_hdr,
                            direction=self.direction,
                            failed_field=True,
                            schc_header=True
    )
    if self.verbose is True:
      show( 'SCHC_hdr_rule', SCHC_hdr_rule )
    ## compressor outputs a an object of type 
    ## gen_bitarray.BitBuffer
    SCHC_hdr = self.compressor.compress(rule=SCHC_hdr_rule,
                                 parsed_packet=parsed_SCHC_hdr,
                                 data=b'',
                                 direction=self.direction,
                                 verbose=True)    
    if self.verbose is True:
      show( 'SCHC_hdr', SCHC_hdr )
    SCHC_packet = self.compressor.compress(rule=packet_rule,
                                 parsed_packet=parsed_packet[0],
                                 data= parsed_packet[1],
                                 direction=self.direction,
                                 verbose=True,
                                 append=SCHC_hdr) # append add to the buffer

    if self.verbose is True:
      show( 'SCHC_packet', SCHC_packet )
    return SCHC_packet.get_content() 
  
  def unschc( self, byte_schc_packet:bytes ):
    schc = gen_bitarray.BitBuffer( byte_schc_packet )
    SCHC_header_rule = self.RM.FindSCHCHeaderRule()
    if self.verbose is True:
      show( f"SCHC_header_rule", SCHC_header_rule )
    SCHC_header = self.decompressor.decompress(rule=SCHC_header_rule, 
            schc=schc, 
            direction=self.direction, 
            schc_header=True)
    show( "SCHC_header", SCHC_header )
    schc_payload = gen_bitarray.BitBuffer( schc.get_remaining_content() )
    if self.verbose is True:
      show( "schc_payload", schc_payload ) # [{type(rData)}]: {rData}" )
    schc_payload_rule = self.RM.FindRuleFromSCHCpacket(schc=schc_payload ) 
    if self.verbose is True:
      show( "schc_payload_rule", schc_payload_rule )         
    payload_fields = self.decompressor.decompress(rule=schc_payload_rule,
            schc=schc_payload, 
            direction=self.direction, schc_header=False)
    if self.verbose is True:
      show( "payload_fields", payload_fields )

    payload = schc_payload.get_remaining_content()
    return self.unparse( payload, payload_fields )

  


class UDPKompressor( Kompressor ):

  def __init__( self, compression_rule_file,\
          direction=T_DIR_DW, 
          verbose=True ):
    super().__init__( compression_rule_file,\
                      direction=T_DIR_DW, 
                      verbose=True )   
    self.next_header = 17 # or \x11

#  def parse( self, byte_packet:bytes ) -> Parsed:
  def parse( self, byte_packet:bytes ) :

    parsed_udp =  self.parser.parse (byte_packet, 
                         self.direction, 
                         layers=["UDP"],
                         start="UDP")
    if self.verbose is True:  
      show( 'parsed_udp', parsed_udp )
    return parsed_udp

  def unparse( self, payload:bytes,  payload_fields:dict )->bytes:
    show( 'unparse-udp', payload )  
    if ('UDP.DEV_PORT', 1) in payload_fields:
      port_src = int.from_bytes( payload_fields[ ('UDP.DEV_PORT', 1) ][0], byteorder="big" )
    else:
      port_src = int.from_bytes( payload[ : 2 ] )
      payload = payload[ 2 : ]
    if ('UDP.APP_PORT', 1) in payload_fields:
      port_dst = int.from_bytes( payload_fields[('UDP.APP_PORT', 1) ][0], byteorder="big" )
    else:
      port_dst = int.from_bytes( payload[ : 2 ] )
      payload = payload[ 2 : ]
    if ('UDP.LEN', 1) in payload_fields:
      udp_len = None  
    else: 
      udp_len = int.from_bytes( payload[ : 2 ] )
      payload = payload[ 2 : ]
        
    if ('UDP.CKSUM', 1) in payload_fields:
      checksum = 0 
    else: 
      checksum = int.from_bytes( payload[ : 2 ] )
      payload = payload[ 2 : ]
              
    udp = bytes( UDP( sport=port_src, 
               dport= port_dst, 
               len=len( payload ) + 8, 
               chksum=0 )/Raw(load=payload) )

    if self.verbose is True:
      show( 'udp', udp )
    return udp


class EncryptedESPKompressor( Kompressor ):
  def __init__( self, compression_rule_file,\
          direction=T_DIR_DW, 
          verbose=True ):
    super().__init__( compression_rule_file,\
                      direction=T_DIR_DW, 
                      verbose=True )  
    self.next_header = 50 # \x32

  def parse( self, byte_packet:bytes ) :
    parsed_esp =  self.parser.parse (byte_packet, 
                         self.direction, 
                         layers=["ESP"],
                         start="ESP")
    if self.verbose is True:  
      show( 'parsed_esp', parsed_esp )
    return parsed_esp

  def unparse( self,payload:bytes,  payload_fields:dict )->bytes:
    if ('ESP.SPI', 1) in payload_fields:
      spi = int.from_bytes( payload_fields[('ESP.SPI', 1)][0], byteorder="big" )
    else: 
      spi = int.from_bytes( payload[ : 4],  "big" )
      payload =  payload[ 4 :]        
    if  ('ESP.SEQ', 1) in payload_fields:
      sn = int.from_bytes( payload_fields[('ESP.SEQ', 1)][0], byteorder="big" )
    else:   
      sn = int.from_bytes( payload[ : 4],  "big" )
#    encrypted_data =  payload[ 4 :]
    esp = bytes( ESP(spi=spi, seq=sn, data=payload ) )
 
    if self.verbose is True:
      show( 'encrypted_esp', esp )

    return esp


UDPK = UDPKompressor( "ipv6-sol-bi-fl-esp-mglt.json" ) 
EESPK = EncryptedESPKompressor( "ipv6-sol-bi-fl-esp-mglt.json" )


## configuring the SA
tunnel_header = IPv6(src='::1', dst='::2')
sa = SecurityAssociation(ESP, spi=5, crypt_algo='AES-CBC',
                         crypt_key=b'sixteenbytes key', 
                         tunnel_header=tunnel_header )

## rdpcap comes from scapy and IP packets from 
## pcap file. These inner IP will be encapsulated 
## with IPsec
packets = rdpcap('trace_coap.pcap')

# Let's iterate through every packet
for sent_inner_packet in packets:

  if sent_inner_packet[Ether].src == "fa:16:3e:1e:cc:2c":
      direction = T_DIR_DW
  elif sent_inner_packet[Ether].dst == "fa:16:3e:1e:cc:2c":
      direction = T_DIR_UP
  else: # skipping
      break

  print("---- Compressing UDP")
  # ulp is a scapy object
  sent_udp = sent_inner_packet[UDP]
  sent_udp.show()
  ## compressing the udp packet
  sent_schc_udp = UDPK.schc( bytes(sent_udp) )
  # updating inner IPv6 packet
  sent_inner_packet[IPv6].nh = 0x5C # SCHC TBD
  sent_inner_packet[IPv6].payload = Raw( sent_schc_udp )
  print ("---- inner IPv6/SCHC")
  sent_inner_packet.show()

  print( "---- Encrypting (IPsec Tunnel mode)" ) 
  ### The IPv6/SCHC packet (or the initial packet ) 
  ## is encrypted and encapsulated in ESP
  ### The ESP Payload in encrypted
  sent_tunnel_ipsec = sa.encrypt( sent_inner_packet[IPv6] )
  sent_tunnel_ipsec.show()
  show( 'esp', bytes( sent_tunnel_ipsec[ ESP ] ) )
  
  ## The current implementation of MO_MSB does not 
  ## scale the TV to the expected number of bytes. 
  ## In other words when b'\x05' is passed it does 
  ## not expand it to b'\x00\x00\x00\x05' so MSB 
  ## can be applied.
  ## One of the issue is that parse was providing 
  ## the smallest numbe rof bytes for a value. This
  ## doe snot seem convenient for MSB rules. As such
  ## we make ESP return bytes. The changes are 
  ## provided in compr_parser.py for ESP only. 

  ## The problem is that JSON does not accept bytes. 
  ## So we need to ensure that when MSB is used.
  ## TV and FV are converted into bytes of the right size. 
  sent_schc_esp = EESPK.schc( bytes( sent_tunnel_ipsec[ESP] ) ) 
  show( 'sent_schc_esp', sent_schc_esp )
  ## Updating tunnel IP header
  sent_tunnel_ipsec[IPv6].nh = 0x5C
  sent_tunnel_ipsec[IPv6].payload = Raw( sent_schc_esp )
  print("Tunnel IP/SCHC(ESP) Packet")
      ## as far as I understand it, the Packet is IPv6/NH
  sent_tunnel_ipsec.show()
  show( 'tunnel_ipsec', bytes( sent_tunnel_ipsec ) )

  print("*****************************")
  print("****** DECOMPRESSION ********")
  print("*****************************")
  ## from the outside the IPv6 contains an SCHC payload
  received_tunnel_ipsec = sent_tunnel_ipsec
  received_tunnel_ipsec.display()

  show( 'tunnel_ipsec[IPv6].plen', received_tunnel_ipsec[IPv6].plen )
  show( 'len( e[IPv6].load )', len( received_tunnel_ipsec[IPv6].payload ) )
  if received_tunnel_ipsec[IPv6].nh == 0x5C: #SCHC payload 92
    bytes_encrypted_esp = EESPK.unschc( bytes( received_tunnel_ipsec[IPv6].payload ) ) 
    show( 'bytes_encrypted_esp', bytes_encrypted_esp )

    ## decompression the IPsec Packet 
    spi = int.from_bytes( bytes_encrypted_esp[ : 4],  "big" )
    sn = int.from_bytes( bytes_encrypted_esp[ : 4],  "big" )
    ## Updating the decompressed packet
    received_tunnel_ipsec[ IPv6 ].payload = ESP( spi=spi, seq=sn, 
                             data=bytes_encrypted_esp[ 8 : ] )
    received_tunnel_ipsec[ IPv6 ].nh = 50
    received_tunnel_ipsec[ IPv6 ].plen = len( bytes_encrypted_esp ) + 8
    print( "display" )    
    received_tunnel_ipsec.display()
    print( "IPsec decapsulation" )
    received_inner_packet = sa.decrypt( received_tunnel_ipsec[ IPv6 ] )
    print("Inner IPv6 Packet" )
    received_inner_packet.show()
    show( 'clear_text_esp', received_inner_packet ) 

  ## checking next header is SCHC
  if received_inner_packet.nh == 0x5c:
    bytes_udp = UDPK.unschc( bytes( received_inner_packet.load ) )
    port_src = int.from_bytes( bytes_udp[ : 2 ], byteorder="big" )
    port_dst = int.from_bytes( bytes_udp[ 2 : 4 ], byteorder="big" )
    udp_len = int.from_bytes( bytes_udp[ 4 : 6 ], byteorder="big" )
    udp_checksum = int.from_bytes( bytes_udp[ 6 : 8 ], byteorder="big" )

    received_udp = UDP( sport=port_src, dport=port_dst, len=udp_len, chksum=udp_checksum )/Raw( load=bytes_udp[8: ])
    received_udp.show()
    show( 'receieved_udp', bytes(received_udp) )
    show( 'received_udp.load', received_udp.load  )
    show( 'sent_udp.load', sent_udp.load  )
    if received_udp.load != sent_udp.load:
      raise ValueError( "ERROR: received_udp.load != sent_udp.load" )    
    else: 
      print( "SUCCESS: received_udp.load == sent_udp.load" )   
