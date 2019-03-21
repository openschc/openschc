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

class SCHC_server:
    def __init__(self, scheduler):
        self.rule = []
        self.context ="example/context-100.json"
        self.rule_comp = "example/comp-rule-100.json"
        '''NO-ACK'''
        self.rule_fragin = "example/frag-rule-201.json"
        self.rule_fragout = "example/frag-rule-202.json"
        '''ACK-ON-ERROR'''
        #self.rule_fragin = "example/frag-rule-101.json"
        #self.rule_fragout = "example/frag-rule-102.json"

        self.rule_fragout = "example/frag-rule-202.json"
        for k in [self.context,self.rule_comp,self.rule_fragin,self.rule_fragout]:
            with open(k) as fd:
                self.rule.append(json.loads(fd.read()))

        self.rule_manager = RuleManager()
        print("RULE: ", self.rule[3])
        self.rule_manager.add_context(self.rule[0], self.rule[1], self.rule[2], self.rule[3])
#--------------------------------------------------------------------------
#simul
        self.l2_mtu = 56
        self.layer_2 = SimulLayer2()
        self.layer_2.set_mtu(self.l2_mtu)
        self.layer_3 = SimulLayer3()
        self.scheduler = scheduler
        #self.scheduler = Scheduler()
        self.protocol = schc.SCHCProtocol(self.scheduler, self.layer_2, self.layer_3)
        self.protocol.set_rulemanager(self.rule_manager)
        self.protocol.set_dev_L2addr(0)#setear la direccion MAC
        self.sender_id = self.layer_2.mac_id #tengo que tener la mac del que envia
#-------------------------------------------------------------------------
    def reassemble(self,Fragment):
        self.layer_2.event_receive_packet(self.sender_id, Fragment)

    def sendMessage(self,msg):
        self.layer_3.send_later(1, 1,msg)

#-----------------------------------------------------------------------
