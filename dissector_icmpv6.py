try:
    from _json_keys import *
    from _util import *
except:
    from ._json_keys import *
    from ._util import *

hdr_map_icmpv6 = (
    (JK_ICMPV6_TYPE,   "B", 0, 0),
    (JK_ICMPV6_CODE,   "B", 0, 0),
    (JK_ICMPV6_CKSUM, ">H", 0, 0),
    (JK_SW, JK_ICMPV6_TYPE, 128, (
        (JK_ICMPV6_IDENT, ">H", 0, 0),
        (JK_ICMPV6_SEQNO, ">H", 0, 0),
     )),
    (JK_SW, JK_ICMPV6_TYPE, 129, (
        (JK_ICMPV6_IDENT, ">H", 0, 0),
        (JK_ICMPV6_SEQNO, ">H", 0, 0),
     ))
)

def dissect_icmpv6(x):
    '''
    return { JK_PROTO:ICMPV6, "HEADER":fld }
    or
    return { JK_PROTO:ICMPV6, "EMSG":error-message }
    '''
    this = {}
    this[JK_PROTO] = JK_ICMPV6
    fld, offset, emsg = dissect_hdr(hdr_map_icmpv6, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    this[JK_HEADER] = fld

    if len(x[offset:]) > 0:
        this[JK_PAYLOAD] = x[offset:]

    return this

