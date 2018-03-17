from json_keys import *
from util import *

def dissect_icmpv6(x):
    '''
    return { JK_PROTO:ICMPV6, "HEADER":fld }
    or
    return { JK_PROTO:ICMPV6, "EMSG":error-message }
    '''
    hdr = (
        (JK_ICMPV6_TYPE, "B", 0),
        (JK_ICMPV6_CODE, "B", 0),
        (JK_ICMPV6_CKSUM, ">H", 0)
    )
    this = {}
    this[JK_PROTO] = JK_ICMPV6
    fld, offset, emsg = dissect_hdr(hdr, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    # ICMPv6 Echo Request/Reply
    if fld[JK_ICMPV6_TYPE] == 128:
        fld[JK_ICMPV6_IDENT] = struct.unpack(">H", x[offset:offset+2])[0]
        offset += 2
        fld[JK_ICMPV6_SEQNO] = struct.unpack(">H", x[offset:offset+2])[0]
        offset += 2

    if len(x[offset:]) > 0:
        fld[JK_PAYLOAD] = x[offset:]

    this[JK_HEADER] = fld

    return this

