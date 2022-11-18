import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

import gen_rulemanager as RM

import pprint
import binascii
import base64

import cbor2 as cbor

from yangson import DataModel

yang_type = {
       "/ietf-schc:schc": "node",
       "/ietf-schc:schc/rule": "node",
       "/ietf-schc:schc/rule/ack-behavior": "identifier",
       "/ietf-schc:schc/rule/direction": "identifier",
       "/ietf-schc:schc/rule/dtag-size": "int",
       "/ietf-schc:schc/rule/entry": "node",
       "/ietf-schc:schc/rule/entry/comp-decomp-action": "identifier",
       "/ietf-schc:schc/rule/entry/comp-decomp-action-value": "node",
       "/ietf-schc:schc/rule/entry/comp-decomp-action-value/index": "int",
       "/ietf-schc:schc/rule/entry/comp-decomp-action-value/value": "str",
       "/ietf-schc:schc/rule/entry/direction-indicator": "identifier",
       "/ietf-schc:schc/rule/entry/field-id": "identifier",
       "/ietf-schc:schc/rule/entry/field-length": "union",
       "/ietf-schc:schc/rule/entry/field-position": "int",
       "/ietf-schc:schc/rule/entry/matching-operator": "identifier",
       "/ietf-schc:schc/rule/entry/matching-operator-value": "node",
       "/ietf-schc:schc/rule/entry/matching-operator-value/index": "int",
       "/ietf-schc:schc/rule/entry/matching-operator-value/value": "str",
       "/ietf-schc:schc/rule/entry/target-value": "node",
       "/ietf-schc:schc/rule/entry/target-value/index": "int",
       "/ietf-schc:schc/rule/entry/target-value/value": "str",
       "/ietf-schc:schc/rule/fcn-size": "int",
       "/ietf-schc:schc/rule/fragmentation-mode": "identifier",
       "/ietf-schc:schc/rule/inactivity-timer": "node",
       "/ietf-schc:schc/rule/inactivity-timer/ticks-duration": "int",
       "/ietf-schc:schc/rule/inactivity-timer/ticks-numbers": "int",
       "/ietf-schc:schc/rule/l2-word-size": "int",
       "/ietf-schc:schc/rule/max-ack-requests": "int",
       "/ietf-schc:schc/rule/max-interleaved-frames": "int",
       "/ietf-schc:schc/rule/maximum-packet-size": "int",
       "/ietf-schc:schc/rule/rcs-algorithm": "identifier",
       "/ietf-schc:schc/rule/retransmission-timer": "node",
       "/ietf-schc:schc/rule/retransmission-timer/ticks-duration": "int",
       "/ietf-schc:schc/rule/retransmission-timer/ticks-numbers": "int",
       "/ietf-schc:schc/rule/rule-id-length": "int",
       "/ietf-schc:schc/rule/rule-id-value": "int",
       "/ietf-schc:schc/rule/rule-nature": "identifier",
       "/ietf-schc:schc/rule/tile-in-all-1": "identifier",
       "/ietf-schc:schc/rule/tile-size": "int",
       "/ietf-schc:schc/rule/w-size": "int",
       "/ietf-schc:schc/rule/window-size": "int"
}

rm    = RM.RuleManager()
rm.Add(file="comp-rule-100.json")
rm.Print()

def convert_to_json(jcc, delta=0, name_ref=""):
    global deep

    if type(jcc) is dict:
        json_dict = {}
        for k, v in jcc.items():
            sid_description = rm.sid_search_sid(k+delta)
            value = convert_to_json(v, k+delta, sid_description["identifier"])
            key = sid_description["identifier"].replace(name_ref+'/', '')

            json_dict[key] = value
        return json_dict
    elif type(jcc) is list:
        json_list = []
        for e in jcc:
            value = convert_to_json(e, delta, name_ref )
            json_list.append(value)
        return json_list
    elif type(jcc) is int:
        node_type = yang_type[name_ref]

        if node_type == "int":
            return jcc
        elif node_type == "identifier":
            sid_ref = rm.sid_search_sid(jcc)
            assert( sid_ref["namespace"] == "identity")
            return sid_ref["identifier"]
        elif node_type == "union":
            return str(jcc)
        else:
            raise ValueError(name_ref, "not a leaf")

    elif type(jcc) is bytes:
        return base64.b64encode(jcc).decode()
    else:
        raise ValueError ("Unknown type", type(jcc))

rm.add_sid_file("ietf-schc@2022-10-09.sid")

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
