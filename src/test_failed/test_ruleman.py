import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")

from gen_rulemanager import RuleManager
from gen_bitarray import BitBuffer
if sys.implementation.name != "micropython":
    import pytest


context1 = {
    "devL2Addr":"AABBCCDD",
    "dstIID":"2001:0db8:85a3::beef"
}
context2 = {
    "devL2Addr":"*",
    "dstIID":"*"
}
bogusRule0 = { # bogus rule with no frag or comp
    "RuleID": 3
    }
rule1 = {
    "RuleID" : 4,
    "RuleIDLength" : 5,
    "Compression" : []
}
rule2 = {
    "RuleID" : 4,
    "RuleIDLength" : 3,
    "profile": {
        "MICAlgorithm": "RCS_RFC8724",
        "MICWordSize": 8,
        "L2WordSize": 8
    },
    "Fragmentation" : {
        "dir": "out",
        "FRMode": "AckOnError",
        "FRModeProfile": {
            "dtagSize" : 2,
            "FCNSize": 3,
            "ackBehavior" : "afterAll1"
        }
    }
}
rule3 = {
    "RuleID" : 7,
    "RuleIDLength" : 3,
    "Profile": {
        "MICAlgorithm": "RCS_RFC8724",
        "MICWordSize": 8,
        "L2WordSize": 8
    },
    "Fragmentation" : {
        "dir": "in",
        "FRMode" :"NoAck"
    },
}
conflictingRule0 = {
    "RuleID" : 15,
    "RuleIDLength" : 4,
    "compression" : { "rule_set": [] }
    }

def test_ruleman_01():
    # XXX actually, it is not test code right now.
    RM = RuleManager()
    RM.add_context(context1, rule1,rule2,rule3)
    RM.add_context(context2, rule1)
    print(RM._db)
    #RM.add_rules(context1, [conflictingRule0])
    #RM.add_rules(context1, [bogusRule0])
    print(RM.find_context_bydevL2addr("AABBCCDD"))
    print(RM.find_context_bydstiid("2001:0db8:85a3::beef"))
    RM.find_rule_bypacket(context1, BitBuffer(int("10000111",2).to_bytes(1, "big")))


# for micropython and other tester.
if __name__ == "__main__":
    test_ruleman_01()
