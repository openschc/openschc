from rulemanager import *

devaddr = b"\xaa\xbb\xcc\xdd"
print("---------Rules Device -----------")
rm0 = RuleManager()
#rm0.add_context(rule_context, compress_rule1, frag_rule3, frag_rule4)
rm0.Add(device = devaddr, file="example/comp-rule-100.json")
rm0.Print()
