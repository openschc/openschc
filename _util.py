import struct
import json
import ipaddress
from collections import OrderedDict
from binascii import a2b_hex

try:
    from _json_keys import *
except:
    from ._json_keys import *

DELIMITER = "00ff707970636170ff00" # b"\x00\xffpypcap\xff\x00"

def dissect_hdr(hdr_elm, x):
    '''
    hdr_elm: list of the header field format in tuple
        (name, format, bits, default)
    x: header in bytes

    if bits is not zero, it takes a series of bits from the field.
    in this case, offset is not proceeded.

    return proto_hdr, offset, None
    or
    return None, offset, error-message
    '''
    hdr_flds = {}
    offset = 0
    fld_size_prev = 0
    for i in hdr_elm:
        fld_name = i[0]
        fld_fmt = i[1]
        fld_size = struct.calcsize(fld_fmt)
        fld_bits = i[2]
        if fld_bits == 0 and fld_size_prev != 0:
            offset += fld_size_prev
            fld_size_prev = 0
        if len(x[offset:]) < fld_size:
            emsg = ("invalid header length, rest:%d < hdr:%d" %
                    (len(x[offset:]), fld_size))
            return None, offset, emsg
        if fld_bits:
            v = struct.unpack(fld_fmt, x[offset:offset+fld_size])[0]
            mask = int("1"*fld_bits,2)
            hdr_flds[fld_name] = (v>>(8*fld_size-fld_bits))&mask
            fld_size_prev = fld_size
            continue
        # otherwise
        hdr_flds[fld_name] = struct.unpack(fld_fmt, x[offset:offset+fld_size])[0]
        offset += fld_size
    #
    return hdr_flds, offset, None

class IPAddr(str):
    def __init__(self, *args, **kwargs):
        self.value = args[0]
        self.addr = ipaddress.ip_address(args[0])

    def __str__(self):
        return str(self.addr)

    def decode(self):
        return self.addr.packed

    def asis(self):
        return self.value

class MACAddr(str):
    def __init__(self, *args, **kwargs):
        self.value = args[0]
        v = self.value.replace(":","").replace("-","").replace(".","")
        self.addr = a2b_hex(v)

    def __str__(self):
        return "-".join(["%02x"%self.addr[i] for i in range(6)])

    def decode(self):
        return self.addr

    def asis(self):
        return self.value

def contains(tag, pkt):
    '''
    tag: string like "ICMPV6"
    pkt: dissected
    '''
    def _contains(tag, pkt):
        if pkt == None:
            return False
        if tag in pkt[JK_PROTO]:
            return True
        if tag in list(pkt[JK_HEADER].keys()):
            return True
        return _contains(tag, pkt.get(JK_PAYLOAD))
    # main
    if not (tag and pkt):
        return False
    if isinstance(tag, list):
        for i in tag:
            return _contains(i, pkt)
    else:
        return _contains(tag, pkt)

def dump_byte(x):
    return "".join([ " %02x"%x[i] if i and i%4==0 else "%02x"%x[i]
                   for i in range(len(x)) ])

def _de_hook(obj):
    ret = OrderedDict()
    for k, v in obj.items():
        if k in ["IPV4.SADDR", "IPV4.DADDR"]:
            ret[k] = IPAddr(v)
        elif k in ["IPV6.SADDR", "IPV6.DADDR"]:
            ret[k] = IPAddr(v)
        elif k in ["EN10MB.DMAC", "EN10MB.SMAC"]:
            ret[k] = MACAddr(v)
        elif k == "PAYLOAD" and isinstance(v, str):
            ret[k] = a2b_hex(v)
        else:
            ret[k] = v
    return ret

def _json_decode_hook(obj):
    return _de_hook(OrderedDict(obj))

def _json_encode_hook(obj):
    if isinstance(obj, (bytes, bytearray)):
        return "".join(["%02x"%i for i in obj])
    else:
        return obj

def dump_pretty(a, indent=4, l2=None):
    if l2 is not None:
        l2[JK_PAYLOAD] = a
        a = l2
    #
    return json.dumps(a, indent=indent, default=_json_encode_hook)

def load_json_packet(jo):
    return json.loads(jo, object_pairs_hook=_json_decode_hook)

if __name__ == "__main__":
    j = load_json_packet('''
    {
    "PROTO": "IPV6",
    "HEADER": [
        { "IPV6.VER": 6 },
        { "IPV6.TC": 96 },
        { "IPV6.FL": 694078 },
        { "IPV6.LEN": 14 },
        { "IPV6.NXT": 17 },
        { "IPV6.HOP_LMT": 64 },
        { "IPV6.SADDR": "fe80:0000:0000:0000:aebc:32ff:feba:1c9f" },
        { "IPV6.DADDR": "fe80:0000:0000:0000:0201:c0ff:fe06:3e69" } ],
    "PAYLOAD": {
        "PROTO": "UDP",
        "HEADER": [
        { "UDP.SPORT": 50145 },
        { "UDP.DPORT": 9999 },
        { "UDP.LEN": 14 },
        { "UDP.CKSUM": 63356 } ],
        "PAYLOAD": "48656c6c6f0a" }
    }
    ''')
    print(j)
    print(dump_pretty(j))
