import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from gen_parameters import T_POSITION_CORE

# Create a Rule Manager and upload the rules.

rm = RM.RuleManager()
rm.Add(file="icmp.json")
rm.Print()

def processPkt(pkt):
    """ called when scapy receives a packet, since this function takes only one argument,
    schc protocol must be specified as a global variable.
    """

    scheduler.run(session=schc_machine, display_period=10)

    # look for a tunneled SCHC pkt
    if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
        e_type = pkt.getlayer(Ether).type
        if e_type == 0x86dd:
            schc_machine.schc_send(bytes(pkt)[34:])


# Start SCHC Machine
POSITION = T_POSITION_CORE

schc_machine = SCHCProtocol(role=POSITION)           
schc_machine.set_rulemanager(rm)
scheduler = schc_machine.system.get_scheduler()


sniff(prn=processPkt, iface="eth1") # scappy cannot read multiple interfaces




 
