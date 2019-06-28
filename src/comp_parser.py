"""
comp_parser.py transforms a packet dump into a dictionnary. Dictionnary
format is the following:
{
("field ID", position) : [value, field length in bits, fixed or variable ]
}
since field ID can be repeated, the index is the tuple field ID and position.
"""

from base_import import *
from schccomp import *  # for common variable describing rules (no function called from this module)
from binascii import hexlify, unhexlify
from struct import pack, unpack

option_names = {
    1: T_COAP_OPT_IF_MATCH,
    3: T_COAP_OPT_URI_HOST,
    4: T_COAP_OPT_ETAG,
    5: T_COAP_OPT_IF_NONE_MATCH,
    6: T_COAP_OPT_OBS,
    7: T_COAP_OPT_URI_PORT,
    8: T_COAP_OPT_URI_PATH,
    11: T_COAP_OPT_URI_PATH,
    12: T_COAP_OPT_CONT_FORMAT,
    14: T_COAP_OPT_MAX_AGE,
    15: T_COAP_OPT_URI_QUERY,
    17: T_COAP_OPT_ACCEPT,
    20: T_COAP_OPT_LOC_QUERY,
    23: T_COAP_OPT_BLOCK2,
    27: T_COAP_OPT_BLOCK1,
    28: T_COAP_OPT_SIZE2,
    35: T_COAP_OPT_PROXY_URI,
    39: T_COAP_OPT_PROXY_SCHEME,
    60: T_COAP_OPT_SIZE1,
    258: T_COAP_OPT_NO_RESP
}


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

        assert direction in [T_DIR_UP, T_DIR_DW, T_DIR_BI]  # rigth value

        pos = 0
        self.header_fields = {}

        if layer == "IPv6":
            version = unpack ("!B", pkt[:1])
            assert version[0]>>4 == 6                 # only IPv6

            assert len(pkt) >= 40  # IPv6 Header is 40 byte long
            firstBytes = unpack('!BBHHBBQQQQ', pkt[:40]) # IPv6 \ UDP \ CoAP header
            self.protocol._log(firstBytes)

            #                                         Value           size nature
            self.header_fields[T_IPV6_VER, 1]      = [firstBytes[0] >> 4, 4, 'fixed']
            self.header_fields[T_IPV6_TC, 1]       = [(firstBytes[0] & 0x0F) << 4 | (firstBytes[1] & 0xF0) >> 4, 8, 'fixed']
            self.header_fields[T_IPV6_FL, 1]       = [(firstBytes[1] & 0x0F ) << 16 | firstBytes[2], 20, 'fixed']
            self.header_fields[T_IPV6_LEN, 1]      = [firstBytes[3], 16,  'fixed']
            self.header_fields[T_IPV6_NXT, 1]      = [firstBytes[4], 8,  'fixed']
            self.header_fields[T_IPV6_HOP_LMT, 1]  = [firstBytes[5], 8,  'fixed']

            if direction == T_DIR_UP:
                self.header_fields[T_IPV6_DEV_PREFIX, 1]     = [firstBytes[6].to_bytes(8, "big"), 64, 'fixed']
                self.header_fields[T_IPV6_DEV_IID, 1]        = [firstBytes[7].to_bytes(8, "big"), 64, 'fixed']
                self.header_fields[T_IPV6_APP_PREFIX, 1]     = [firstBytes[8].to_bytes(8, "big"), 64, 'fixed']
                self.header_fields[T_IPV6_APP_IID, 1]        = [firstBytes[9].to_bytes(8, "big"), 64, 'fixed']
            elif direction == T_DIR_DW:
                self.header_fields[T_IPV6_APP_PREFIX, 1]     = [firstBytes[6], 64, 'fixed']
                self.header_fields[T_IPV6_APP_IID, 1]        = [firstBytes[7], 64, 'fixed']
                self.header_fields[T_IPV6_DEV_PREFIX, 1]     = [firstBytes[8], 64, 'fixed']
                self.header_fields[T_IPV6_DEV_IID, 1]        = [firstBytes[9], 64, 'fixed']


            assert self.header_fields[T_IPV6_NXT, 1][0] == 17 or self.header_fields[T_IPV6_NXT, 1][0] == 58

            if self.header_fields[T_IPV6_NXT, 1][0] == 17: layer = "udp"
            if self.header_fields[T_IPV6_NXT, 1][0] == 58: layer = "icmp"

            pos = 40 # IPv6 is fully parsed

        if layer == "udp":
            udpBytes = unpack('!HHHH', pkt[pos:pos+8])
            if direction == T_DIR_UP:
                self.header_fields[T_UDP_DEV_PORT, 1]   = [udpBytes[0], 16, 'fixed']
                self.header_fields[T_UDP_APP_PORT, 1]   = [udpBytes[1], 16, 'fixed']
            else:
                self.header_fields[T_UDP_APP_PORT, 1]   = [udpBytes[0], 16, 'fixed']
                self.header_fields[T_UDP_DEV_PORT, 1]   = [udpBytes[1], 16, 'fixed']
            self.header_fields[T_UDP_LEN, 1]            = [udpBytes[2], 16, 'fixed']
            self.header_fields[T_UDP_CKSUM, 1]          = [udpBytes[3], 16, 'fixed']

            pos += 8

            layer = "coap"

        if layer == "icmp":
            icmpBytes = unpack('!HHH', pkt[pos:pos+6])

            self.header_fields[T_ICMPV6_TYPE, 1]        = [icmpBytes[0], 16, 'fixed']
            self.header_fields[T_ICMPV6_CODE, 1]        = [icmpBytes[1], 16, 'fixed']
            self.header_fields[T_ICMPV6_CKSUM, 1]       = [icmpBytes[2], 16, 'fixed']

            pos += 6

        if layer == "coap":
            field_position = {}
            coapBytes = unpack('!BBH', pkt[pos:pos+4])

            self.header_fields[T_COAP_VERSION, 1]        = [coapBytes[0] >> 6, 2, 'fixed']
            self.header_fields[T_COAP_TYPE, 1]           = [(coapBytes[0] & 0x30) >> 4, 2, 'fixed']
            self.header_fields[T_COAP_TKL, 1]            = [coapBytes[0] & 0x0F, 4, 'fixed']
            self.header_fields[T_COAP_CODE, 1]           = [coapBytes[1], 8, 'fixed']
            self.header_fields[T_COAP_MID, 1]            = [coapBytes[2], 16, 'fixed']

            pos += 4

            token = int(0)
            tkl   = self.header_fields[T_COAP_TKL, 1][0]
            for i in range(0, tkl):
                token <<= 8
                token += int(pkt[pos+i])
                pos += 1

            self.header_fields[T_COAP_TOKEN, 1] = [token, tkl*8, 'fixed']

            option_number = 0
            while (pos < len(pkt)):
                if (int(pkt[pos]) == 0xFF): break

                deltaTL = int(pkt[pos])
                pos += 1

                deltaT = (deltaTL & 0xF0) >> 4
                # /!\ add long value
                option_number += int(deltaT)

                L = int(deltaTL & 0x0F)
                # /!\ add long values

                # create a field_position counter if a field is repeated in the header
                try:
                    field_position[option_number] += 1
                except:
                    field_position[option_number] = 1

                option_value = ''

                for i in range (0, L):
                    option_value += chr(pkt[pos])
                    pos += 1
                    # /!\ check if max length is reached

                try:
                    self.header_fields[option_names[option_number], field_position[option_number]] = [option_value, L*8,  "variable"]
                except:
                    raise ValueError("CoAP Option {} not found".format(option_number))

            if(pos < len(pkt)):
                assert int(pkt[pos]) == 0xFF # if data reamins, an 0xFF must be present

                self.header_fields[T_COAP_OPT_END, 1] = [0xFF, 8, 'fixed']
                pos += 1


        return self.header_fields, pkt[pos:]
