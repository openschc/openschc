import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *
import binascii
import gen_rulemanager as RM
import compr_parser as parser
from compr_core import *
from protocol import SCHCProtocol

import pprint
import binascii

import socket

import time, datetime
import struct

import frag_recv

from random import randint

import cbor2 as cbor

# ------

class debug_protocol:
    def _log(*arg):
        print (arg)

parse = parser.Parser(debug_protocol)
rm    = RM.RuleManager()
rm.Add(file="icmp.json")
rm.Print()

comp = Compressor(debug_protocol)
decomp = Decompressor(debug_protocol)

# -------
tunnel = None

event_queue = []

mid = 0
token = 0X200



frag_ctxt = [] 

def get_frag_ctxt (rule, dev=None):
    global frag_ctxt

    print (frag_ctxt)
    for fc in frag_ctxt:
        if fc[T_RULEID] == rule[T_RULEID] and fc[T_RULEIDLENGTH] == rule[T_RULEIDLENGTH]:
            return fc
    print ("get_fragCtxt not found", T_FRAG_NO_ACK, rule, rule[T_FRAG][T_FRAG_MODE])
    fc = None
    if rule[T_FRAG][T_FRAG_MODE] == T_FRAG_NO_ACK:
        fc = {}
        fc[T_RULEID]  = rule[T_RULEID]
        fc[T_RULEIDLENGTH] = rule[T_RULEIDLENGTH]
        fc["CONTEXT"] = frag_recv.ReassemblerNoAck(rule=rule)
        frag_ctxt.append(fc)
        print (frag_ctxt)

    return fc


def send_coap_request():
    global mid, token
    global tunnel
    
    print ("send CoAP", mid, token, flush=True)

    coap_msg = struct.pack("!BHH", 2, mid, token)
    coap_msg += cbor.dumps(randint(10, 1000))

    print (binascii.hexlify(coap_msg))

    tunnel.sendto(coap_msg, ("tests.openschc.net", 0x5C4C))
    
    mid += 1
    token += 2
    event_queue.append([int(time.time())+10, send_coap_request])
    

def processPkt(pkt):
    global parser
    global rm
    global frag_ctxt
    global SCHC_machine
    global device_id
    
    # look for a tunneled SCHC pkt
    epoch = int(time.time())

    if len(event_queue) > 0 and epoch > event_queue[0][0]:
        e = event_queue.pop(0)
        print (e)
        e[1]()
        
    if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
        e_type = pkt.getlayer(Ether).type
        if e_type == 0x0800:
            ip_proto = pkt.getlayer(IP).proto
            if ip_proto == 17:
                udp_dport = pkt.getlayer(UDP).dport
                if udp_dport == socket_port: # tunnel SCHC msg to be decompressed
                    print ("tunneled SCHC msg")

                    #pkt.show()

            
                    schc_pkt, addr = tunnel.recvfrom(2000)
                    r = SCHC_machine.schc_recv(device_id, schc_pkt)

                    print (r)
                    
                    return



        
    elif IP in pkt and pkt.getlayer(IP).version == 6 : # regular IPv6trafic to be compression

        pkt_fields, data, err = parse.parse( bytes(pkt), T_DIR_DW, layers=["IP", "ICMP"], start="IPv6")
        print (pkt_fields)

        if pkt_fields != None:
            rule, device = rm.FindRuleFromPacket(pkt_fields, direction=T_DIR_DW)
            if rule != None:
                schc_pkt = comp.compress(rule, pkt_fields, data, T_DIR_DW)
                if device.find("udp") == 0:
                    destination = (device.split(":")[1], int(device.split(":")[2]))
                    print (destination)
                    schc_pkt.display()
                    tunnel.sendto(schc_pkt._content, destination)
                else:
                    print ("unknown connector" + device)
    else:
     print (".", end="", flush=True)           
                    
        
# look at the IP address to define sniff behavior

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]

if ip_addr == "192.168.1.11":
    print("device role")
    send_dir = T_DIR_UP
    recv_dir = T_DIR_DW

    socket_port = 8888

    device_id = "udp:83.199.61.5:8888"

    tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tunnel.bind(("0.0.0.0", 8888))

    SCHC_machine = SCHCProtocol()
    SCHC_machine.set_rulemanager(rm)

    #event_queue.append([int(time.time())+10, send_coap_request]) s

    sniff (filter="ip6 or port 23628 and not arp",
           prn=processPkt,
           iface="en0")


 
