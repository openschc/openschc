try:
    from _json_keys import *
    from _util import *
except:
    from ._json_keys import *
    from ._util import *

hdr_map_coap = (
    (JK_COAP_VER,        "B", 2, 0),
    (JK_COAP_TYPE,       "B", 2, 0),
    (JK_COAP_TOKEN_LEN,  "B", 4, 0),
    (JK_COAP_CODE,       "B", 0, 0),
    (JK_COAP_MSGID,     ">H", 0, 0),
)

def dissect_coap(x):
    '''
    return { JK_PROTO:COAP, "HEADER":fld }
    or
    return { JK_PROTO:COAP, "EMSG":error-message }
    '''
    this = {}
    this[JK_PROTO] = JK_COAP
    fld, offset, emsg = dissect_hdr(hdr_map_coap, x)
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

    this[JK_HEADER] = fld

    if len(x[offset:]) > 0:
        this[JK_PAYLOAD] = x[offset:]

    return this
