import sys, os
# insert at 1, 0 is the script path (or '' in REPL)

if os.name == 'nt':
    sys.path.insert(1, '..\\..\\src\\')
else:
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

def convert_to_json(jcc, delta=0, name_ref=""):
    global deep

    if type(jcc) is dict:
        json_dict = {}
        for k, v in jcc.items():
            sid_description = rm.sid_search_sid(k+delta)
            value = convert_to_json(v, k+delta, sid_description)
            key = sid_description.replace(name_ref+'/', '')

            json_dict[key] = value
        return json_dict
    elif type(jcc) is list:
        json_list = []
        for e in jcc:
            value = convert_to_json(e, delta, name_ref )
            json_list.append(value)
        return json_list
    elif type(jcc) is int:
        node_type = rm.get_yang_type(name_ref)

        if node_type in ["int", "union"]: #/!\ to be improved, suppose that union contains an int
            return jcc
        elif node_type == "identifier":
            sid_ref = rm.sid_search_sid(jcc)
            return sid_ref
        else:
            raise ValueError(name_ref, node_type, "not a leaf")

    elif type(jcc) is bytes:
        return base64.b64encode(jcc).decode()
    elif type(jcc) is cbor.CBORTag: # TAG == 45, an identifier not an int.
        if jcc.tag == 45:
            sid_ref = rm.sid_search_sid(jcc.value)
            return sid_ref
        else:
            raise ValueError("CBOR Tag unknown:", jcc.tag)
    else:
        raise ValueError ("Unknown type", type(jcc))

rm.add_sid_file("ietf-schc@2022-12-19.sid")
rm.add_sid_file("ietf-schc-oam@2021-11-10.sid")

ycbor = rm.to_coreconf()
print (binascii.hexlify(ycbor))
pprint.pprint(cbor.loads(ycbor))

yr = convert_to_json (cbor.loads(ycbor))
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

print ("APP PREFIX TV")
app_prefix_tv = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/target-value", 
                                        keys= [5, 3, 1000057, 1, 1000018,]) 
pprint.pprint (app_prefix_tv)

print ("URI QUERY MSB VAL")
mo_tv = rm.manipulate_coreconf(device="test:device1", sid="/ietf-schc:schc/rule/entry/matching-operator-value/value", 
                                        keys= [5, 3, 'fid-coap-option-uri-query', 1, 'di-up', 0]) 
pprint.pprint (mo_tv)