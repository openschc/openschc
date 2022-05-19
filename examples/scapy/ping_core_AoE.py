import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from scapy_connection import *
from gen_utils import dprint, sanitize_value
from scapy.layers.inet import IP
#from scapy.layers.inet6 import IPv6

import pprint
import binascii
import socket
import ipaddress
from threading import Thread
from requests import get

class Sniffer(Thread):
    def  __init__(self, interface="ens3"):
        super().__init__()

        self.interface = interface
        #self.stop_sniffer = Event()

    def run(self):
        sniff(prn=self.processPkt, iface=self.interface) # stop_filter=self.should_stop_sniffer)

    def processPkt(self, pkt):
        """ called when scapy receives a packet, since this function takes only one argument,
        schc_machine and scheduler must be specified as a global variable.
        """
        scheduler.run(session=schc_machine)

        # look for a tunneled SCHC pkt
        if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
            e_type = pkt.getlayer(Ether).type
            if e_type == 0x0800:
                ip_proto = pkt.getlayer(IP).proto
                if ip_proto == 17:
                    udp_dport = pkt.getlayer(UDP).dport
                    print ("tunneled SCHC msg", udp_dport)  
                    if udp_dport == socket_port: # tunnel SCHC msg to be decompressed
                        print ("tunneled SCHC msg")                    
                        schc_pkt, addr = tunnel.recvfrom(2000)
                        other_end = "udp:"+addr[0]+":"+str(addr[1])
                        print("other end =", other_end)
                        uncomp_pkt = schc_machine.schc_recv(core_id=core_id, device_id=other_end, schc_packet=schc_pkt)                       
                        if uncomp_pkt != None:
                            uncomp_pkt[1].show()
                            send(uncomp_pkt[1], iface="he-ipv6") 
                elif ip_proto==41:
                    contexts.append(tuple([ time.time(), schc_machine.schc_send(raw_packet=bytes(pkt)[34:], core_id=core_id)])) # device_id is retrieved later from the rule
                    print ("frag_context at ping_core", contexts[-1])
                    pkt.show2() 

class Loop_on_contexts(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            for ctx in range(len(contexts)):
                print("Contexts at ping_core: ", contexts)
                print("Context added time : ", contexts[ctx][0])
                print("Session type at ping_core: ", contexts[ctx][1].get_session_type())
                last_time = contexts[ctx][1].last_send_time - init_time
                abort_sent = contexts[ctx][1].sender_abort_sent
                all1_send = contexts[ctx][1].all1_send
                print("last time: ", last_time, "abort_sent : ", abort_sent)
                if all1_send == False and last_time > 7 and not abort_sent:
                    print("Sending Abort")
                    abort = contexts[ctx][1].send_sender_abort()

            old_contexts = [i for i, x in enumerate(contexts) if contexts[ctx][1].send_sender_abort() or contexts[ctx][1].all1_send]
            new_contexts = [i for j, i in enumerate(contexts) if j not in old_contexts]
            contexts.clear()
            for ctx in range(len(new_contexts)):
                contexts.append(new_contexts[ctx])

            time.sleep(5)

# Create a Rule Manager and upload the rules.
rm = RM.RuleManager()
rm.Add(file="icmp3.json")
rm.Print()

# Start SCHC Machine
POSITION = T_POSITION_CORE

socket_port = 0x5C4C
ip = get('https://api.ipify.org').text
core_id = 'udp:'+ip+":"+str(socket_port)

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", socket_port))

lower_layer = ScapyLowerLayer(position=POSITION, socket=tunnel, other_end=None)
system = ScapySystem()
scheduler = system.get_scheduler()
schc_machine = SCHCProtocol(
    system=system,           # define the scheduler
    layer2=lower_layer,      # how to send messages
    role=POSITION,           # DEVICE or CORE
    verbose = True)         
schc_machine.set_rulemanager(rm)


init_time = time.time()

sniffer = Sniffer()
sniffer.start()

contexts = list()
context_tracker = Loop_on_contexts()
context_tracker.start()