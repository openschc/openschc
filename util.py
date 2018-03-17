import struct

try:
    from json_keys import *
except:
    from .json_keys import *

def dissect_hdr(hdr_elm, x):
    '''
    hdr_elm: list of the header field format in tuple
    x: header in bytes

    return proto_hdr, offset, None
    or
    return None, offset, error-message
    '''
    hdr_flds = {}
    offset = 0
    for i in hdr_elm:
        fld_fmt = i[1]
        fld_size = struct.calcsize(fld_fmt)
        fld_name = i[0]
        if len(x[offset:]) < fld_size:
            emsg = ("invalid header length, rest:%d < hdr:%d" %
                    (len(x[offset:]), fld_size))
            return None, offset, emsg
        hdr_flds[fld_name] = struct.unpack(fld_fmt, x[offset:offset+fld_size])[0]
        offset += fld_size
    #
    return hdr_flds, offset, None

def ipv6addr(x):
    '''
    x: assuming the length is 16 bytes
    '''
    return ":".join(["%02x%02x"%(x[i],x[i+1]) for i in range(0,16,2)])

def ipv4addr(x):
    '''
    x: assuming the length is 16 bytes
    '''
    return ".".join(["%d"%x[i] for i in range(4)])

def macaddr(x):
    '''
    x: assuming the length is 6 bytes
    '''
    return "-".join(["%02x"%x[i] for i in range(6)])

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

def dump_pretty(a, indent="  ", l2=None):
    if l2:
        l2[JK_PAYLOAD] = a
        a = l2
    #
    ret = []
    for k in a.keys():
        if k in [JK_IPV6_SADDR, JK_IPV6_DADDR]:
            ret.append('%s"%s": "%s"' % (indent, k, ipv6addr(a[k])))
        elif k in [JK_IPV4_SADDR, JK_IPV4_DADDR]:
            ret.append('%s"%s": "%s"' % (indent, k, ipv4addr(a[k])))
        elif k in [JK_EN10MB_DMAC, JK_EN10MB_SMAC]:
            ret.append('%s"%s": "%s"' % (indent, k, macaddr(a[k])))
        elif isinstance(a[k], (bytes, bytearray)):
            ret.append('%s"%s": "%s"' %
                  (indent, k, "".join(["%02x"%i for i in a[k]])))
        elif isinstance(a[k], dict):
            ret.append('%s"%s": ' % (indent, k))
            ret.append(dump_pretty(a[k], indent=indent+"  "))
        else:
            ret.append('%s"%s": "%s"' % (indent, k, str(a[k])))
    return "\n".join(ret)

if __name__ == "__main__":
    print(ipv4addr([0x7f, 0, 0, 1]))
    print(ipv6addr(b"&\x07\xf8\xb0@\x0e\x0c\x04\x00\x00\x00\x00\x00\x00\x00_"))
    print(ipv6addr(b"\x00"*15 + b"\x01"))
