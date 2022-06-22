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

RM.Add(dev_info=[rule1100,rule001100])
RM.Print()
