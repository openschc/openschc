# This scrip is used to manage two rules (rule1100 and 001100) and displays it

from scapy.all import *
import os
os.sys.path.append('../../src')
from gen_rulemanager import *

RM = RuleManager()

rule1100 =   {
  "RuleID" : 12,
  "RuleIDLength" : 4,
  "Compression" : []
}

rule001100 =   {
  "RuleID" : 12,
  "RuleIDLength" : 6,
  "Fragmentation" :  {
    "FRMode" : "NoAck",
    "FRDirection" : "UP"
  }
}

RM.Add(dev_info=rule1100)
RM.Add(dev_info=rule001100)

RM.Print()
