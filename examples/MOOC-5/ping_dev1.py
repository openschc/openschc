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

# Start SCHC Machine
POSITION = T_POSITION_DEVICE

schc_machine = SCHCProtocol(role=POSITION, tunnel=tunnel)           
schc_machine.set_rulemanager(rm)
scheduler = schc_machine.system.get_scheduler()
tunnel = schc_machine.get_tunnel()

t = AsyncSniffer(iface="eth0", store=False) 
t.start()
print ("sniff started")
while True:
    scheduler.run(session=schc_machine)

    s_in, _, _ = select.select([tunnel], [], [], 0.1)
    if len(s_in) > 0: # data on the socket
        SCHC_pkt, device = tunnel.recvfrom(1000)

        core_id = "udp:"+device[0]+":"+str(device[1])

        origin, full_packet = schc_machine.schc_recv(
                            schc_packet=SCHC_pkt, 
                            device_id=deviceID, 
                            verbose=True)
        
        if full_packet is not None and ICMPv6EchoRequest in full_packet:
            response =             IPv6Header = IPv6 (
                version= full_packet[IPv6].version,
                tc     = full_packet[IPv6].tc,
                fl     = full_packet[IPv6].fl,
                hlim   = 64,
                src    = full_packet[IPv6].dst,
                dst    = full_packet[IPv6].src
            ) / ICMPv6EchoReply (
                id = full_packet[ICMPv6EchoRequest].id,
                seq = full_packet[ICMPv6EchoRequest].seq,
                data = full_packet[ICMPv6EchoRequest].data
            )
            schc_machine.schc_send(bytes(response), core_id = core_id, verbose=True)
    time.sleep(0.1)
