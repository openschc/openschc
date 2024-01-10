import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from gen_parameters import T_POSITION_DEVICE

import netifaces as ni

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

    scheduler.run(session=schc_machine)

    if pkt.getlayer(Ether) != None: 
        e_type = pkt.getlayer(Ether).type
        if e_type == 0x86dd:
            print ("get IPv6 packet")
            print ("=", pkt[Ether].src)
            pkt.show()
            if core_id:
                schc_machine.schc_send(bytes(pkt)[14:], core_id = core_id)
        elif e_type == 0x0800:
            if pkt[IP].proto == 17 and pkt[UDP].dport == 8888:
                print ("get tunneled SCHC packet")
                # got a packet in the socket
                SCHC_pkt, device = tunnel.recvfrom(1000)

                core_id = "udp:"+device[0]+":"+str(device[1])


                origin, full_packet = schc_machine.schc_recv(
                                   schc_packet=SCHC_pkt, 
                                   device_id=deviceID, 
                                   iface='lo',
                                   verbose=True)
                print (core_id)

# Start SCHC Machine
POSITION = T_POSITION_DEVICE

schc_machine = SCHCProtocol(role=POSITION, tunnel=tunnel)           
schc_machine.set_rulemanager(rm)
scheduler = schc_machine.system.get_scheduler()
tunnel = schc_machine.get_tunnel()

sniff(prn=processPkt, iface=["eth0", "lo"]) 




 
