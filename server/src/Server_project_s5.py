#---------------------------------------------------------------------------
import sys
import time
# Template for schc simulation implemented to Project S5
import argparse

from base_import import *  # used for now for differing modules in py/upy
from simsched import SimulScheduler as Scheduler
import schc
import simsched
from simlayer2 import SimulLayer2
from simul import SimulLayer3
import simul
from rulemanager import RuleManager

class Server_project_s5:
    def main():
        add_rules()        
#--------------------------------------------------------------------------
#addthe group of rules, for the Tx and Rx
    def add_rules():
        loss_config = None
        rule = []
        context ="example/context-100.json"
        rule_comp = "example/comp-rule-100.json"
        rule_fragin = "example/frag-rule-201.json"
        rule_fragout = "example/frag-rule-202.json"
        for k in [context,rule_comp,rule_fragin,rule_fragout]:
            with open(k) as fd:
                rule.append(json.loads(fd.read()))

        rule_manager = RuleManager()
        print("RULE: ", rule[3])
        rule_manager.add_context(rule[0], rule[1], rule[2], rule[3])
#--------------------------------------------------------------------------
#simul
        l2_mtu = 56
        simul_config = {
            "log": True,
        }
        if loss_config is not None:
            simul_config["loss"] = loss_config
        sim = simul.Simul(simul_config)

        layer_2 = SimulLayer2(sim)
        layer_2.set_mtu(l2_mtu)
        layer_3 = SimulLayer3(sim)
        scheduler = Scheduler()
        protocol = schc.SCHCProtocol(scheduler,sim, layer_2, layer_3)
        protocol.set_rulemanager(rule_manager)
        protocol.set_dev_L2addr(0)#setear la direccion MAC
#--------------------------------------------------------------------------
#packets simulated
        sender_id = layer_2.mac_id #tengo que tener la mac del que envia
        Fragment1 = b'\x48\x01\x02\x03\x04\x05\x06'
        Fragment2 = b'\x48\x07\x08\x09\x0a\x0b\x0c'
        Fragment3 = b'\x48\x0d\x0e\x0f\x10\x11\x12'
        Fragment4 = b'\x48\x13\x14\x15\x16\x17\x18'
        Fragment5 = b'\x48\x19\x1a\x1b\x1c\x1d\x1e'
        Fragment6 = b'\x48\x1f\x20\x21\x22\x23\x24'
        Fragment7 = b'\x48\x25\x26\x27\x28\x29\x2a'
        Fragment8 = b'\x48\x2b\x2c\x2d\x2e\x2f\x30'
        Fragment9 = b'\x48\x31\x32\x33\x34\x35\x36'
        Fragment10 = b'\x48\x37\x38\x39\x3a\x3b\x3c'
        Fragment11 = b'\x48\x3d\x3e\x3f\x40\x41\x42'
        Fragment12 = b'\x48\x43\x44\x45\x46\x47\x48'
        Fragment13 = b'\x48\x49\x4a\x4b\x4c\x4d\x4e'
        Fragment14 = b'\x48\x4f\x50\x51\x52\x53\x54'
        Fragment15 = b'\x48\x55\x56\x57\x58\x59\x5a'
        Fragment16 = b'\x48\x5b\x5c\x5d\x5e\x5f\x60'
        Fragment17 = b'\x48\x61\x62\x63\x64'
        Fragment18 = b'\x4f\x65\xf0\x0f\x42'   
          
        
                        
#-----------------------------------------------------------------------     
#Received message
        layer_2.event_receive_packet(sender_id, Fragment1)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment2)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment3)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment4)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment5)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment6)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment7)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment8)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment9)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment10)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment11)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment12)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment13)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment14)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment15)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment16)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment17)
        #time.sleep(1)
        layer_2.event_receive_packet(sender_id, Fragment18)
        



#-----------------------------------------------------------------------

    if __name__ == "__main__":
        #main()
        add_rules()

