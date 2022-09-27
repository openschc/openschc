import pytest
import gen_rulemanager
import gen_bitarray

#============================ defines =========================================

CONTEXT1 = {
    "devL2Addr":             "AABBCCDD",
    "dstIID":                "2001:0db8:85a3::beef",
}
CONTEXT2 = {
    "devL2Addr":             "*",
    "dstIID":                "*",
}
BOGUSRULE0 = { # bogus rule with no frag or comp
    "RuleID":                3,
}
RULE1 = {
    "RuleID":                4,
    "RuleIDLength":          5,
    "Compression":           [],
}
RULE2 = {
    "RuleID":                4,
    "RuleIDLength":          3,
    "profile": {
        "MICAlgorithm":      "RCS_RFC8724",
        "MICWordSize":       8,
        "L2WordSize":        8,
    },
    "Fragmentation": {
        "dir":               "out",
        "FRMode":            "AckOnError",
        "FRModeProfile": {
            "dtagSize":      2,
            "FCNSize":       3,
            "ackBehavior":   "afterAll1",
        }
    }
}
RULE3 = {
    "RuleID" :               7,
    "RuleIDLength" :         3,
    "Profile": {
        "MICAlgorithm":      "RCS_RFC8724",
        "MICWordSize":       8,
        "L2WordSize":        8,
    },
    "Fragmentation": {
        "dir":               "in",
        "FRMode":            "NoAck",
    },
}
CONFLICTINGRULE0 = {
    "RuleID":                15,
    "RuleIDLength":          4,
    "compression": {
        "rule_set":          [],
    }
}

#============================ helpers =========================================

#============================ tests ===========================================

@pytest.mark.skip() 
def test_rulemanager():
    # XXX actually, it is not test code right now.
    RM = gen_rulemanager.RuleManager()
    RM.add_context(CONTEXT1, RULE1, RULE2, RULE3)
    RM.add_context(CONTEXT2, RULE1)
    print(RM._db)
    #RM.add_rules(CONTEXT1, [CONFLICTINGRULE0])
    #RM.add_rules(CONTEXT1, [BOGUSRULE0])
    print(RM.find_context_bydevL2addr("AABBCCDD"))
    print(RM.find_context_bydstiid("2001:0db8:85a3::beef"))
    RM.find_rule_bypacket(CONTEXT1, gen_bitarray.BitBuffer(int("10000111",2).to_bytes(1, "big")))
