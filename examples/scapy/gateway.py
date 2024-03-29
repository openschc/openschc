import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *
import scapy.contrib.coap as scapy_coap


import gen_rulemanager as RM
import compr_parser as parser
from compr_core import *
from protocol import SCHCProtocol

from scapy_connection import *

from gen_utils import dprint, sanitize_value


import sched

import protocol

import pprint
import binascii

import socket
import ipaddress

import time, datetime

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

class debug_protocol:
    def _log(*arg):
        print (arg)

parse = parser.Parser(debug_protocol)
rm    = RM.RuleManager()
rm.Add(file="icmp.json")
rm.Print()

comp = Compressor(debug_protocol)
decomp = Decompressor(debug_protocol)

def send_scapy(fields, pkt_bb, rule=None):
    """" Create and send a packet, rule is needed if containing CoAP options to order them
    """ 

    pkt_data = bytearray()
    while (pkt_bb._wpos - pkt_bb._rpos) >= 8:
        octet = pkt_bb.get_bits(nb_bits=8)
        pkt_data.append(octet)

    c = {}
    for k in [T_IPV6_DEV_PREFIX, T_IPV6_DEV_IID, T_IPV6_APP_PREFIX, T_IPV6_APP_IID]:
        v = fields[(k, 1)][0]
        if type(v) == bytes:
            c[k] = int.from_bytes(v, "big")
        elif type(v) == int:
            c[k] = v
        else:
            raise ValueError ("Type not supported")
        
    
    IPv6Src = (c[T_IPV6_DEV_PREFIX] <<64) + c[T_IPV6_DEV_IID]
    IPv6Dst = (c[T_IPV6_APP_PREFIX] <<64) + c[T_IPV6_APP_IID]

    
    IPv6Sstr = ipaddress.IPv6Address(IPv6Src)
    IPv6Dstr = ipaddress.IPv6Address(IPv6Dst)
    
    IPv6Header = IPv6 (
        version= fields[(T_IPV6_VER, 1)][0],
        tc     = fields[(T_IPV6_TC, 1)][0],
        fl     = fields[(T_IPV6_FL, 1)][0],
        nh     = fields[(T_IPV6_NXT, 1)][0],
        hlim   = fields[(T_IPV6_HOP_LMT, 1)][0],
        src    =IPv6Sstr.compressed, 
        dst    =IPv6Dstr.compressed
    ) 

    if fields[(T_IPV6_NXT, 1)][0] == 58: #IPv6 /  ICMPv6
        ICMPv6Header = ICMPv6EchoReply(
            id = fields[(T_ICMPV6_IDENT, 1)][0],
            seq =  fields[(T_ICMPV6_SEQNO, 1)][0],
            data = pkt_data
        )

        full_header = IPv6Header/ICMPv6Header
    elif fields[(T_IPV6_NXT, 1)][0] == 17: # IPv6 / UDP
        UDPHeader = UDP (
            sport = fields[(T_UDP_DEV_PORT, 1)][0],
            dport = fields[(T_UDP_APP_PORT, 1)][0]
            )
        if (T_COAP_VERSION, 1) in fields: # IPv6 / UDP / COAP
            print ("CoAP Inside")

            b1 = (fields[(T_COAP_VERSION, 1)][0] << 6)|(fields[(T_COAP_TYPE, 1)][0]<<4)|(fields[(T_COAP_TKL, 1)][0])
            coap_h = struct.pack("!BBH", b1, fields[(T_COAP_CODE, 1)][0], fields[(T_COAP_MID, 1)][0])

            tkl = fields[(T_COAP_TKL, 1)][0]
            if tkl != 0:
                token = fields[(T_COAP_TOKEN, 1)][0]
                for i in range(tkl-1, -1, -1):
                    bt = (token & (0xFF << 8*i)) >> 8*i
                    coap_h += struct.pack("!B", bt)

            delta_t = 0
            comp_rule = rule[T_COMP] # look into the rule to find options 
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
                    
                opt_len = fields[(comp_rule[idx2][T_FID], comp_rule[idx2][T_FP])][1] // 8
                opt_val = fields[(comp_rule[idx2][T_FID], comp_rule[idx2][T_FP])][0]
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

            if len(pkt_data) > 0:
                coap_h += b'\xff'
                coap_h += pkt_data

                    
            print (binascii.hexlify(coap_h))

            full_header = IPv6Header / UDPHeader / Raw(load=coap_h)
            pass
        else: # IPv6/UDP
            full_header = IPv6Header / UDPHeader / Raw(load=pkt_data)
    else: # IPv6 only
        full_header= IPv6Header / Raw(load=pkt_data)
        

    full_header.show()

    send(full_header, iface="he-ipv6")


    
def send_tunnel(pkt, dest):
    print ("send tunnel")
    print (dest, pkt)
    print (pkt.display())


def processPkt(pkt):
    global parser
    global rm
    global event_queue
    global SCHC_machine
    

    scheduler.run(session=schc_protocol, period=10)

    # look for a tunneled SCHC pkt

    if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
        e_type = pkt.getlayer(Ether).type
        if e_type == 0x0800:
            ip_proto = pkt.getlayer(IP).proto
            if ip_proto == 17:
                udp_dport = pkt.getlayer(UDP).dport
                if udp_dport == socket_port: # tunnel SCHC msg to be decompressed
                    print ("tunneled SCHC msg")                    
                    schc_pkt, addr = tunnel.recvfrom(2000)
                    other_end = "udp:"+addr[0]+":"+str(addr[1])
                    print("other end =", other_end)
                    r = schc_protocol.schc_recv(other_end, schc_pkt)
                    print (r)
    elif IP in pkt and pkt.getlayer(IP).version == 6 : # regular IPv6trafic to be compression
        schc_protocol.schc_send(bytes(pkt))
    else:
     print (".", end="", flush=True)           
                    
        
# look at the IP address to define sniff behavior

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]

POSITION = T_POSITION_CORE

if POSITION==T_POSITION_DEVICE:
    device_id = "udp:83.199.24.39:8888"
    socket_port = 8888
    other_end = ("tests.openschc.net", 0x5C4C)
elif POSITION==T_POSITION_CORE:
    device_id = None
    socket_port = 0x5C4C
    other_end = None # defined by the rule
else:
    print ("not a good position")


tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", 0x5C4C))

config = {}
upper_layer = ScapyUpperLayer()
lower_layer = ScapyLowerLayer(position=POSITION, socket=tunnel, other_end=other_end)
system = ScapySystem()
scheduler = system.get_scheduler()
schc_protocol = protocol.SCHCProtocol(
    config=config, system=system, 
    layer2=lower_layer, layer3=upper_layer, 
    role=POSITION, unique_peer=False)
schc_protocol.set_position(POSITION)
schc_protocol.set_rulemanager(rm)


sniff(prn=processPkt, iface=["he-ipv6", "ens3"])


 
