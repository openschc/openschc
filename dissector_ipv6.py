try:
    from _json_keys import *
    from _util import *
    from defs_L4 import dissectors_L4
except:
    from ._json_keys import *
    from ._util import *
    from .defs_L4 import dissectors_L4

def dissect_ipv6(x):
    '''
    return { JK_PROTO:IPV6, JK_HEADER:fld, JK_PAYLOAD:(dissectors_L4) }
    or
    return { JK_PROTO:IPV6, JK_EMSG:(error-message) }
    '''
    key_v_tc_fl = "v_tc_fl"
    hdr = (
        (key_v_tc_fl, ">I", 0x60000000),
        (JK_IPV6_LEN, ">H", 0),
        (JK_IPV6_NXT, "B", 0),
        (JK_IPV6_HOP_LMT, "B", 0),
        (JK_IPV6_SADDR, "16s", b"\x00" * 16),
        (JK_IPV6_DADDR, "16s", b"\x00" * 16),
    )
    this = {}
    this[JK_PROTO] = JK_IPV6
    fld, offset, emsg = dissect_hdr(hdr, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    fld[JK_IPV6_VER] = (fld[key_v_tc_fl]>>28)
    fld[JK_IPV6_TC] = (fld[key_v_tc_fl]>>24)&0x0ff
    fld[JK_IPV6_FL] = fld[key_v_tc_fl]&0x0fffff
    del(fld[key_v_tc_fl])

    this[JK_HEADER] = fld

    proto = fld[JK_IPV6_NXT]
    if proto in dissectors_L4:
        this[JK_PAYLOAD] = dissectors_L4[proto](x[offset:])
        return this
    else:
        this[JK_EMSG] = "unsupported. L4 proto=%d" % proto
        return this

