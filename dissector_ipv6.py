try:
    from _json_keys import *
    from _util import *
    from defs_L4 import dissectors_L4
except:
    from ._json_keys import *
    from ._util import *
    from .defs_L4 import dissectors_L4

hdr_map_ipv6 = (
    (JK_IPV6_VER,    ">I",  4,   6),
    (JK_IPV6_TC,     ">I",  8,   0),
    (JK_IPV6_FL,     ">I", 20,   0),
    (JK_IPV6_LEN,    ">H",  0,   0),
    (JK_IPV6_NXT,     "B",  0,   0),
    (JK_IPV6_HOP_LMT, "B",  0, 255),
    (JK_IPV6_SADDR, "16s",  0,   0),
    (JK_IPV6_DADDR, "16s",  0,   0)
)

def dissect_ipv6(x):
    '''
    return { JK_PROTO:IPV6, JK_HEADER:fld, JK_PAYLOAD:(dissectors_L4) }
    or
    return { JK_PROTO:IPV6, JK_EMSG:(error-message) }
    '''
    this = {}
    this[JK_PROTO] = JK_IPV6
    fld, offset, emsg = dissect_hdr(hdr_map_ipv6, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    # update the field
    fld[JK_IPV6_SADDR] = IPAddr(fld[JK_IPV6_SADDR])
    fld[JK_IPV6_DADDR] = IPAddr(fld[JK_IPV6_DADDR])

    this[JK_HEADER] = fld

    proto = fld[JK_IPV6_NXT]
    if proto in dissectors_L4:
        this[JK_PAYLOAD] = dissectors_L4[proto](x[offset:])
        return this
    else:
        this[JK_EMSG] = "unsupported. L4 proto=%d" % proto
        return this

