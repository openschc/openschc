import struct
import json
import ipaddress
from collections import OrderedDict
from binascii import a2b_hex

try:
    from _json_keys import *
except:
    from ._json_keys import *

def dissect_hdr(hdr_map, x):
    '''
    hdr_map: list of the header field format in tuple
        (name, format, bits, default)
    x: header in bytes

    if bits is not zero, it takes a series of bits from the field.
    in this case, offset is not proceeded.

    return proto_hdr, offset, None
    or
    return None, offset, error-message
    '''
    hdr_ret = {}
    offset = 0
    bit_shift = None
    fld_size_prev = 0
    for i in hdr_map:
        fld_name = i[0]
        if fld_name == JK_SW:
            if hdr_ret[i[1]] != i[2]:
                # just skip it
                continue
            # otherwise
            _hdr, _size, _emsg = dissect_hdr(i[3], x[offset:])
            if _hdr is None:
                return _hdr, _size, _emsg
            offset += _size
            hdr_ret.update(_hdr)
            continue
        #
        fld_fmt = i[1]
        fld_size = struct.calcsize(fld_fmt)
        fld_bits = i[2]
        if fld_bits == 0 and fld_size_prev != 0:
            # move offset and finish the operation for a field.
            offset += fld_size_prev
            fld_size_prev = 0
            bit_shift = None
        if len(x[offset:]) < fld_size:
            emsg = ("invalid header length, rest:%d < hdr:%d" %
                    (len(x[offset:]), fld_size))
            return None, offset, emsg
        # get a value from the field.
        if fld_bits:
            # the value is in bits.
            v = struct.unpack(fld_fmt, x[offset:offset+fld_size])[0]
            mask = int("1"*fld_bits,2)
            if bit_shift is None:
                # init
                bit_shift = 8*fld_size
            bit_shift -= fld_bits
            hdr_ret[fld_name] = (v>>bit_shift)&mask
            fld_size_prev = fld_size
            continue
        # otherwise
        hdr_ret[fld_name] = struct.unpack(fld_fmt, x[offset:offset+fld_size])[0]
        offset += fld_size
    #
    return hdr_ret, offset, None

class IPAddr():
    def __init__(self, *args, **kwargs):
        a = args[0]
        if isinstance(a, (bytes, bytearray)):
            # if the arg is binary, converting it into a string.
            a = str(ipaddress.ip_address(a))
        self.value = a
        self.addr = ipaddress.ip_address(a)

    def __str__(self):
        return str(self.addr)

    def __repr__(self):
        return "'" + self.__str__() + "'"

    def decode(self):
        return self.addr.packed

    def asis(self):
        return self.value

class MACAddr():
    def __init__(self, *args, **kwargs):
        self.value = args[0]
        v = self.value.replace(":","").replace("-","").replace(".","")
        self.addr = bytearray(a2b_hex(v))

    def __str__(self):
        return "-".join(["%02x"%self.addr[i] for i in range(6)])

    def __repr__(self):
        return "'" + self.__str__() + "'"

    def decode(self):
        return self.addr

    def asis(self):
        return self.value

def _de_hook(obj):
    ret = OrderedDict()
    for k, v in obj.items():
        if k in [JK_IPV4_SADDR, JK_IPV4_DADDR]:
            ret[k] = IPAddr(v)
        elif k in [JK_IPV6_SADDR, JK_IPV6_DADDR]:
            ret[k] = IPAddr(v)
        elif k in ["EN10MB.DMAC", "EN10MB.SMAC"]:
            ret[k] = MACAddr(v)
        elif k == JK_PAYLOAD and isinstance(v, str):
            ret[k] = bytearray(a2b_hex(v))
        else:
            ret[k] = v
    return ret

def _json_decode_hook(obj):
    return _de_hook(OrderedDict(obj))

def _json_encode_hook(obj):
    if isinstance(obj, (bytes, bytearray)):
        return "".join(["%02x"%i for i in obj])
    elif isinstance(obj, (IPAddr,MACAddr)):
        return str(obj)
    else:
        return "TBD" + str(obj)

def dumps(l3, indent=4, l2=None, ts=None):
    '''
    l3, l2: dict
    ts: dict, i.e. {"TS": ts}
    '''
    obj = OrderedDict()
    if ts:
        obj.update(ts)
    if l2 is not None:
        l2[JK_PAYLOAD] = l3
        obj.update(l2)
    else:
        obj.update(l3)
    #
    return json.dumps(obj, indent=indent, default=_json_encode_hook)

def dump_byte(x):
    return "".join([ " %02x"%x[i] if i and i%4==0 else "%02x"%x[i]
                   for i in range(len(x)) ])

def load_json_packet(jo):
    '''
    load a packet data in json and convert it into the OrderedDict.
    '''
    return json.loads(jo, object_pairs_hook=_json_decode_hook)

