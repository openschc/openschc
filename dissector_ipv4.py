try:
    from _json_keys import *
    from _util import *
    from defs_L4 import dissectors_L4
except:
    from ._json_keys import *
    from ._util import *
    from .defs_L4 import dissectors_L4

def dissect_ipv4(x):
    '''
    return { JK_PROTO:IPV4, JK_HEADER:fld, JK_PAYLOAD:dissectors_L4 }
    or
    return { JK_PROTO:IPV4, JK_EMSG:error-message }
    '''
    key_f_foff = "f_foff"
    key_v_ihl = "f_v_ihl"
    hdr = (
        (key_v_ihl, "B", 0x40),
        (JK_IPV4_TOS, "B", 0),
        (JK_IPV4_LEN, ">H", 0),
        (JK_IPV4_IDENT, ">H", 0),
        (key_f_foff, ">H", 0),
        (JK_IPV4_TTL, "B", 0),
        (JK_IPV4_NXT, "B", 0),
        (JK_IPV4_CKSUM, ">H", 0),
        (JK_IPV4_SADDR, "4s", b"\x00" * 4),
        (JK_IPV4_DADDR, "4s", b"\x00" * 4),
    )
    this = {}
    this[JK_PROTO] = JK_IPV4
    fld, offset, emsg = dissect_hdr(hdr, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    fld[JK_IPV4_VER] = (fld[key_v_ihl]>>4)&0x0f
    fld[JK_IPV4_HDR_LEN] = (fld[key_v_ihl])&0x0f
    fld[JK_IPV4_FLAG] = (fld[key_f_foff]>>5)&0x07
    fld[JK_IPV4_OFFSET] = (fld[key_f_foff])&0x1fff
    del(fld[key_v_ihl])
    del(fld[key_f_foff])

    this[JK_HEADER] = fld

    proto = fld[JK_IPV4_NXT]
    if proto in dissectors_L4:
        this[JK_PAYLOAD] = dissectors_L4[proto](x[offset:])
        return this
    else:
        this[JK_EMSG] = "unsupported. L4 proto=%d" % proto
        return this
