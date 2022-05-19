"""
compr_parser.py transforms a packet dump into a dictionnary. Dictionnary
format is the following:
{
("field ID", position) : [value, field length in bits, fixed or variable ]
}
since field ID can be repeated, the index is the tuple field ID and position.
"""

from gen_base_import import *
from compr_core import *  # for common variable describing rules (no function called from this module)
from binascii import hexlify, unhexlify
from struct import pack, unpack
import ipaddress
from scapy.all import *


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

icmpv6_types = {
    T_ICMPV6_TYPE_ECHO_REQUEST: 128,
    T_ICMPV6_TYPE_ECHO_REPLY: 129
}

coap_options = {'If-Match':1,
            'Uri-Host':3,
            'ETag':4,
            'If-None-Match':5,
            'Observe':6,
            'Uri-Port':7,
            'Location-Path':8,
            'Uri-Path':11,
            'Content-Format':12,
            'Max-Age':14,
            'Uri-Query':15,
            'Accept':17,
            'Location-Query':20,
            'Block2':23,
            'Block1':27,
            'Size2':28,
            'Proxy-Uri':35,
            'Proxy-Scheme':39,
            'Size1':60}

class Parser:
    """
    Parser takes a bytearray and transforms it into a dictionnay indexed by field id.
    """

    def __init__(self, protocol):
        self.protocol = protocol
        self.header_fields = {}

    def parse(self, pkt, direction, layers=["IPv6", "ICMP", "UDP", "COAP"], start="IPv6"):
        """
        Parsing a byte array:
        - pkt is the bytearray to be parsed
        - direction can be T_DIR_UP or T_DIR_DW
        - layer is a optional argument: 3 means which protocols can be parsed
        - start where to start parsing

        example to start at COAP layer start="COAP"
        to stop before CoAP layers = ["IPv6, "UDP"]
        """

        assert direction in [T_DIR_UP, T_DIR_DW, T_DIR_BI]  # rigth value
        dprint("direction in parser:", direction)

        pos = 0
        self.header_fields = {}

        next_header = start

        if  next_header == "IPv6" :
            version = unpack ("!B", pkt[:1])
            #assert version[0]>>4 == 6                 # only IPv6
            if version[0]>>4 == 6 != 6:
                return None, None, "IP.version != 6"

            #assert len(pkt) >= 40  # IPv6 Header is 40 byte long
            if len(pkt) < 40:
                return None, None, "packet too short"
            firstBytes = unpack('!BBHHBBQQQQ', pkt[:40]) # IPv6 \ UDP \ CoAP header
            #self.protocol._log("compr_parser - firstBytes {}".format(firstBytes))

            #                                         Value           size nature
            self.header_fields[T_IPV6_VER, 1]      = [firstBytes[0] >> 4, 4]
            self.header_fields[T_IPV6_TC, 1]       = [(firstBytes[0] & 0x0F) << 4 | (firstBytes[1] & 0xF0) >> 4, 8]
            self.header_fields[T_IPV6_FL, 1]       = [(firstBytes[1] & 0x0F ) << 16 | firstBytes[2], 20]
            self.header_fields[T_IPV6_LEN, 1]      = [firstBytes[3], 16,  'fixed']
            self.header_fields[T_IPV6_NXT, 1]      = [firstBytes[4], 8,  'fixed']
            self.header_fields[T_IPV6_HOP_LMT, 1]  = [firstBytes[5], 8,  'fixed']

            # The prefix, DEV_PREFIX and APP_PREFIX, should be in bytes
            # to keep its length and to be aligned to the left.
            # This is because it will be used to compare with the one
            # in the src/dst address of IPv6 packet.
            if direction == T_DIR_UP:
                self.header_fields[T_IPV6_DEV_PREFIX, 1]     = [firstBytes[6].to_bytes(8, "big"), 64]
                self.header_fields[T_IPV6_DEV_IID, 1]        = [firstBytes[7].to_bytes(8, "big"), 64]
                self.header_fields[T_IPV6_APP_PREFIX, 1]     = [firstBytes[8].to_bytes(8, "big"), 64]
                self.header_fields[T_IPV6_APP_IID, 1]        = [firstBytes[9].to_bytes(8, "big"), 64]
            elif direction == T_DIR_DW:
                self.header_fields[T_IPV6_APP_PREFIX, 1]     = [firstBytes[6].to_bytes(8, "big"), 64]
                self.header_fields[T_IPV6_APP_IID, 1]        = [firstBytes[7].to_bytes(8, "big"), 64]
                self.header_fields[T_IPV6_DEV_PREFIX, 1]     = [firstBytes[8].to_bytes(8, "big"), 64]
                self.header_fields[T_IPV6_DEV_IID, 1]        = [firstBytes[9].to_bytes(8, "big"), 64]


            if not (self.header_fields[T_IPV6_NXT, 1][0] == 17 or self.header_fields[T_IPV6_NXT, 1][0] == 58):
                return None, None, "packet neither UDP nor ICMP"

            if self.header_fields[T_IPV6_NXT, 1][0] == 17: next_layer = "UDP"
            if self.header_fields[T_IPV6_NXT, 1][0] == 58: next_layer = "ICMP"

            pos = 40 # IPv6 is fully parsed

        if "UDP" in layers and next_layer == "UDP":
            udpBytes = unpack('!HHHH', pkt[pos:pos+8])
            if direction == T_DIR_UP:
                self.header_fields[T_UDP_DEV_PORT, 1]   = [udpBytes[0], 16]
                self.header_fields[T_UDP_APP_PORT, 1]   = [udpBytes[1], 16]
            else:
                self.header_fields[T_UDP_APP_PORT, 1]   = [udpBytes[0], 16]
                self.header_fields[T_UDP_DEV_PORT, 1]   = [udpBytes[1], 16]
            self.header_fields[T_UDP_LEN, 1]            = [udpBytes[2], 16]
            self.header_fields[T_UDP_CKSUM, 1]          = [udpBytes[3], 16]

            pos += 8

            next_layer = "COAP"

        if "ICMP" in layers and next_layer == "ICMP":
            icmpBytes = unpack('!BBH', pkt[pos:pos+4])

            self.header_fields[T_ICMPV6_TYPE, 1]        = [icmpBytes[0], 8]
            self.header_fields[T_ICMPV6_CODE, 1]        = [icmpBytes[1], 8]
            self.header_fields[T_ICMPV6_CKSUM, 1]       = [icmpBytes[2], 16]

            pos += 4
            if icmpBytes[0] == 128 or icmpBytes[0] == 129: #icmp echo request or reply
                echoHeader = unpack('!HH', pkt[pos:pos+4])
                self.header_fields[T_ICMPV6_IDENT, 1]       = [echoHeader[0], 16]
                self.header_fields[T_ICMPV6_SEQNO, 1]        = [echoHeader[1], 16]
                pos += 4


        if "COAP" in layers and next_layer == "COAP":
            field_position = {}
            coapBytes = unpack('!BBH', pkt[pos:pos+4])

            self.header_fields[T_COAP_VERSION, 1]        = [coapBytes[0] >> 6, 2]
            self.header_fields[T_COAP_TYPE, 1]           = [(coapBytes[0] & 0x30) >> 4, 2]
            self.header_fields[T_COAP_TKL, 1]            = [coapBytes[0] & 0x0F, 4]
            self.header_fields[T_COAP_CODE, 1]           = [coapBytes[1], 8]
            self.header_fields[T_COAP_MID, 1]            = [coapBytes[2], 16]

            pos += 4

            token = int(0)
            tkl   = self.header_fields[T_COAP_TKL, 1][0]
            for i in range(0, tkl):
                token <<= 8
                token += int(pkt[pos+i])
                pos += 1

            self.header_fields[T_COAP_TOKEN, 1] = [token, tkl*8]

            option_number = 0
            while (pos < len(pkt)):
                if (int(pkt[pos]) == 0xFF): break

                deltaTL = int(pkt[pos])
                pos += 1

                deltaT = (deltaTL & 0xF0) >> 4
                if deltaT == 13:
                    deltaT = int(pkt[pos]) + 13
                    pos += 1
                
                # /!\ Larger value not implemented

                option_number += int(deltaT)

                L = int(deltaTL & 0x0F)
                if L == 13: 
                    L = int(pkt[pos]) + 13
                    pos += 1
                # /!\ Larger value not implemented

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

                self.header_fields[T_COAP_OPT_END, 1] = [0xFF, 8]
                pos += 1
        return self.header_fields, pkt[pos:], None


class Unparser:

    def _init(self):
        pass

    def unparse (self, header_d, data, direction, d_rule, iface=None):
        #dprint ("unparse: ", header_d, data, direction)

        L2header = None
        L3header = None
        L4header = None
        L7header = None

        c = {}
        for k in [T_IPV6_DEV_PREFIX, T_IPV6_DEV_IID, T_IPV6_APP_PREFIX, T_IPV6_APP_IID]:
            v = header_d[(k, 1)][0]
            if type(v) == bytes:
                c[k] = int.from_bytes(v, "big")
            elif type(v) == int:
                c[k] = v
            else:
                raise ValueError ("Type not supported")

        DevStr = ipaddress.IPv6Address((c[T_IPV6_DEV_PREFIX] <<64) + c[T_IPV6_DEV_IID])
        AppStr = ipaddress.IPv6Address((c[T_IPV6_APP_PREFIX] <<64) + c[T_IPV6_APP_IID])

        IPv6Src = DevStr
        IPv6Dst = AppStr

        IPv6Header = IPv6 (
            version= header_d[(T_IPV6_VER, 1)][0],
            tc     = header_d[(T_IPV6_TC, 1)][0],
            fl     = header_d[(T_IPV6_FL, 1)][0],
            nh     = header_d[(T_IPV6_NXT, 1)][0],
            hlim   = header_d[(T_IPV6_HOP_LMT, 1)][0],
            src    = IPv6Src.compressed, 
            dst    = IPv6Dst.compressed
            ) 

        if header_d[(T_IPV6_NXT, 1)][0] == 58: #IPv6 /  ICMPv6
            for i in icmpv6_types:
                if header_d[('ICMPV6.TYPE', 1)][0] == icmpv6_types[T_ICMPV6_TYPE_ECHO_REPLY]:
                    IPv6Src = DevStr
                    IPv6Dst = AppStr
                    ICMPv6Header = ICMPv6EchoReply(
                        id = header_d[(T_ICMPV6_IDENT, 1)][0],
                        seq =  header_d[(T_ICMPV6_SEQNO, 1)][0],
                        data = data)
                if header_d[('ICMPV6.TYPE', 1)][0] == icmpv6_types[T_ICMPV6_TYPE_ECHO_REQUEST]:
                    IPv6Src = AppStr
                    IPv6Dst = DevStr 
                    ICMPv6Header = ICMPv6EchoRequest(
                        id = header_d[(T_ICMPV6_IDENT, 1)][0],
                        seq =  header_d[(T_ICMPV6_SEQNO, 1)][0],
                        data = data)

            # Put Dev and App accordingly

            IPv6Header = IPv6 (
            version= header_d[(T_IPV6_VER, 1)][0],
            tc     = header_d[(T_IPV6_TC, 1)][0],
            fl     = header_d[(T_IPV6_FL, 1)][0],
            nh     = header_d[(T_IPV6_NXT, 1)][0],
            hlim   = header_d[(T_IPV6_HOP_LMT, 1)][0],
            src    = IPv6Src.compressed, 
            dst    = IPv6Dst.compressed
            ) 

            full_header = IPv6Header/ICMPv6Header

        elif header_d[(T_IPV6_NXT, 1)][0] == 17: # IPv6 / UDP
            UDPHeader = UDP (
                sport = header_d[(T_UDP_DEV_PORT, 1)][0],
                dport = header_d[(T_UDP_APP_PORT, 1)][0]
                )
            if (T_COAP_VERSION, 1) in fields: # IPv6 / UDP / COAP
                print ("CoAP Inside")

                b1 = (header_d[(T_COAP_VERSION, 1)][0] << 6)|(header_d[(T_COAP_TYPE, 1)][0]<<4)|(header_d[(T_COAP_TKL, 1)][0])
                coap_h = struct.pack("!BBH", b1, header_d[(T_COAP_CODE, 1)][0], header_d[(T_COAP_MID, 1)][0])

                tkl = header_d[(T_COAP_TKL, 1)][0]
                if tkl != 0:
                    token = header_d[(T_COAP_TOKEN, 1)][0]
                    for i in range(tkl-1, -1, -1):
                        bt = (token & (0xFF << 8*i)) >> 8*i
                        coap_h += struct.pack("!B", bt)

                delta_t = 0
                comp_rule = header_d[T_COMP] # look into the rule to find options 
                for idx in range(0, len(comp_rule)):
                    if comp_rule[idx][T_FID] == T_COAP_MID:
                        break

                idx += 1 # after MID is there TOKEN
                if idx < len(comp_rule) and comp_rule[idx][T_FID] == T_COAP_TOKEN:
                    print ("skip token")
                    idx += 1

                for idx2 in range (idx, len(comp_rule)):
                    print (comp_rule[idx2])
                    opt_name = comp_rule[idx2][T_FID].replace("COAP.", "")
                
                    delta_t = coap_options[opt_name] - delta_t
                    print (delta_t)

                    if delta_t < 13:
                        dt = delta_t
                    else:
                        dt = 13
                    
                    opt_len = header_d[(comp_rule[idx2][T_FID], comp_rule[idx2][T_FP])][1] // 8
                    opt_val = header_d[(comp_rule[idx2][T_FID], comp_rule[idx2][T_FP])][0]
                    print (opt_len, opt_val)

                    if opt_len < 13:
                        ol = opt_len
                    else:
                        ol = 13
                    
                    coap_h += struct.pack("!B", (dt <<4) | ol)

                    if dt == 13:
                        coap_h += struct.pack("!B", delta_t - 13)

                    if ol == 13:
                        coap_h += struct.pack("!B", opt_len - 13)


                    for i in range (0, opt_len):
                        print (i)
                        if type(opt_val) == str:
                            coap_h += struct.pack("!B", ord(opt_val[i]))
                        elif type(opt_val) == int:
                            v = (opt_val & (0xFF << (opt_len - i - 1))) >> (opt_len - i - 1)
                            coap_h += struct.pack("!B", v)

                if len(data) > 0:
                    coap_h += b'\xff'
                    coap_h += data
                    
                full_header = IPv6Header / UDPHeader / Raw(load=coap_h)
                pass
            else: # IPv6/UDP
                full_header = IPv6Header / UDPHeader / Raw(load=data)
        else: # IPv6 only
            full_header= IPv6Header / Raw(load=data)

        return full_header


