from json_keys import *
from util import *

def dissect_coap(x):
    '''
    return { JK_PROTO:COAP, "HEADER":fld }
    or
    return { JK_PROTO:COAP, "EMSG":error-message }
    '''
    tag_v_t_tkl = "v_t_tkl"
    hdr = (
        (tag_v_t_tkl, "B", 0),
        (JK_COAP_CODE, "B", 0),
        (JK_COAP_MSGID, ">H", 0),
    )
    this = {}
    this[JK_PROTO] = JK_COAP
    fld, offset, emsg = dissect_hdr(hdr, x)
    if fld == None:
        this[JK_EMSG] = emsg
        return this

    fld[JK_COAP_VER] = (fld[tag_v_t_tkl]>>6)&0x03
    fld[JK_COAP_TYPE] = (fld[tag_v_t_tkl]>>4)&0x03
    fld[JK_COAP_TOKEN_LEN] = (fld[tag_v_t_tkl])&0x07
    del(fld[tag_v_t_tkl])

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
