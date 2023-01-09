import sys, os
# insert at 1, 0 is the script path (or '' in REPL)

sys.path.insert(1, '../../src/')

import gen_rulemanager as RM

import pprint
import binascii
import base64

import cbor2 as cbor

from yangson import DataModel

rm    = RM.RuleManager()
rm.Add(file="comp-rule-100.json", device="test:device1")
rm.Print()



rm.add_sid_file("ietf-schc@2022-12-19.sid")
rm.add_sid_file("ietf-schc-oam@2021-11-10.sid")

ycbor = rm.to_coreconf()
print (binascii.hexlify(ycbor))
pprint.pprint(cbor.loads(ycbor))

yr = rm.convert_to_json (cbor.loads(ycbor))
pprint.pprint(yr)


dm = DataModel.from_file("description.json")

print (dm.ascii_tree())

inst = dm.from_raw(yr)
print ("validation", inst.validate())
print(dm.ascii_tree(no_types=True, val_count=True), end='')


print ("FULL SET OF RULES")
sor=rm.manipulate_coreconf(device="test:device1", sid=1000095) # get full conf
pprint.pprint (sor)

print ("RULE 5/3")
rule_5_3 = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule", keys= [5, 3]) # get full conf
pprint.pprint (rule_5_3)

print ("IPv6 VERSION TV")
ipv6_version_tv = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value", 
                                        keys= [5, 3, 1000068, 1, 1000018]) 
pprint.pprint (ipv6_version_tv)


print ("IPv6 VERSION VALUE")
ipv6_version_value = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value/value", 
                                        keys= [5, 3, 1000068, 1, 1000018, 0]) 
pprint.pprint (ipv6_version_value)

print ("APP PREFIX TV")
app_prefix_tv = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value", 
                                        keys= [5, 3, 1000057, 1, 1000018,]) 
pprint.pprint (app_prefix_tv)

print ("APP PREFIX VALUE 1")
app_prefix_tv = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value/value", 
                                        keys= [5, 3, 1000057, 1, 1000018, 1]) 
pprint.pprint (app_prefix_tv)

print ("URI QUERY MSB VAL")
mo_tv = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/matching-operator-value/value", 
                                        keys= [5, 3, 'fid-coap-option-uri-query', 1, 'di-up', 0]) 
pprint.pprint (mo_tv)

print ("SET HOP LIMIT")
hop_limit_value = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value/value", 
                                        keys= [5, 3, 'fid-ipv6-hoplimit', 1, 'di-bidirectional', 0]) 
pprint.pprint (hop_limit_value)
hop_limit = int.from_bytes(list(hop_limit_value.values())[0], "big")
hop_limit -= 1
hop_limit_value = hop_limit.to_bytes(1, "big")
print ("decrement value")

hop_limit_result = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value/value", 
                                        keys= [5, 3, 'fid-ipv6-hoplimit', 1, 'di-bidirectional', 0], value=hop_limit_value) 
pprint.pprint(hop_limit_result)


hop_limit_value = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value/value", 
                                        keys= [5, 3, 'fid-ipv6-hoplimit', 1, 'di-bidirectional', 0]) 
pprint.pprint (hop_limit_value)
rm.Print()

print("generate an error since rule is not conform to YANG DM")
#set to not-send without TV

try:
    wrong_result = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/comp-decomp-action", 
                                        keys= [5, 3, 'fid-coap-type', 1, 'di-bidirectional'], value='cda-not-sent',
                                        validate = dm) 
except Exception as e:
    print ("Yangson do not accept this")
    print (e)

print ("make it conform")
intermediary_result = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/comp-decomp-action", 
                                        keys= [5, 3, 'fid-coap-type', 1, 'di-bidirectional'], value='cda-not-sent')

print ("CDA set")
intermediary_result = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value", 
                                        keys= [5, 3, 'fid-coap-type', 1, 'di-bidirectional'], 
                                        value=[{1: 0, 2: b'\x03'}],
                                        validate=dm)

rm.Print()

print ("CHANGE AN EXISTING RULE")

intermediary_result = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule", 
                                        keys=[6, 3],
                                        value={33: 3, 34: 6, 35: 1000090})
rm.Print()

print ("ADD A RULE")

intermediary_result = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule", 
                                        keys=[10, 8],
                                        value={33: 8, 34: 10, 35: 1000090}, validate=dm) # 33: and 34: useless since in key
rm.Print()