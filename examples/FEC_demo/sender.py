import sys
sys.path.insert(1, '../../../openschc/src/')

from scapy.all import *
import gen_rulemanager as RM
from protocol import SCHCProtocol
from gen_parameters import T_POSITION_DEVICE
import socket
import select
import time

# Paramètres loopback
addr = '127.0.0.1'
PORT = 8888
REMOTE_PORT = 9999

device_id = "udp:127.0.0.1:8888"
core_id = "udp:127.0.0.1:9999"

print("Device ID is", device_id)
print("Core ID (destination) is", core_id)

# Création du socket UDP IPv4
tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind((addr, PORT))

# Rule manager
rm = RM.RuleManager()
rm.Add(file="icmp-bi-FEC.json")
rm.Print()

# Start SCHC stack
schc_machine = SCHCProtocol(role=T_POSITION_DEVICE, tunnel=tunnel)
schc_machine.set_rulemanager(rm)
scheduler = schc_machine.system.get_scheduler()

# Simuler un ICMP Echo Request IPv4 (avec Scapy, c’est ICMP classique)
icmp_request = IP(src=addr, dst=addr) / ICMP(id=0x1234, seq=1) / b"0123456789abcdef0123456789abcdef"

print("[*] Sending ICMP Echo Request...")
schc_machine.schc_send(bytes(icmp_request), device_id= device_id ,core_id=core_id, verbose=True)

scheduler.run(session=schc_machine)

print("Paquet envoyé :", bytes(icmp_request))