try:
    from _json_keys import *
    from _util import *
    from defs_L4 import dissectors_L4
except:
    from ._json_keys import *
    from ._util import *
    from .defs_L4 import dissectors_L4

hdr_map_ipv4 = (
    (JK_IPV4_VER,      "B",  4, 4),
    (JK_IPV4_HDR_LEN,  "B",  4, 0),
    (JK_IPV4_TOS,      "B",  0, 0),
    (JK_IPV4_LEN,     ">H",  0, 0),
    (JK_IPV4_IDENT,   ">H",  0, 0),
    (JK_IPV4_FLAG,    ">H",  3, 0),
    (JK_IPV4_OFFSET,  ">H", 13, 0),
    (JK_IPV4_TTL,      "B",  0, 255),
    (JK_IPV4_NXT,      "B",  0, 0),
    (JK_IPV4_CKSUM,   ">H",  0, 0),
    (JK_IPV4_SADDR,   "4s",  0, 0),
    (JK_IPV4_DADDR,   "4s",  0, 0),
)

def dissect_ipv4(x):
    '''
    return { JK_PROTO:IPV4, JK_HEADER:fld, JK_PAYLOAD:dissectors_L4 }
    or
    return { JK_PROTO:IPV4, JK_EMSG:error-message }
    '''
    this = {}
    this[JK_PROTO] = JK_IPV4
    fld, offset, emsg = dissect_hdr(hdr_map_ipv4, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    this[JK_HEADER] = fld

    proto = fld[JK_IPV4_NXT]
    if proto in dissectors_L4:
        this[JK_PAYLOAD] = dissectors_L4[proto](x[offset:])
        return this
    else:
        this[JK_EMSG] = "unsupported. L4 proto=%d" % proto
        return this
