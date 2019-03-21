#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from rulemanager import RuleManager

context1 = {
    "devL2Addr":"AABBCCDD",
    "dstIID":"2001:0db8:85a3::beef"
}
context2 = {
    "devL2Addr":"*",
    "dstIID":"*"
}
bogusRule0 = { # bogus rule with no frag or comp
    "ruleID": 3
    }
rule1 = {
    "ruleID" : 4,
    "ruleLength" : 5,
    "compression" : {
    }
}
rule2 = {
    "ruleID" : 4,
    "ruleLength" : 3,
    "profile": {
        "MICAlgorithm": "crc32",
        "MICWordSize": 8,
        "L2WordSize": 8
    },
    "fragmentation" : {
        "dir": "out",
        "FRMode": "ackOnError",
        "FRModeProfile": {
            "dtagSize" : 2,
            "FCNSize": 3,
            "ackBehavior" : "afterAll1"
        }
    }
}
rule3 = {
    "ruleID" : 7,
    "ruleLength" : 3,
    "profile": {
        "MICAlgorithm": "crc32",
        "MICWordSize": 8,
        "L2WordSize": 8
    },
    "fragmentation" : {
        "dir": "in",
        "FRMode" :"noAck"
    },
}
conflictingRule0 = {
    "ruleID" : 15,
    "ruleLength" : 4,
    "compression" : {},
    }

RM = RuleManager()
RM.add_context(context1, rule1,rule2,rule3)
RM.add_context(context2, rule1)
print(RM._db)
#RM.add_rules(context1, [conflictingRule0])
#RM.add_rules(context1, [bogusRule0])
print(RM.find_context_bydevL2addr("AABBCCDD"))
print(RM.find_context_bydstiid("2001:0db8:85a3::beef"))

from bitarray import BitBuffer
RM.find_rule_bypacket(context1, BitBuffer(int("10000111",2).to_bytes(1, "big")))
