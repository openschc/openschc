import sys
sys.path.insert(1, '../../../openschc/src/')

from protocol import SCHCProtocol
import gen_rulemanager as RM
from gen_parameters import T_POSITION_DEVICE
from gen_parameters import T_POSITION_CORE
import socket
import select
import time

addr = '127.0.0.1'
PORT = 9999
deviceID = "udp:127.0.0.1:8888"


# Création du socket UDP IPv4
tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind((addr, PORT))

# Rule manager
rm = RM.RuleManager()
rm.Add(file="icmp-bi2.json")
rm.Print()

schc_machine = SCHCProtocol(role=T_POSITION_CORE, tunnel=tunnel)
schc_machine.set_rulemanager(rm)
scheduler = schc_machine.system.get_scheduler()

print(f"Receiver running on {deviceID}...")

while True:
    scheduler.run(session=schc_machine)

    r, _, _ = select.select([tunnel], [], [], 0.1)
    if r:
        SCHC_pkt, device = tunnel.recvfrom(2000)
        origin, full_packet = schc_machine.schc_recv(SCHC_pkt, device_id=deviceID, verbose=True)


        if full_packet:
            print("[+] Got packet:")
            full_packet.show()

    time.sleep(0.1)
