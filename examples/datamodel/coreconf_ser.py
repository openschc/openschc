import binascii
import cbor2 as cbor
import json

rules = "a11a000f429ea10183a4048aa7061a000f428307040801051a000f4252091a000f4292011a000f424f0d81a20100\
024106a7061a000f428007080801051a000f4252091a000f4292011a000f424f0d81a201000240a7061a000f427c071408010\
51a000f4252091a000f4293011a000f424f0d81a201000240a6061a000f427f07100801051a000f4252091a000f4293011a000\
f424ba7061a000f427e07080801051a000f4252091a000f4292011a000f424f0d81a2010002413aa7061a000f427d070808010\
51a000f4252091a000f4293011a000f424f0d81a201000241ffa7061a000f427b0718400801051a000f4252091a000f4292011\
a000f424f0d81a201000248200104701f2101d2a7061a000f427a0718400801051a000f4252091a000f4292011a000f424f0d81\
a2010002480000000000000001a6061a000f42780718400801051a000f4252091a000f4293011a000f4250a6061a000f427707\
18400801051a000f4252091a000f4293011a000f425018220618210318231a000f4297a818220c18210b18231a000f4298021\
a000f4254181d1a000f429a03021403151a000f4290a31822186418210818231a000f4299"

sor = binascii.unhexlify(rules)
sids = []

sor_mem = cbor.loads(sor)

dm_keys = {
    1000095 : [1000129, 1000128], # rule : rule-id-length, rule-id-value
    1000099 : [1000105, 1000107, 1000104], # entry : field-id, field-position, direction-indicator
    1000112 : [1000113]
}

def lookfor_sid(sid, namespace="data"):
    for e in sids:
        for s in e["items"]:
            if s["namespace"] == namespace and s["sid"] == sid:
                return s["identifier"]

    return None

def add_sid_file(name):
    with open(name) as sid_file:
        sid_values = json.loads(sid_file.read())

    sids.append(sid_values)    

def dump_cc (sor, delta=0, ident=0):
    if type(sor) is dict:
        for e in sor:
            print (" "*ident, lookfor_sid(e+delta), '(', e+delta, ')',  end="")
            if type(sor[e]) is int:
                if sor[e] > 1000000:
                    print (": ", lookfor_sid(sor[e], namespace="identity"), '(', sor[e], ')')
                else: 
                    print (' -> ', sor[e]) 
            elif type(sor[e]) is bytes:
                print (' -> ', sor[e])
            else:
                print ()
                dump_cc(sor[e], delta=e+delta, ident=ident+1)
    elif type(sor) is list:
        for x in sor:
            #print (" "*ident, "="*20)
            dump_cc(x, delta=delta, ident=ident+1)
    else:
        print ("unknown type", type(sor), sor)

def get_cc (sor, sid=None, keys = [], delta=0, ident=0, value=None):
    if type(sor) is dict:
        for e in sor:
            if e+delta == sid:
                if value == None:
                    return {e+delta: sor[e]} 
                else:
                    sor[e] = value
                    return True

            if type(sor[e]) is list:
                if e+delta in dm_keys:
                    key_search = {}
                    for k in dm_keys[e+delta]:
                        key_search[k-(e+delta)] = keys.pop(0)
                    
                    found_st = None
                    for l in sor[e]:
                        if key_search.items() <= l.items():
                            found_st = l
                            break
                    if found_st:
                        return get_cc(l, delta=e+delta, ident=ident+1, sid=sid, keys=keys, value=value)
                    else:
                        raise ValueError ("not found mapping")

            if type(sor[e]) is dict:
                return get_cc(sor[e], delta=e+delta, ident=ident+1, sid=sid, keys=keys, value=value)
    else:
        print ("unknown type", type(sor), sor)

add_sid_file("ietf-schc@2022-07-22.sid")

#dump_cc(sor_mem)
r=get_cc(sor_mem, sid=1000130, keys=[100, 8]) # get nature for rule-id

dump_cc (r)

r=get_cc(sor_mem, sid=1000112, keys=[6, 3, 1000067, 1, 1000018]) # get the full TV for rule 6/3 and ipv6-version

dump_cc (r)

r=get_cc(sor_mem, sid=1000114, keys=[6, 3, 1000067, 1, 1000018, 0]) # get the value TV for rule 6/3 and ipv6-version

dump_cc (r)

print (binascii.hexlify(cbor.dumps(sor_mem)))

r=get_cc(sor_mem, sid=1000114, keys=[6, 3, 1000067, 1, 1000018, 0], value=b'04') # write ipv6 version to 4

r=get_cc(sor_mem, sid=1000114, keys=[6, 3, 1000067, 1, 1000018, 0]) # get the value TV for rule 6/3 and ipv6-version

dump_cc (r)


print (binascii.hexlify(cbor.dumps(sor_mem)))

import pprint

pprint.pprint(sor_mem)