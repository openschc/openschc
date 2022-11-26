import sys, os
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

rule = binascii.unhexlify('a11a000f429ea10187a404981aa7061a000f428307040801051a000f4252091a000f4292011a000f424f0d81a20100024106a7061a000f428007080801051a000f4252091a000f4292011a000f424f0d81a20100024101a7061a000f427c07140801051a000f4252091a000f4293011a000f424f0d81a201000243023456a6061a000f427f07100801051a000f4252091a000f4293011a000f424ba7061a000f427e07080801051a000f4252091a000f4293011a000f42500d81a20100024111a7061a000f427d07080801051a000f4252091a000f4293011a000f424f0d81a201000241ffa7061a000f427b0718400801051a000f4252091a000f4294011a000f424e0d83a20100024820010db800000000a201010248fe80000000000000a20102024820010420c0dc1002a7061a000f427a0718400801051a000f4252091a000f4292011a000f424c0d81a2010002480000000000000001a7061a000f42780718400801051a000f4252091a000f4294011a000f424e0d83a20100024820010db800010000a201010248fe80000000000000a2010202482404680040040818a7061a000f42770718400801051a000f4252091a000f4292011a000f424f0d81a2010002480000000000000002a8061a000f428807100801051a000f4252091a000f42950a81a2010002410c011a000f424d0d81a2010002421630a8061a000f428507100801051a000f4252091a000f42950a81a2010002410c011a000f424d0d81a2010002421630a7061a000f428907100801051a000f4252091a000f4293011a000f424b0d81a20100024100a7061a000f428707100801051a000f4252091a000f4293011a000f424b0d81a20100024100a7061a000f427607020801051a000f4252091a000f4292011a000f424f0d81a20100024101a6061a000f427507020801051a000f4252091a000f4293011a000f4250a6061a000f427307040801051a000f4252091a000f4293011a000f4250a6061a000f425707080801051a000f4252091a000f4293011a000f4250a6061a000f425a07100801051a000f4252091a000f4293011a000f4250a6061a000f427407d82d1a000f428b0801051a000f4252091a000f4293011a000f4250a7061a000f427007d82d1a000f428c0801051a000f4254091a000f4292011a000f424f0d81a201000243666f6fa7061a000f427007d82d1a000f428c0802051a000f4254091a000f4294011a000f424e0d82a201000243626172a201010244746f746fa6061a000f427007d82d1a000f428c0803051a000f4254091a000f4293011a000f4250a6061a000f427007d82d1a000f428c0804051a000f4254091a000f4293011a000f4250a8061a000f427207d82d1a000f428c0801051a000f4254091a000f42950a81a20100024110011a000f424d0d81a2010002426b3da7061a000f425e07d82d1a000f428c0801051a000f4253091a000f4292011a000f424f0d81a2010002411e18220518210318231a000f4297a4048fa7061a000f428307040801051a000f4252091a000f4292011a000f424f0d81a20100024106a7061a000f428007080801051a000f4252091a000f4292011a000f424f0d81a20100024100a7061a000f427c07140801051a000f4252091a000f4293011a000f424f0d81a20100024100a6061a000f427f07100801051a000f4252091a000f4293011a000f424ba7061a000f427e07080801051a000f4252091a000f4292011a000f424f0d81a2010002413aa7061a000f427d07080801051a000f4252091a000f4293011a000f424f0d81a201000241ffa7061a000f427b0718400801051a000f4252091a000f4294011a000f424e0d83a20100024820010db800000000a201010248fe80000000000000a20102024820010420c0dc1002a7061a000f427a0718400801051a000f4252091a000f4292011a000f424c0d81a2010002480000000000000079a7061a000f42780718400801051a000f4252091a000f4294011a000f424e0d83a20100024820010db800010000a201010248fe80000000000000a2010202482404680040040818a7061a000f42770718400801051a000f4252091a000f4292011a000f424f0d81a20100024800000000000007d4a7061a001e848607080801051a000f4252091a000f4292011a000f424f0d81a20100024180a7061a001e848307080801051a000f4252091a000f4292011a000f424f0d81a20100024100a7061a001e848207100801051a000f4252091a000f4293011a000f424b0d81a20100024100a7061a001e848407100801051a000f4252091a000f4293011a000f42500d81a20100024100a7061a001e848507100801051a000f4252091a000f4293011a000f42500d81a2010002410018220618210318231a000f4297a818220118210318231a000f4298021a000f4253181d1a000f429b03021403151a000f428ea818220218210318231a000f4298021a000f4253181d1a000f429b03021403151a000f428ea818220318210318231a000f4298021a000f4253181d1a000f429b03021403151a000f4290a818220418210318231a000f4298021a000f4253181d1a000f429b03021403151a000f4290a318220818210818231a000f4299')


rm    = RM.RuleManager()
rm.add_sid_file("ietf-schc@2022-10-09.sid")
rm.add_sid_file("ietf-schc-oam@2021-11-10.sid")
rm.Add_coreconf(dev_info=rule)
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
        node_type = yang_type[name_ref]

        if node_type == "int":
            return jcc
        elif node_type == "identifier":
            sid_ref = rm.sid_search_sid(jcc)
            return sid_ref
        elif node_type == "union":
            return str(jcc)
        else:
            raise ValueError(name_ref, "not a leaf")

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
