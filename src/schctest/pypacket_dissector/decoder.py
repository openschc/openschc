try:
    from _json_keys import *
    from _util import *
    from defs_L3 import dissectors_L3
except:
    from ._json_keys import *
    from ._util import *
    from .defs_L3 import dissectors_L3

def decoder(x):
    '''
    return (dissectors_L3)
    or
    return { JK_EMSG:(error-message) }
    '''
    this = None
    # only show ipv6 packets
    if len(x) < 1:
        return { JK_EMSG:"invalid packet length" }

    proto = (x[0]&0xf0)>>4
    if proto in dissectors_L3:
        if this != None:
            this[JK_PAYLOAD] = dissectors_L3[proto](x)
            return this
        else:
            return dissectors_L3[proto](x)
    else:
        return { JK_EMSG:"unsupported. L3 proto=%d" % proto }

