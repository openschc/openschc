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
  "Fragmentation" : {
    "FRMode": "NoAck"
  }
}

RM.Add(device="1234567890", dev_info=[rule1100, rule001100])

RM.Print()
