try:
    from _json_keys import *
    from _util import *
    from defs_L5 import dissectors_L5
except:
    from ._json_keys import *
    from ._util import *
    from .defs_L5 import dissectors_L5

hdr_map_udp = (
    (JK_UDP_SPORT, ">H", 0),
    (JK_UDP_DPORT, ">H", 0),
    (JK_UDP_LEN, ">H", 0),
    (JK_UDP_CKSUM, ">H", 0),
)

def dissect_udp(x):
    '''
    return { JK_PROTO:UDP, JK_HEADER:fld, JK_PAYLOAD:(dissectors_L5) }
    or
    return { JK_PROTO:UDP, JK_EMSG:(error-message) }
    '''
    this = {}
    this[JK_PROTO] = JK_UDP
    fld, offset, emsg = dissect_hdr(hdr_map_udp, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    this[JK_HEADER] = fld

    proto = None
    if fld[JK_UDP_SPORT] in dissectors_L5:
        proto = fld[JK_UDP_SPORT]
    elif fld[JK_UDP_DPORT] in dissectors_L5:
        proto = fld[JK_UDP_DPORT]
    if proto != None:
        this[JK_PAYLOAD] = dissectors_L5[proto](x[offset:])
        return this
    else:
        if len(x[offset:]) > 0:
            fld[JK_PAYLOAD] = x[offset:]
        this[JK_EMSG] = ("unsupported. L5 PORT=(%d, %d)" %
                         (fld[JK_UDP_SPORT], fld[JK_UDP_DPORT]))
        return this
