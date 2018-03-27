try:
    from _json_keys import *
    from _util import *
except:
    from ._json_keys import *
    from ._util import *

def dissect_coap(x):
    '''
    return { JK_PROTO:COAP, "HEADER":fld }
    or
    return { JK_PROTO:COAP, "EMSG":error-message }
    '''
    hdr = (
        (JK_COAP_VER,        "B", 2, 0),
        (JK_COAP_TYPE,       "B", 2, 0),
        (JK_COAP_TOKEN_LEN,  "B", 4, 0),
        (JK_COAP_CODE,       "B", 0, 0),
        (JK_COAP_MSGID,     ">H", 0, 0),
    )
    this = {}
    this[JK_PROTO] = JK_COAP
    fld, offset, emsg = dissect_hdr(hdr, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    if fld[JK_COAP_TOKEN_LEN] > 0:
        try:
            fld[JK_COAP_TOKEN] = x[:fld[JK_COAP_TOKEN_LEN]]
        except ValueError as e:
            this[JK_EMSG] = e
            return this
        offset += fld[JK_COAP_TOKEN_LEN]

    if len(x[offset:]) > 0:
        fld[JK_PAYLOAD] = x[offset:]

    this[JK_HEADER] = fld

    return this
