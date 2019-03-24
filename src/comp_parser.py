"""
comp_parser.py transforms a packet dump into a dictionnary. Dictionnary
format is the following:
{
"field ID": [value, position, field length in bits, fixed or variable ]
}
"""

from base_import import *
from schccomp import *  # for common variable describing rules (no function called from this module)
from binascii import hexlify, unhexlify
from struct import pack, unpack

# Layer 3:
#  - IPv6
# Layer 4:
#  - UDP, ICMPv6
# Layer 7:
# - CoAP:



class Parser:
    """
    Parser takes a bytearray and transforms it into a dictionnay indexed by field id.
    """

    def __init__(self, protocol):
        self.protocol = protocol
        self.header_fields = {}

    def parse(self, pkt, direction, layer="IPv6"):
        """
        Parsing a byte array:
        - pkt is the bytearray to be parsed
        - direction can be T_DIR_UP or T_DIR_DW
        - layer is a optional argument: 3 means that parsing must start at ip Layer
        """

        assert (direction == T_DIR_UP) or (direction == T_DIR_DOWN)  # cannot be bidirectionnal

        pos = 0
        self.header_fields = {}

        if layer == "IPv6":
            version = unpack ("!B", pkt[:1])
            assert version[0]>>4 == 6                 # only IPv6

            assert len(pkt) >= 40  # IPv6 Header is 40 byte long
            firstBytes = unpack('!BBHHBBQQQQ', pkt[:40]) # IPv6 \ UDP \ CoAP header
            self.protocol._log(firstBytes)

            #                                         Value           Pos size nature
            self.header_fields[T_IPV6_VER]      = [firstBytes[0] >> 4, 1, 4, 'fixed']
            self.header_fields[T_IPV6_TC]       = [(firstBytes[0] & 0x0F) << 4 | (firstBytes[1] & 0xF0) >> 4, 1, 8, 'fixed']
            self.header_fields[T_IPV6_FL]       = [(firstBytes[1] & 0x0F ) << 16 | firstBytes[2], 1, 20, 'fixed']
            self.header_fields[T_IPV6_LEN]      = [firstBytes[3], 1, 16,  'fixed']
            self.header_fields[T_IPV6_NXT]      = [firstBytes[4], 1, 8,  'fixed']
            self.header_fields[T_IPV6_HOP_LMT]  = [firstBytes[5], 1, 8,  'fixed']

            if direction == T_DIR_UP:
                self.header_fields[T_IPV6_DEV_PREFIX]     = [firstBytes[6], 1, 64, 'fixed']
                self.header_fields[T_IPV6_DEV_IID]        = [firstBytes[7], 1, 64, 'fixed']
                self.header_fields[T_IPV6_APP_PREFIX]     = [firstBytes[8], 1, 64, 'fixed']
                self.header_fields[T_IPV6_APP_IID]        = [firstBytes[9], 1, 64, 'fixed']
            elif direction == T_DIR_DOWN:
                self.header_fields[T_IPV6_APP_PREFIX]     = [firstBytes[6], 1, 64, 'fixed']
                self.header_fields[T_IPV6_APP_IID]        = [firstBytes[7], 1, 64, 'fixed']
                self.header_fields[T_IPV6_DEV_PREFIX]     = [firstBytes[8], 1, 64, 'fixed']
                self.header_fields[T_IPV6_DEV_IID]        = [firstBytes[9], 1, 64, 'fixed']


            assert self.header_fields[T_IPV6_NXT][0] == 17 or self.header_fields[T_IPV6_NXT][0] == 58

            if self.header_fields[T_IPV6_NXT][0] == 17: layer = "udp"
            if self.header_fields[T_IPV6_NXT][0] == 58: layer = "icmp"

            pos = 40 # IPv6 is fully parsed

        if layer == "udp":
            udpBytes = unpack('!HHHH', pkt[pos:pos+8])
            if direction == T_DIR_UP:
                self.header_fields[T_UDP_DEV_PORT]   = [udpBytes[0], 1, 16, 'fixed']
                self.header_fields[T_UDP_APP_PORT]   = [udpBytes[1], 1, 16, 'fixed']
            else:
                self.header_fields[T_UDP_APP_PORT]   = [udpBytes[0], 1, 16, 'fixed']
                self.header_fields[T_UDP_DEV_PORT]   = [udpBytes[1], 1, 16, 'fixed']
            self.header_fields[T_UDP_LEN]            = [udpBytes[2], 1, 16, 'fixed']
            self.header_fields[T_UDP_CKSUM]          = [udpBytes[3], 1, 16, 'fixed']

            pos += 8

            layer = "coap"

        if layer == "icmp":
            icmpBytes = unpack('!HHH', pkt[pos:pos+6])

            self.header_fields[T_ICMPV6_TYPE]        = [icmpBytes[0], 1, 16, 'fixed']
            self.header_fields[T_ICMPV6_CODE]        = [icmpBytes[1], 1, 16, 'fixed']
            self.header_fields[T_ICMPV6_CKSUM]       = [icmpBytes[2], 1, 16, 'fixed']

            pos += 6

        if layer == "coap":
            print ("CoAP")
            coapBytes = unpack('!BBH', pkt[pos:pos+4])



        return self.header_fields, pkt[pos:]
