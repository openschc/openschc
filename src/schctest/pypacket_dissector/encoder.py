# -*- coding: utf-8 -*-

try:
    from _json_keys import *
    from _util import *
    from dissector_ipv6 import hdr_map_ipv6
    from dissector_ipv4 import hdr_map_ipv4
    from dissector_icmpv6 import hdr_map_icmpv6
    from dissector_udp import hdr_map_udp
    from dissector_coap import hdr_map_coap
except:
    from ._json_keys import *
    from ._util import *
    from .dissector_ipv6 import hdr_map_ipv6
    from .dissector_ipv4 import hdr_map_ipv4
    from .dissector_icmpv6 import hdr_map_icmpv6
    from .dissector_udp import hdr_map_udp
    from .dissector_coap import hdr_map_coap

encode_hdr_map = {
    JK_IPV6: hdr_map_ipv6,
    JK_IPV4: hdr_map_ipv4,
    JK_ICMPV6: hdr_map_icmpv6,
    JK_UDP: hdr_map_udp,
    JK_COAP: hdr_map_coap,
}

def encode_hdr(hdr_map, hdr_list):
    '''
    hdr_map is defined each protocol.
    hdr_list must be OrderedDict.
    '''
    def get_elm(k0):
        for k, v in hdr_list.items():
            if k0 == k:
                return v
        return None
    # 
    ba = bytearray(0)
    offset = 0
    fld_size_prev = 0
    fld_fmt_prev = None
    fld_v = None
    for i in hdr_map:
        fld_name = i[0]
        if fld_name == JK_SW:
            if hdr_list.get(i[1], None) != i[2]:
                # just skip it
                continue
            # otherwise
            _ba = encode_hdr(i[3], hdr_list)
            ba += _ba
            continue
        #
        fld_fmt = i[1]
        fld_size = struct.calcsize(fld_fmt)
        fld_bits = i[2]
        fld_def = i[3]
        if 8*fld_size < fld_bits:
            raise ValueError("fld_bits is bigger than fld_size. {:d} > {:d}".
                             format(fld_bits, 8*fld_size))
        if fld_bits == 0 and fld_size_prev != 0:
            # flush the fld_v to the header.
            # move offset and finish the operation for a field.
            ba += struct.pack(fld_fmt_prev, fld_v)
            fld_v = None
            fld_fmt_prev = None
            offset += fld_size_prev
            fld_size_prev = 0
        # get the value.
        v = get_elm(fld_name)
        if v is None:
            raise ValueError("{:s} is not found in the map.".format(fld_name))
        # set the value to the bytearray.
        if fld_bits:
            if fld_v is None:
                # initialize if None
                fld_v = 0
                fld_fmt_prev = fld_fmt
                fld_size_prev = fld_size
            # the value is in bits.
            fld_v <<= fld_bits
            fld_v |= v
            continue
        # otherwise
        if isinstance(v, (IPAddr, MACAddr)):
            v = v.decode()
        ba += struct.pack(fld_fmt, v)
    #
    return ba

def encoder(jo, hm=encode_hdr_map):
    if isinstance(jo, (bytes, bytearray)):
        return jo
    #
    proto = jo.get(JK_PROTO)
    header = jo.get(JK_HEADER)
    payload = jo.get(JK_PAYLOAD)
    if not proto:
        raise ValueError("protocol is not defined.")
    if not header:
        raise ValueError("header is not defined.")
    hdr_map = hm.get(proto)
    if not hdr_map:
        raise ValueError("unknown protocol {:s}".format(proto))
    ba = encode_hdr(hdr_map, header)
    if ba == None:
        raise ValueError("error in {:s}".format(proto))
    if payload:
        ba += encoder(payload)
    return ba

