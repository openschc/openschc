"""
compr_parser.py transforms a packet dump into a dictionnary. Dictionnary
format is the following:
{
("field ID", position) : [value, field length in bits, fixed or variable ]
}
since field ID can be repeated, the index is the tuple field ID and position.
"""

from gen_base_import import *
from gen_parameters import *  
from gen_utils import *
from binascii import hexlify, unhexlify
from struct import pack, unpack
import ipaddress
from scapy.all import *
import binascii


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

coap_options = {value: key for key, value in option_names.items()}

icmpv6_types = {
    T_ICMPV6_TYPE_ECHO_REQUEST: 128,
    T_ICMPV6_TYPE_ECHO_REPLY: 129
}

class Parser:
    """
    Parser takes a bytearray and transforms it into a dictionary indexed by field id.
    """

    def __init__(self, protocol=None):
        self.protocol = protocol
        self.header_fields = {}

    def parse(self, pkt, direction, layers=["IPv6", "ICMP", "UDP", "CoAP"], 
              coap_port = 5683,
              start="IPv6"):
        """
        Parsing a byte array:
        - pkt is the bytearray to be parsed
        - direction can be T_DIR_UP or T_DIR_DW
        - layer is a optional argument: 3 means which protocols can be parsed
        - start where to start parsing
        example to start at COAP layer start="COAP"
        to stop before CoAP layers = ["IPv6, "UDP"]
        """

        assert direction in [T_DIR_UP, T_DIR_DW]  # rigth value
        #dprint("direction in parser:", direction)

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
            self.header_fields[T_IPV6_VER, 1]      = [adapt_value(firstBytes[0] >> 4), 4]
            self.header_fields[T_IPV6_TC, 1]       = [adapt_value((firstBytes[0] & 0x0F) << 4 | (firstBytes[1] & 0xF0) >> 4), 
                                                      8]
            self.header_fields[T_IPV6_FL, 1]       = [adapt_value((firstBytes[1] & 0x0F ) << 16 | firstBytes[2]),
                                                      20]
            self.header_fields[T_IPV6_LEN, 1]      = [adapt_value(firstBytes[3]), 16,  'fixed']
            self.header_fields[T_IPV6_NXT, 1]      = [adapt_value(firstBytes[4]), 8,  'fixed']
            self.header_fields[T_IPV6_HOP_LMT, 1]  = [adapt_value(firstBytes[5]), 8,  'fixed']

            # The prefix, DEV_PREFIX and APP_PREFIX, should be in bytes
            # to keep its length and to be aligned to the left.
            # This is because it will be used to compare with the one
            # in the src/dst address of IPv6 packet.
            if direction == T_DIR_UP:
                self.header_fields[T_IPV6_DEV_PREFIX, 1]     = [adapt_value(firstBytes[6].to_bytes(8, "big"), 64, T_IPV6_DEV_PREFIX), 64]
                self.header_fields[T_IPV6_DEV_IID, 1]        = [adapt_value(firstBytes[7].to_bytes(8, "big"), 64, T_IPV6_DEV_IID), 64]
                self.header_fields[T_IPV6_APP_PREFIX, 1]     = [adapt_value(firstBytes[8].to_bytes(8, "big"), 64, T_IPV6_APP_PREFIX), 64]
                self.header_fields[T_IPV6_APP_IID, 1]        = [adapt_value(firstBytes[9].to_bytes(8, "big"), 64, T_IPV6_APP_IID,), 64]
            elif direction == T_DIR_DW:
                self.header_fields[T_IPV6_APP_PREFIX, 1]     = [adapt_value(firstBytes[6].to_bytes(8, "big"), 64, T_IPV6_APP_PREFIX), 64]
                self.header_fields[T_IPV6_APP_IID, 1]        = [adapt_value(firstBytes[7].to_bytes(8, "big"), 64, T_IPV6_APP_IID), 64]
                self.header_fields[T_IPV6_DEV_PREFIX, 1]     = [adapt_value(firstBytes[8].to_bytes(8, "big"), 64, T_IPV6_DEV_PREFIX), 64]
                self.header_fields[T_IPV6_DEV_IID, 1]        = [adapt_value(firstBytes[9].to_bytes(8, "big"), 64, T_IPV6_DEV_IID), 64]


            if not (self.header_fields[T_IPV6_NXT, 1][0] == b'\x11' or self.header_fields[T_IPV6_NXT, 1][0] == b'\x3a'):
                return None, None, "packet neither UDP nor ICMP"

            if self.header_fields[T_IPV6_NXT, 1][0] == b'\x11': next_layer = "UDP"
            if self.header_fields[T_IPV6_NXT, 1][0] == b'\x3a': next_layer = "ICMP"

            pos = 40 # IPv6 is fully parsed

        if "UDP" in layers and next_layer == "UDP":
            udpBytes = unpack('!HHHH', pkt[pos:pos+8])
            if direction == T_DIR_UP:
                self.header_fields[T_UDP_DEV_PORT, 1]   = [adapt_value(udpBytes[0]), 16]
                self.header_fields[T_UDP_APP_PORT, 1]   = [adapt_value(udpBytes[1]), 16]
            else:
                self.header_fields[T_UDP_APP_PORT, 1]   = [adapt_value(udpBytes[0]), 16]
                self.header_fields[T_UDP_DEV_PORT, 1]   = [adapt_value(udpBytes[1]), 16]
            self.header_fields[T_UDP_LEN, 1]            = [adapt_value(udpBytes[2]), 16]
            self.header_fields[T_UDP_CKSUM, 1]          = [adapt_value(udpBytes[3]), 16]

            pos += 8

            if udpBytes[0] == coap_port or udpBytes[1] == coap_port:
                next_layer = "CoAP"

        if "ICMP" in layers and next_layer == "ICMP":
            icmpBytes = unpack('!BBH', pkt[pos:pos+4])

            self.header_fields[T_ICMPV6_TYPE, 1]        = [adapt_value(icmpBytes[0]), 8]
            self.header_fields[T_ICMPV6_CODE, 1]        = [adapt_value(icmpBytes[1]), 8]
            self.header_fields[T_ICMPV6_CKSUM, 1]       = [adapt_value(icmpBytes[2]), 16]

            pos += 4
            if icmpBytes[0] == 128 or icmpBytes[0] == 129: #icmp echo request or reply
                echoHeader = unpack('!HH', pkt[pos:pos+4])
                self.header_fields[T_ICMPV6_IDENT, 1]       = [adapt_value(echoHeader[0]), 16]
                self.header_fields[T_ICMPV6_SEQNO, 1]       = [adapt_value(echoHeader[1]), 16]
                pos += 4
            elif icmpBytes[0] == 1: # Destination Unreachable
                unused = unpack('!L', pkt[pos:pos+4])
                self.header_fields[T_ICMPV6_UNUSED, 1]       = [adapt_value(unused[0]), 32]
                pos += 4

            if True:  # current draft propose to parse even the payload for all ICMPv6 packets
                self.header_fields[T_ICMPV6_PAYLOAD, 1]       = [adapt_value(pkt[pos:]), (len(pkt)- pos)*8]
                pos = len(pkt)

                
        if "CoAP" in layers and next_layer == "CoAP":
            field_position = {}
            coapBytes = unpack('!BBH', pkt[pos:pos+4])

            self.header_fields[T_COAP_VERSION, 1]        = [adapt_value(coapBytes[0] >> 6), 2]
            self.header_fields[T_COAP_TYPE, 1]           = [adapt_value((coapBytes[0] & 0x30) >> 4), 2]
            self.header_fields[T_COAP_TKL, 1]            = [adapt_value(coapBytes[0] & 0x0F), 4]
            self.header_fields[T_COAP_CODE, 1]           = [adapt_value(coapBytes[1]), 8]
            self.header_fields[T_COAP_MID, 1]            = [adapt_value(coapBytes[2]), 16]

            pos += 4

            token = b''
            tkl   = int.from_bytes(self.header_fields[T_COAP_TKL, 1][0], "big")
            for i in range(0, tkl):
                token += pkt[pos].to_bytes(1, 'big')
                pos += 1

            if token != b'':
                self.header_fields[T_COAP_TOKEN, 1] = [adapt_value(token), tkl*8]

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
                if option_number in field_position:
                    field_position[option_number] += 1
                else:
                    field_position[option_number] = 1

                option_value = bytearray()

                for i in range (0, L):
                    option_value.append(pkt[pos])
                    pos += 1
                    # /!\ check if max length is reached

                try:
                    self.header_fields[option_names[option_number], field_position[option_number]] = [bytes(option_value), L*8,  "variable"]
                except:
                    print (binascii.hexlify(pkt))
                    print ("position:", pos)
                    print (self.header_fields)
                    raise ValueError("CoAP Option {} not found".format(option_number))

            if(pos < len(pkt)):
                assert int(pkt[pos]) == 0xFF # if data reamins, an 0xFF must be present

                #self.header_fields[T_COAP_OPT_END, 1] = [0xFF, 8]
                pos += 1
        return self.header_fields, pkt[pos:], None


class Unparser:

    def _init(self):
        pass

    def unparse (self, header_d, data, direction, d_rule=None, iface=None, verbose=False):
        #dprint ("unparse: ", header_d, data, direction)

        L2header = None
        L3header = None
        L4header = None
        L7header = None
        coap_h   = None

        if (T_IPV6_VER, 1) in header_d: # doing IPv6 and UDP

            c = {}
            for k in [T_IPV6_DEV_PREFIX, T_IPV6_DEV_IID, T_IPV6_APP_PREFIX, T_IPV6_APP_IID]:
                v = header_d[(k, 1)][0]
                if type(v) == bytes:
                    c[k] = int.from_bytes(v, "big")
                elif type(v) == int:
                    c[k] = v
                else:
                    raise ValueError ("Type  {} not supported".format(type(v)))

            DevStr = ipaddress.IPv6Address((c[T_IPV6_DEV_PREFIX] <<64) + c[T_IPV6_DEV_IID])
            AppStr = ipaddress.IPv6Address((c[T_IPV6_APP_PREFIX] <<64) + c[T_IPV6_APP_IID])
            
            if direction == T_DIR_UP:
                IPv6Src = DevStr
                IPv6Dst = AppStr
            else:
                IPv6Dst = DevStr
                IPv6Src = AppStr                

            IPv6Header = IPv6 (
                version= int.from_bytes(header_d[(T_IPV6_VER, 1)][0], byteorder="big" ),
                tc     = int.from_bytes(header_d[(T_IPV6_TC, 1)][0], byteorder="big" ),
                fl     = int.from_bytes(header_d[(T_IPV6_FL, 1)][0], byteorder="big" ),
                nh     = int.from_bytes(header_d[(T_IPV6_NXT, 1)][0], byteorder="big" ),
                hlim   = int.from_bytes(header_d[(T_IPV6_HOP_LMT, 1)][0], byteorder="big" ),
                src    = IPv6Src.compressed, 
                dst    = IPv6Dst.compressed
            ) 

            L3header = IPv6Header  

            ipv6_next = int.from_bytes(header_d[(T_IPV6_NXT, 1)][0], byteorder="big" )

            if ipv6_next == 58 and (T_ICMPV6_TYPE, 1) in header_d: #IPv6 /  ICMPv6
                icmp_type = int.from_bytes(header_d[(T_ICMPV6_TYPE, 1)][0], byteorder="big" )

                if icmp_type == 129: #icmpv6_types[T_ICMPV6_TYPE_ECHO_REPLY]:
                    IPv6Src = DevStr
                    IPv6Dst = AppStr
                    ICMPv6Header = ICMPv6EchoReply(
                        id =  int.from_bytes(header_d[(T_ICMPV6_IDENT, 1)][0], byteorder="big" ),
                        seq =   int.from_bytes(header_d[(T_ICMPV6_SEQNO, 1)][0], byteorder="big" ),
                        data = header_d[(T_ICMPV6_PAYLOAD, 1)][0])
                elif icmp_type == 128: #icmpv6_types[T_ICMPV6_TYPE_ECHO_REQUEST]:
                    IPv6Src = AppStr
                    IPv6Dst = DevStr 
                    ICMPv6Header = ICMPv6EchoRequest(
                        id =  int.from_bytes(header_d[(T_ICMPV6_IDENT, 1)][0], byteorder="big" ),
                        seq =   int.from_bytes(header_d[(T_ICMPV6_SEQNO, 1)][0], byteorder="big" ),
                        data = header_d[(T_ICMPV6_PAYLOAD, 1)][0])
                else:
                    print ("ICMPv6 not covered")
                    ICMPv6Header = None

                L4header = ICMPv6Header

            elif ipv6_next == 17: # UDP
                dev_port = header_d[(T_UDP_DEV_PORT, 1)][0]
                app_port = header_d[(T_UDP_APP_PORT, 1)][0]                    

                if type(dev_port) == bytes:
                    dev_port = int.from_bytes(dev_port,"big")
                if type(app_port) == bytes:
                    app_port = int.from_bytes(app_port,"big")
                if direction == T_DIR_UP:    
                    L4header = UDP (sport=dev_port, dport=app_port)
                else:
                    L4header = UDP (dport=dev_port, sport=app_port)
#            else:
#                raise ValueError("TBD")

            if (T_COAP_VERSION, 1) in header_d: # IPv6 / UDP / COAP
                #print ("CoAP Inside")

                coap_ver  = int.from_bytes(header_d[(T_COAP_VERSION, 1)][0], byteorder="big" )
                coap_type = int.from_bytes(header_d[(T_COAP_TYPE, 1)][0], byteorder="big" )
                coap_tlk  = int.from_bytes(header_d[(T_COAP_TKL, 1)][0], byteorder="big" )
                coap_code = int.from_bytes(header_d[(T_COAP_CODE, 1)][0], byteorder="big" )
                coap_mid  = int.from_bytes(header_d[(T_COAP_MID, 1)][0], byteorder="big" )
                
                b1 = (coap_ver << 6)|(coap_type<<4)|(coap_tlk)
                coap_h = struct.pack("!BBH", b1, coap_code ,coap_mid )

                tkl = int.from_bytes(header_d[(T_COAP_TKL, 1)][0], byteorder="big" )
                if tkl != 0:
                    token = header_d[(T_COAP_TOKEN, 1)][0]
                    for i in range(len(token)):
                        coap_h += struct.pack("!B", token[i])

                cumul_t = 0
                # /!\ should sort the options before recontructing them
                for opt in header_d.items():
                    if not ("COAP" in opt[0][0]) or (opt[0][0] in [T_COAP_VERSION, T_COAP_TYPE, T_COAP_TKL, T_COAP_CODE, T_COAP_MID, T_COAP_TOKEN]):  
                        continue

                    opt_name = opt[0][0].replace("COAP.", "")
                    opt_val  = opt[1][0]
                    opt_len  = opt[1][1]//8
                    
                    delta_t = coap_options["COAP."+opt_name] - cumul_t
                    cumul_t = coap_options["COAP."+opt_name]
                    #print (opt_name, coap_options[opt_name], delta_t)
                    
                    if delta_t < 13:
                        dt = delta_t
                    else:
                        dt = 13
                        
                    #print (opt_len, opt_val)

                    if opt_len < 13:
                        ol = opt_len
                    else:
                        ol = 13
                        
                    coap_h += struct.pack("!B", (dt <<4) | ol)

                    if dt == 13:
                        coap_h += struct.pack("!B", delta_t - 13)

                    if ol == 13:
                        coap_h += struct.pack("!B", opt_len - 13)

                    #print (binascii.hexlify(coap_h))

                    for i in range (0, opt_len):
                        coap_h += struct.pack("!B", opt_val[i])


                if len(data) > 0:
                    coap_h += b'\xff'
                    coap_h += data
                        
                #print (binascii.hexlify(coap_h))



        if coap_h != None:
            full_packet = L3header / L4header / Raw(load=coap_h)
        elif L4header != None: 
            full_packet = L3header / L4header / Raw(load=data)
        else:
            full_packet = L3header / Raw(load=data)

        if full_packet and iface:
            if verbose:
                print ("Sending to ", iface)
                hexdump(full_packet)
            send(full_packet, iface=iface, verbose=False) #scapy

        return full_packet
