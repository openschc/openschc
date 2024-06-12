import binascii
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from gen_parameters import T_POSITION_DEVICE

import netifaces as ni

import socket
import select
import time

addr = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

PORT = 8888
deviceID = "udp:"+addr+":"+str(PORT)

print("device ID is", deviceID)

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind (("0.0.0.0", PORT)) # same port as in the DeviceID
# Create a Rule Manager and upload the rules.

rm = RM.RuleManager()
rm.Add(file="icmp-bi.json")
rm.Print()

core_id = None

def processPkt(pkt):
    global core_id

    print("+", end="")

    if pkt.getlayer(Ether) != None: 
        print ("-", end="")
        e_type = pkt.getlayer(Ether).type
        pkt.show()
        if e_type == 0x86dd:
            print ("*", end="")
            if pkt[Ether].src == "00:00:00:00:00:00": # on loopback
                if pkt[IPv6].nh == 58: # ICMPv6 
                    print("get from sniff")
                    pkt.show()
                    if core_id: # core is identified, can answer
                        schc_machine.schc_send(bytes(pkt)[14:], core_id = core_id, verbose=True)
                    else:
                        print ("core not yet identified, do not send SCHC pkt")
            else:
                print ("IPv6 not on loopback")
 
    s_in, _, _ = select.select([tunnel], [], [])
 
    if len(s_in) > 0: # data on the socket
        SCHC_pkt, device = tunnel.recvfrom(1000)

        core_id = "udp:"+device[0]+":"+str(device[1])

        origin, full_packet = schc_machine.schc_recv(
                            schc_packet=SCHC_pkt, 
                            device_id=deviceID, 
                            verbose=True)
        print("result", full_packet)

# Start SCHC Machine
POSITION = T_POSITION_DEVICE

schc_machine = SCHCProtocol(role=POSITION, tunnel=tunnel)           
schc_machine.set_rulemanager(rm)
scheduler = schc_machine.system.get_scheduler()
tunnel = schc_machine.get_tunnel()

t = AsyncSniffer(prn=processPkt, iface=["lo"], store=False) 
t.start()
print ("sniff started")
while True:
    scheduler.run(session=schc_machine)

    s_in, _, _ = select.select([tunnel], [], [])
    if len(s_in) > 0: # data on the socket
        SCHC_pkt, device = tunnel.recvfrom(1000)

        core_id = "udp:"+device[0]+":"+str(device[1])

        resp = schc_machine.schc_recv(
                            schc_packet=SCHC_pkt, 
                            device_id=deviceID, 
                            verbose=True)
        
        origin = resp[0]
        full_packet = resp[1]
        
        #print ("---->", type(origin), origin, full_packet)

        if full_packet != None:
        
            #print ("RESULT", full_packet)
            if ICMPv6EchoRequest in full_packet:
                IPv6Header = IPv6 (
                    version= full_packet.version ,
                    tc     = full_packet.tc,
                    fl     = full_packet.fl,
                    nh     = full_packet.nh,
                    hlim   = full_packet.hlim,
                    src    = full_packet.dst, 
                    dst    = full_packet.src
                ) 

                ICMPv6Header = ICMPv6EchoReply(
                    id = full_packet.id,
                    seq =  full_packet.seq,
                    data = full_packet.data)

                Echoreply = IPv6Header / ICMPv6Header

                print ("response is:")
                Echoreply.show()

                schc_machine.schc_send(
                        bytes(Echoreply), 
                        core_id = core_id,
                        verbose=True)
            
                #print (Echoreply)

    time.sleep(0.1)

t.stop()



 
