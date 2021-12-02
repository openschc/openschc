"""
.. module:: compr_core
   :platform: Python, Micropython
"""
from gen_base_import import *
from gen_utils import dprint

import pprint

T_RULEID = "RuleID"
T_RULEIDLENGTH = "RuleIDLength"
T_DEVICEID = "DeviceID"

T_PROTO = "BACNET"
T_BACNET_FID = "BACNET.FID"
T_BACNET_FL = "BACNET.FL"
T_BACNET_FP = "BACNET.FP"
T_BACNET_DI = "BACNET.DI"
T_BACNET_TV = "BACNET.TV"
T_BACNET_MO = "BACNET.MO"
T_BACNET_MO_VAL = "BACNET.MO.VAL"
T_BACNET_CDA = "BACNET.CDA"
T_BACNET_SB = "BACNET.SB"

T_PROTO_IPV4 = "IPV4"
T_IPV4_VER = "IPV4.VER"
T_IPV4_IHL = "IPV4.IHL"
T_IPV4_DF = "IPV4.DF"
T_IPV4_LEN = "IPV4.LEN"
T_IPV4_ID = "IPV4.ID"
T_IPV4_FLAG = "IPV4.FLAG"
T_IPV4_OFF = "IPV4.OFF"
T_IPV4_LEN = "IPV4.LEN"
T_IPV4_TTL = "IPV4.TTL"
T_IPV4_PROTO = "IPV4.PROTO"
T_IPV4_CKSUM = "IPV4.CKSUM"
T_IPV4_APP_ADDR = "IPV4.APP_ADDR"
T_IPV4_DEV_ADDR = "IPV4.DEV_ADDR"


T_PROTO_IPV6 = "IPV6"
T_IPV6_VER = "IPV6.VER"
T_IPV6_TC = "IPV6.TC"
T_IPV6_FL = "IPV6.FL"
T_IPV6_LEN = "IPV6.LEN"
T_IPV6_NXT = "IPV6.NXT"
T_IPV6_HOP_LMT = "IPV6.HOP_LMT"
T_IPV6_DEV_PREFIX = "IPV6.DEV_PREFIX"
T_IPV6_DEV_IID = "IPV6.DEV_IID"
T_IPV6_APP_PREFIX = "IPV6.APP_PREFIX"
T_IPV6_APP_IID = "IPV6.APP_IID"

T_PROTO_ICMPV6 = "ICMPV6"
T_ICMPV6_TYPE = "ICMPV6.TYPE"
T_ICMPV6_CODE = "ICMPV6.CODE"
T_ICMPV6_CKSUM = "ICMPV6.CKSUM"
T_ICMPV6_IDENT = "ICMPV6.IDENT"
T_ICMPV6_SEQNO = "ICMPV6.SEQNO"

T_PROTO_UDP = "UDP"
T_UDP_DEV_PORT = "UDP.DEV_PORT"
T_UDP_APP_PORT = "UDP.APP_PORT"
T_UDP_LEN = "UDP.LEN"
T_UDP_CKSUM = "UDP.CKSUM"

T_PROTO_COAP = "COAP"
T_COAP_VERSION = "COAP.VER"
T_COAP_TYPE = "COAP.TYPE"
T_COAP_TKL = "COAP.TKL"
T_COAP_CODE = "COAP.CODE"
T_COAP_MID = "COAP.MID"
T_COAP_TOKEN = "COAP.TOKEN"

# WARNING: CoAP option string must be writen exactly as in standards and IANA
T_COAP_OPT_IF_MATCH =  "COAP.If-Match"
T_COAP_OPT_URI_HOST = "COAP.Uri-Host"
T_COAP_OPT_ETAG = "COAP.ETag"
T_COAP_OPT_IF_NONE_MATCH =  "COAP.If-None-Match"
T_COAP_OPT_OBS =  "COAP.Observe"
T_COAP_OPT_URI_PORT =  "COAP.Uri-Port"
T_COAP_OPT_LOC_PATH = "COAP.Location-Path"
T_COAP_OPT_URI_PATH =  "COAP.Uri-Path"
T_COAP_OPT_CONT_FORMAT =  "COAP.Content-Format"
T_COAP_OPT_MAX_AGE =  "COAP.Max-Age"
T_COAP_OPT_URI_QUERY =  "COAP.Uri-Query"
T_COAP_OPT_ACCEPT =  "COAP.Accept"
T_COAP_OPT_LOC_QUERY =  "COAP.Location-Query"
T_COAP_OPT_BLOCK2 =  "COAP.Block2"
T_COAP_OPT_BLOCK1 =  "COAP.Block1"
T_COAP_OPT_SIZE2 =  "COAP.Size2"
T_COAP_OPT_PROXY_URI =  "COAP.Proxy-Uri"
T_COAP_OPT_PROXY_SCHEME =  "COAP.Proxy-Scheme"
T_COAP_OPT_SIZE1 =  "COAP.Sizel"
T_COAP_OPT_NO_RESP = "COAP.No-Response"

T_BACNET_VLC_TYPE = "BACnet.type"
T_BACNET_VLC_FUN = "BACnet.fun"
T_BACNET_VLC_LEN = "BACnet.len"

T_BACNET_NPDU_VER = "BACnet.NPDU.ver"
T_BACNET_NPDU_CTRL = "BACnet.NPDU.ctrl"

T_BACNET_APDU_TYPE = "BACnet.APDU.type"
T_BACNET_APDU_SER = "BACnet.APDU.ser"
T_BACNET_APDU_PID = "BACnet.APDU.pid"
T_BACNET_APDU_DEVID = "BACnet.APDU.devid"
T_BACNET_APDU_OBJID = "BACnet.APDU.objid"
T_BACNET_APDU_TRE = "BACnet.APDU.tre"
T_BACNET_APDU_VALS = "BACnet.APDU.vals"


T_FUNCTION_VAR = "var"
T_FUNCTION_TKL = "tkl"


T_DIR_UP = "UP"
T_DIR_DW = "DW"
T_DIR_BI = "BI"

T_MO_EQUAL = "EQUAL"
T_MO_IGNORE = "IGNORE"
T_MO_MSB = "MSB"
T_MO_MMAP = "MATCH-MAPPING"

T_CDA_NOT_SENT = "NOT-SENT"
T_CDA_VAL_SENT = "VALUE-SENT"
T_CDA_MAP_SENT = "MAPPING-SENT"
T_CDA_LSB = "LSB"
T_CDA_COMP_LEN = "COMPUTE-LENGTH"
T_CDA_COMP_CKSUM = "COMPUTE-CHECKSUM"
T_CDA_DEVIID = "DEVIID"
T_CDA_APPIID = "APPIID"

T_ALGO = "ALGO"
T_ALGO_DIRECT = "DIRECT"
T_ALGO_COAP_OPT = "COAP_OPTION"

T_META = "META"
T_UP_RULES = "UP_RULES"
T_DW_RULES = "DW_RULES"

T_ACTION = "Action"

T_COMP = "Compression"
T_NO_COMP = "NoCompression"
T_FRAG = "Fragmentation"
T_FRAG_MODE = "FRMode"
T_FRAG_NO_ACK = "NoAck"
T_FRAG_ACK_ALWAYS = "AckAlways"
T_FRAG_ACK_ON_ERROR = "AckOnError"
T_FRAG_DIRECTION = "FRDirection"
T_FRAG_PROF = "FRModeProfile"
T_FRAG_DTAG = "dtagSize" # XXX: should be T_FRAG_DTAG_SIZE
T_FRAG_W = "WSize" # XXX: should be T_FRAG_W_SIZE
T_FRAG_FCN = "FCNSize"
T_FRAG_WINDOW_SIZE = "windowSize"
T_FRAG_ACK_BEHAVIOR = "ackBehavior"
T_FRAG_TILE = "tileSize"
T_FRAG_MIC = "MICALgorithm"
T_FRAG_MAX_RETRY = "maxRetry"
T_FRAG_TIMEOUT  = "timeout"
T_FRAG_L2WORDSIZE = "L2WordSize"
T_FRAG_LAST_TILE_IN_ALL1 = "lastTileInAll1"
T_FRAG_RFC8724 = "RCS_RFC8724"

T_POSITION_CORE = "core"
T_POSITION_DEVICE = "device"


SID = 100000

YANG_ID = {
    "TBD" : [SID+1, "RCS-algorithm-base-type"],
    T_FRAG_RFC8724 : [SID+2, "rcs-RFC8724"],
    "TBD" : [SID+3, "ack-behavior-after-All0"],
    "TBD" : [SID+4, "ack-behavior-after-All1"],
    "TBD" : [SID+5, "ack-behavior-always"],
    "TBD" : [SID+6, "ack-behavior-base-type"],
    "TBD" : [SID+7, "all1-data-base-type"],
    "TBD" : [SID+8, "all1-data-no"],
    "TBD" : [SID+9, "all1-data-sender-choice"],
    "TBD" : [SID+10, "all1-data-yes"],
    T_CDA_APPIID : [SID+11, "cda-appiid"],
    T_CDA_COMP_CKSUM : [SID+12, "cda-compute-checksum"],
    T_CDA_COMP_LEN : [SID+13, "cda-compute-length"],
    T_CDA_DEVIID : [SID+14, "cda-deviid"],
    T_CDA_LSB : [SID+15, "cda-lsb"],
    T_CDA_MAP_SENT : [SID+16, "cda-mapping-sent"],
    T_CDA_NOT_SENT : [SID+17, "cda-not-sent"],
    T_CDA_VAL_SENT : [SID+18, "cda-value-sent"],
    "TBD" : [SID+19, "compression-decompression-action-base-type"],
    T_DIR_BI : [SID+20, "di-bidirectional"],
    T_DIR_DW : [SID+21, "di-down"],
    T_DIR_UP : [SID+22, "di-up"],
    "TBD" : [SID+23, "direction-indicator-base-type"],
    T_COAP_CODE : [SID+24, "fid-coap-code"],
    "TBD" : [SID+25, "fid-coap-code-class"],
    "TBD" : [SID+26, "fid-coap-code-detail"],
    T_COAP_MID : [SID+27, "fid-coap-mid"],
    T_COAP_OPT_ACCEPT : [SID+28, "fid-coap-option-accept"],
    T_COAP_OPT_BLOCK1 : [SID+29, "fid-coap-option-block1"],
    T_COAP_OPT_BLOCK2 : [SID+30, "fid-coap-option-block2"],
    T_COAP_OPT_CONT_FORMAT : [SID+31, "fid-coap-option-content-format"],
    T_COAP_OPT_ETAG : [SID+32, "fid-coap-option-etag"],
    T_COAP_OPT_IF_MATCH : [SID+33, "fid-coap-option-if-match"],
    T_COAP_OPT_IF_NONE_MATCH : [SID+34, "fid-coap-option-if-none-match"],
    T_COAP_OPT_LOC_PATH : [SID+35, "fid-coap-option-location-path"],
    T_COAP_OPT_LOC_QUERY : [SID+36, "fid-coap-option-location-query"],
    T_COAP_OPT_MAX_AGE : [SID+37, "fid-coap-option-max-age"],
    T_COAP_OPT_NO_RESP : [SID+38, "fid-coap-option-no-response"],
    T_COAP_OPT_OBS : [SID+39, "fid-coap-option-observe"],
    'TBD' : [SID+40, "fid-coap-option-oscore-flags"],
    "TBD" : [SID+41, "fid-coap-option-oscore-kid"],
    "TBD" : [SID+42, "fid-coap-option-oscore-kidctx"],
    "TBD" : [SID+43, "fid-coap-option-oscore-piv"],
    T_COAP_OPT_PROXY_SCHEME : [SID+44, "fid-coap-option-proxy-scheme"],
    T_COAP_OPT_PROXY_URI : [SID+45, "fid-coap-option-proxy-uri"],
    T_COAP_OPT_SIZE1 : [SID+46, "fid-coap-option-size1"],
    T_COAP_OPT_SIZE2 : [SID+47, "fid-coap-option-size2"],
    T_COAP_OPT_URI_HOST : [SID+48, "fid-coap-option-uri-host"],
    T_COAP_OPT_URI_PATH : [SID+49, "fid-coap-option-uri-path"],
    T_COAP_OPT_URI_PORT : [SID+50, "fid-coap-option-uri-port"],
    T_COAP_OPT_URI_QUERY : [SID+51, "fid-coap-option-uri-query"],
    T_COAP_TKL : [SID+52, "fid-coap-tkl"],
    T_COAP_TOKEN : [SID+53, "fid-coap-token"],
    T_COAP_TYPE : [SID+54, "fid-coap-type"],
    T_COAP_VERSION : [SID+55, "fid-coap-version"],
    T_ICMPV6_CKSUM : [SID+56, "fid-icmpv6-checksum"],
    T_ICMPV6_CODE : [SID+57, "fid-icmpv6-code"],
    T_ICMPV6_IDENT : [SID+58, "fid-icmpv6-identifier"],
    T_ICMPV6_SEQNO : [SID+59, "fid-icmpv6-sequence"],
    T_ICMPV6_TYPE : [SID+60, "fid-icmpv6-type"],
    T_IPV6_APP_IID : [SID+61, "fid-ipv6-appiid"],
    T_IPV6_APP_PREFIX : [SID+62, "fid-ipv6-appprefix"],
    T_IPV6_DEV_IID : [SID+63, "fid-ipv6-deviid"],
    T_IPV6_DEV_PREFIX : [SID+64, "fid-ipv6-devprefix"],
    T_IPV6_FL : [SID+65, "fid-ipv6-flowlabel"],
    T_IPV6_HOP_LMT : [SID+66, "fid-ipv6-hoplimit"],
    T_IPV6_NXT : [SID+67, "fid-ipv6-nextheader"],
    T_IPV6_LEN : [SID+68, "fid-ipv6-payloadlength"],
    T_IPV6_TC : [SID+69, "fid-ipv6-trafficclass"],
    "TBD" : [SID+70, "fid-ipv6-trafficclass-ds"],
    "TBD" : [SID+71, "fid-ipv6-trafficclass-ecn"],
    T_IPV6_VER : [SID+72, "fid-ipv6-version"],
    T_UDP_APP_PORT : [SID+73, "fid-udp-app-port"],
    T_UDP_CKSUM : [SID+74, "fid-udp-checksum"],
    T_UDP_DEV_PORT : [SID+75, "fid-udp-dev-port"],
    T_UDP_LEN : [SID+76, "fid-udp-length"],
    "TBD" : [SID+77, "field-id-base-type"],
    "TBD" : [SID+78, "field-id-coap-base-type"],
    "TBD" : [SID+79, "field-id-icmpv6-base-type"],
    "TBD" : [SID+80, "field-id-ipv6-base-type"],
    "TBD" : [SID+81, "field-id-udp-base-type"],
    "TBD" : [SID+82, "field-length-base-type"],
    T_FUNCTION_TKL : [SID+83, "fl-token-length"],
    T_FUNCTION_VAR : [SID+84, "fl-variable"],
    T_FRAG_ACK_ALWAYS : [SID+85, "fragmentation-mode-ack-always"],
    T_FRAG_ACK_ON_ERROR : [SID+86, "fragmentation-mode-ack-on-error"],
    "TBD" : [SID+87, "fragmentation-mode-base-type"],
    T_FRAG_NO_ACK : [SID+88, "fragmentation-mode-no-ack"],
    "TBD" : [SID+89, "matching-operator-base-type"],
    T_MO_EQUAL : [SID+90, "mo-equal"],
    T_MO_IGNORE : [SID+91, "mo-ignore"],
    T_MO_MMAP : [SID+92, "mo-matching"],
    T_MO_MSB : [SID+93, "mo-msb"]
}



# from gen_rulemanager import *


#---------------------------------------------------------------------------
# MO operation
#   return (True, tv) if matched.
#   return (False, None) if not matched.
# MO in rule.
#   if MO is MSG, assumed that MO.VAL exist in the rule.

#---------------------------------------------------------------------------
# 7.5.  Compression Decompression Actions (CDA)
#
#    The Compression Decompression Action (CDA) describes the actions
#    taken during the compression of headers fields and the inverse action
#    taken by the decompressor to restore the original value.
#
#    /--------------------+-------------+----------------------------\
#    |  Action            | Compression | Decompression              |
#    |                    |             |                            |
#    +--------------------+-------------+----------------------------+
#    |not-sent            |elided       |use value stored in Context |
#    |value-sent          |send         |build from received value   |
#    |mapping-sent        |send index   |value from index on a table |
#    |LSB                 |send LSB     |TV, received value          |
#    |compute-length      |elided       |compute length              |
#    |compute-checksum    |elided       |compute UDP checksum        |
#    |DevIID              |elided       |build IID from L2 Dev addr  |
#    |AppIID              |elided       |build IID from L2 App addr  |
#    \--------------------+-------------+----------------------------/

#---------------------------------------------------------------------------
class Compressor:

    def __init__(self, protocol):
        self.protocol = protocol

        self.__func_tx_cda = {
            T_CDA_NOT_SENT : self.tx_cda_not_sent,
            T_CDA_VAL_SENT : self.tx_cda_val_sent,
            T_CDA_MAP_SENT : self.tx_cda_map_sent,
            T_CDA_LSB : self.tx_cda_lsb,
            T_CDA_COMP_LEN: self.tx_cda_not_sent,
            T_CDA_COMP_CKSUM: self.tx_cda_not_sent,
            T_CDA_DEVIID : self.tx_cda_not_sent,
            T_CDA_APPIID : self.tx_cda_notyet,
            }

    def init(self):
        pass

    def tx_cda_not_sent(self, field, rule, output):
        pass

    def tx_cda_val_sent(self, field, rule, output):
        dprint(field)
        if rule[T_FL] == "var":
            dprint("VARIABLE")
            assert (field[1]%8 == 0)
            size = field[1]//8 # var unit is bytes
            output.add_length(size)

            if size == 0:
                return

        if type(field[0]) is int:
            dprint("+++", bin(field[0]), field[1])
            output.add_bits(field[0], field[1])
        elif type(field[0]) is str:
            assert (field[1] % 8 == 0) # string is a number of bytes
            for i in range(field[1]//8):
                dprint(i, field[0][i])
                output.add_bytes(field[0][i].encode("utf-8"))
        elif type(field[0]) is bytes:
            output.add_bits(int.from_bytes(field[0], "big"), field[1])
        else:
            raise ValueError("CA value-sent unknown type")

    def tx_cda_map_sent(self, field, rule, output):
        # 7.5.5.  mapping-sent CDA
        # The number of bits sent is the minimal size for coding all the
        # possible indices.

        target_value = rule[T_TV]
        assert (type(target_value) == list)

        size = len(bin(len(target_value)-1)[2:])

        dprint("size of ", target_value, "is ", size)

        pos = 0
        for tv in target_value:
            if type(field[0]) == type(tv) and field[0] == tv:
                output.add_bits(pos, size)
                return
            else:
                pos += 1

        raise ValueError ("value not found in TV")

    def tx_cda_lsb(self, field, rule, output):
        assert rule[T_MO] == T_MO_MSB
        size = field[1] - rule[T_MO_VAL]
        full_value = field[0]
        dprint("size =", size)

        if rule[T_FL] == "var":
            assert (size%8 == 0) #var implies bytes

            output.add_length(size//8)

        if type(full_value) == int:
            for i in range(size):
                output.set_bit(full_value & 0x01)
                full_value >>= 1
        elif type(full_value) == str:
            dprint(rule[T_TV], field[0])
            for i in range(rule[T_MO_VAL]//8, field[1]//8):
                dprint(i, "===>", field[0][i] )
            pass
        else:
            raise ValueError("CA value-sent unknown type")

    def tx_cda_notyet(self, field, rule, output):
        raise NotImplementedError

    # def compress(self, context, packet_bbuf, di=T_DIR_UP):
    #     """ compress the data in the packet_bbuf according to the rule_set.
    #     check if the all of the rules in the rule set are matched with the packet.
    #     return the compressed data to be sent if matched.
    #     or return None if not.
    #     regarding to the di, the address comparion is like below:
    #         di     source address      destination address
    #         T_DIR_DW  APP_PREFIX/APP_IID  DEV_PREFIX/DEV_IID
    #         T_DIR_UP  DEV_PREFIX/DEV_IID  APP_PREFIX/APP_IID
    #     """
    #     assert isinstance(packet_bbuf, BitBuffer)
    #     assert di in [T_DIR_UP, T_DIR_DW]
    #     input_bbuf = packet_bbuf.copy()
    #     output_bbuf = BitBuffer()
    #     rule = context["comp"]
    #     # set ruleID first.
    #     if rule["ruleID"] is not None and rule["ruleLength"] is not None:
    #         output_bbuf.add_bits(rule["ruleID"], rule["ruleLength"])
    #     for r in rule["compression"]["rule_set"]:
    #         # compare each rule with input_bbuf.
    #         # XXX need to handle "DI"
    #         dprint("rule item:", r)
    #         result, val = self.__func_tx_mo[r[T_MO]](r, input_bbuf)
    #         dprint("result", result, val)
    #         if result == False:
    #             # if any of MO functions is failed, return None.
    #             # this rule should not be applied.
    #             return None
    #         # if match the rule, call CDA.
    #         self.__func_tx_cda[r[T_CDA]](r, val, output_bbuf)
    #     if input_bbuf.count_remaining_bits() > 0:
    #         output_bbuf += input_bbuf
    #     # if all process have been succeeded, return the data.
    #     self.protocol._log("compress: {}=>{}".format(
    #         packet_bbuf, output_bbuf))
    #     return output_bbuf

    def compress(self, rule, parsed_packet, data, direction=T_DIR_UP):
        """
        Take a compression rule and a parsed packet and return a SCHC pkt
        """
        assert direction in [T_DIR_UP, T_DIR_DW]
        output_bbuf = BitBuffer()
        # set ruleID first.
        if rule[T_RULEID] is not None and rule[T_RULEIDLENGTH] is not None:
            output_bbuf.add_bits(rule[T_RULEID], rule[T_RULEIDLENGTH])
            dprint("rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
            #output_bbuf.display(format="bin")

        for r in rule["Compression"]:
            dprint("rule item:", r)

            if r[T_DI] in [T_DIR_BI, direction]:
                if (r[T_FID], r[T_FP]) in parsed_packet:
                    dprint("in packet")
                    self.__func_tx_cda[r[T_CDA]](field=parsed_packet[(r[T_FID], r[T_FP])],
                                                rule = r,
                                                output= output_bbuf)
                else: # not find in packet, but is variable length can be coded as 0
                    dprint("send variable length")
                    self.__func_tx_cda[T_CDA_VAL_SENT](field = [0, 0, "Null Field"], rule = r, output = output_bbuf)
            else:
                dprint("rule skipped, bad direction")

            #output_bbuf.display(format="bin")

        output_bbuf.add_bytes(data)

        return output_bbuf

    def no_compress(self, rule, data):
        """
        Take a compression rule and a parsed packet and return a SCHC pkt
        """
        assert T_NO_COMP in rule

        output_bbuf = BitBuffer()
        # set ruleID first.
        if rule[T_RULEID] is not None and rule[T_RULEIDLENGTH] is not None:
            output_bbuf.add_bits(rule[T_RULEID], rule[T_RULEIDLENGTH])
            dprint("rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
            #output_bbuf.display(format="bin")

        output_bbuf.add_bytes(data)

        return output_bbuf

class Decompressor:

    def __init__(self, protocol=None):
        self.protocol = protocol
        self.__func_rx_cda = {
            T_CDA_NOT_SENT : self.rx_cda_not_sent,
            T_CDA_VAL_SENT : self.rx_cda_val_sent,
            T_CDA_MAP_SENT : self.rx_cda_map_sent,
            T_CDA_LSB : self.rx_cda_lsb,
            T_CDA_COMP_LEN: self.rx_cda_comp_len,
            T_CDA_COMP_CKSUM: self.rx_cda_comp_cksum,
            T_CDA_DEVIID : self.rx_cda_not_sent,
            T_CDA_APPIID : self.rx_cda_not_sent,
            }


    def cal_checksum(self, packet):
        # RFC 1071
        assert isinstance(packet, bytearray)
        packet_size = len(packet)
        if packet_size%2:
            cksum = sum(struct.unpack(">{}H".format(packet_size//2), packet[:-1]))
            cksum += (packet[-1]<<8)&0xff00
        else:
            cksum = sum(struct.unpack(">{}H".format(packet_size//2), packet))
        while cksum>>16:
            cksum = (cksum & 0xFFFF) + (cksum >> 16 & 0xFFFF)
        return ~cksum & 0xFFFF

    def build_ipv6_pseudo_header(self):
        assert self.src_prefix is not None
        assert self.src_iid is not None
        assert self.dst_prefix is not None
        assert self.dst_iid is not None
        assert self.ipv6_payload is not None
        assert self.next_proto is not None
        phdr = bytearray([0]*40)
        phdr[ 0: 8] = self.src_prefix
        phdr[ 8:16] = self.src_iid
        phdr[16:24] = self.src_prefix
        phdr[24:32] = self.src_iid
        phdr[32:36] = struct.pack(">I",len(self.ipv6_payload))
        phdr[39] = self.next_proto
        return phdr

    # def cda_copy_field(self, out_bbuf, target_val):
    #     """ copy the appropriate target_val and return it. """
    #     if type(target_val) == bytes:
    #         pass
    #     else:
    #         tv = target_val
    #         out_bbuf.add_bits(tv, rule[T_FL])
    #     self.protocol._log("MO {}: copy {}".format(rule[T_MO], tv))
    #     return tv


    def rx_cda_not_sent(self, rule, in_bbuf):
        if rule[T_FL] == "var":
            if type(rule[T_TV]) == str:
                size = len(rule[T_TV]) * 8
            elif type(rule[T_TV]) == int: # return the minimal size, used in CoAP
                size = 0
                v = rule[T_TV]
                while v != 0:
                    size += 8
                    v >>=8
            else:
                size="var" # should never happend
        else:
            size = rule[T_FL]
        
        return [rule[T_TV], size]

    def rx_cda_val_sent(self, rule, in_bbuf):
        # XXX not implemented that the variable length size.

        if rule[T_FL] == "var":
            size = in_bbuf.get_length()*8
            dprint("siZE = ", size)
            if size == 0:
                return (None, 0)
        elif rule[T_FL] == "tkl":
            size = self.parsed_packet[(T_COAP_TKL, 1)][0]*8
            dprint("token size", size)
        elif type (rule[T_FL]) == int:
            size = rule[T_FL]
        else:
            raise ValueError("cannot read field length")
        #in_bbuf.display("bin")
        val = in_bbuf.get_bits(size)

        return [val, size]


    def rx_cda_map_sent(self, rule, in_bbuf):
        # 7.5.5.  mapping-sent CDA
        # The number of bits sent is the minimal size for coding all the
        # possible indices.


        size = len(bin(len(rule[T_TV])-1)[2:])
        val = in_bbuf.get_bits(size)

        dprint("====>", rule[T_TV][val], len(rule[T_TV][val]), rule[T_FL])

        if rule[T_FL] == "var":
            size = len(rule[T_TV][val])
        else:
            size = rule[T_FL]

        return [rule[T_TV][val], size]

    def rx_cda_lsb(self, rule, in_bbuf):
        assert rule[T_MO] == T_MO_MSB
        #
        # the value should consist of if FL is fixed:
        #
        #    |<------------ T_FL ------------>|
        #    |<-- T_MO_VAL -->|
        #    |      T_TV      |  field value  |
        # if FL = var
        #    |<-- T_MO_VAL -->|<- sent length->|
        tmp_bbuf = BitBuffer()

        if rule[T_FL] == "var":
            send_length = in_bbuf.get_length()
            total_size = rule[T_MO_VAL] + send_length
        elif type(rule[T_TV]) == int:
            total_size = rule[T_FL]
            send_length = rule[T_FL] - rule[T_MO_VAL]

        tmp_bbuf.add_value(rule[T_TV], rule[T_MO_VAL])
        val = in_bbuf.get_bits(send_length)
        tmp_bbuf.add_value(val, send_length)

        return [bytes(tmp_bbuf.get_content()), total_size]

    def rx_cda_comp_len(self, rule, in_bbuf):
        # will update the length field later.
        return ("LL"*(rule[T_FL]//8), rule[T_FL] )

    def rx_cda_comp_cksum(self, rule, in_bbuf):
        # will update the length field later.
        return ("CC"*(rule[T_FL]//8), rule[T_FL] )

    # def decompress(self, context, packet_bbuf, di=T_DIR_DW):
    #     """ decompress the data in the packet_bbuf according to the rule_set.
    #     return the decompressed data.
    #     or return None if any error happens.
    #     Note that it saves the content of packet_bbuf.

    #     XXX how to consider the IPv6 extension headers.
    #     """
    #     assert isinstance(packet_bbuf, BitBuffer)
    #     assert di in [T_DIR_UP, T_DIR_DW]
    #     input_bbuf = packet_bbuf.copy()
    #     output_bbuf = BitBuffer()
    #     rule = context["comp"]
    #     # skip ruleID if needed.
    #     if rule["ruleID"] is not None and rule["ruleLength"] is not None:
    #         rule_id = input_bbuf.get_bits(rule["ruleLength"])
    #         if rule_id != rule["ruleID"]:
    #             self.protocol._log("rule_id doesn't match. {} != {}".format(
    #                     rule_id, rule["ruleID"]))
    #             return None
    #     for r in rule["compression"]["rule_set"]:
    #         # XXX need to handle "DI"
    #         self.protocol._log("rule item: {}".format(r))
    #         # if match the rule, call CDA.
    #         val = self.__func_rx_cda[r[T_CDA]](r, input_bbuf, output_bbuf)
    #         # update info to build the IPv6 pseudo header.
    #         if r[T_FID] == T_IPV6_NXT:
    #             self.next_proto = val
    #         elif r[T_FID] == T_IPV6_DEV_PREFIX:
    #             if di == T_DIR_UP:
    #                 self.src_prefix = val
    #             else:
    #                 self.dst_prefix = val
    #         elif r[T_FID] == T_IPV6_DEV_IID:
    #             if di == T_DIR_UP:
    #                 self.src_iid = val
    #             else:
    #                 self.dst_iid = val
    #         elif r[T_FID] == T_IPV6_APP_PREFIX:
    #             if di == T_DIR_UP:
    #                 self.dst_prefix = val
    #             else:
    #                 self.src_prefix = val
    #         elif r[T_FID] == T_IPV6_APP_IID:
    #             if di == T_DIR_UP:
    #                 self.dst_iid = val
    #             else:
    #                 self.src_iid = val
    #         elif r[T_FID].startswith(T_PROTO_ICMPV6):
    #             self.cksum_field_offset = 42
    #         elif r[T_FID].startswith(T_PROTO_UDP):
    #             self.cksum_field_offset = 46
    #         #
    #     if input_bbuf.count_remaining_bits() > 0:
    #         output_bbuf += input_bbuf
    #     # update the ipv6 payload.
    #     self.ipv6_payload = output_bbuf.get_content()[40:]
    #     # update the field of IPv6 length.
    #     output_bbuf.add_bits(len(self.ipv6_payload), 16, position=32)
    #     # update the checksum field of the upper layer.
    #     if self.cksum_field_offset:
    #         assert self.ipv6_payload is not None
    #         cksum = self.cal_checksum(self.build_ipv6_pseudo_header() + self.ipv6_payload)
    #         output_bbuf.add_bits(cksum, 16, position=self.cksum_field_offset)
    #     # if all process have been succeeded, return the data.
    #     self.protocol._log("decompress: {}=>{}".format(
    #         packet_bbuf, output_bbuf))
    #     return output_bbuf

    def decompress(self, schc, rule, direction):
        assert ("Compression" in rule)
        schc.set_read_position(0)

        self.parsed_packet = {}

        rule_send = schc.get_bits(nb_bits=rule[T_RULEIDLENGTH])
        assert (rule_send == rule["RuleID"])

        for r in rule["Compression"]:
            dprint(r)
            if r[T_DI] in [T_DIR_BI, direction]:
                full_field = self.__func_rx_cda[r[T_CDA]](r, schc)
                dprint("<<<", full_field)
                self.parsed_packet[(r[T_FID], r[T_FP])] = full_field
                #pprint.pprint (self.parsed_packet)

        return self.parsed_packet

#---------------------------------------------------------------------------
