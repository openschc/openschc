T_RULEID = "RuleID"
T_RULEIDVALUE = "RuleIDValue"
T_RULEIDLENGTH = "RuleIDLength"
T_DEVICEID = "DeviceID"

T_FID = "FID"
T_FL = "FL"
T_FP = "FP"
T_DI = "DI"
T_TV = "TV"
T_TV_IND = "TV.IND"
T_MO = "MO"
T_MO_VAL = "MO.VAL"
T_CDA = "CDA"
T_SB = "SB"

T_PROTO_IPV6 = "IPV6"
# IPv6 header fields
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
# ICMPv6 header fields
T_ICMPV6_TYPE = "ICMPV6.TYPE"
T_ICMPV6_CODE = "ICMPV6.CODE"
T_ICMPV6_CKSUM = "ICMPV6.CKSUM"
T_ICMPV6_IDENT = "ICMPV6.IDENT"
T_ICMPV6_SEQNO = "ICMPV6.SEQNO"
T_ICMPV6_UNUSED = "ICMPV6.UNUSED"
T_ICMPV6_PAYLOAD = "ICMPV6.PAYLOAD"
# ICMPv6 types
T_ICMPV6_TYPE_ECHO_REQUEST = "ICMPV6.TYPE.ECHO.REQUEST"
T_ICMPV6_TYPE_ECHO_REPLY = "ICMPV6.TYPE.ECHO.REPLY"

T_PROTO_UDP = "UDP"
# UDP fields
T_UDP_DEV_PORT = "UDP.DEV_PORT"
T_UDP_APP_PORT = "UDP.APP_PORT"
T_UDP_LEN = "UDP.LEN"
T_UDP_CKSUM = "UDP.CKSUM"

T_PROTO_COAP = "COAP"
# CoAP fields
T_COAP_VERSION = "COAP.VER"
T_COAP_TYPE = "COAP.TYPE"
T_COAP_TKL = "COAP.TKL"
T_COAP_CODE = "COAP.CODE"
T_COAP_MID = "COAP.MID"
T_COAP_TOKEN = "COAP.TOKEN"
# CoAP options string (written exactly as in standards)
T_COAP_OPT_IF_MATCH =  "COAP.IF-MATCH"
T_COAP_OPT_URI_HOST = "COAP.URI-HOST"
T_COAP_OPT_ETAG = "COAP.ETAG"
T_COAP_OPT_IF_NONE_MATCH =  "COAP.IF-NONE-MATCH"
T_COAP_OPT_OBS =  "COAP.OBSERVE"
T_COAP_OPT_URI_PORT =  "COAP.URI-PORT"
T_COAP_OPT_LOC_PATH = "COAP.LOCATION-PATH"
T_COAP_OPT_URI_PATH =  "COAP.URI-PATH"
T_COAP_OPT_CONT_FORMAT =  "COAP.CONTENT-FORMAT"
T_COAP_OPT_MAX_AGE =  "COAP.MAX-AGE"
T_COAP_OPT_URI_QUERY =  "COAP.URI-QUERY"
T_COAP_OPT_ACCEPT =  "COAP.ACCEPT"
T_COAP_OPT_LOC_QUERY =  "COAP.LOCATION-QUERY"
T_COAP_OPT_BLOCK2 =  "COAP.BLOCK2"
T_COAP_OPT_BLOCK1 =  "COAP.BLOCK1"
T_COAP_OPT_SIZE2 =  "COAP.SIZE2"
T_COAP_OPT_PROXY_URI =  "COAP.PROXY-URI"
T_COAP_OPT_PROXY_SCHEME =  "COAP.PROXY-SCHEME"
T_COAP_OPT_SIZE1 =  "COAP.SIZE1"
T_COAP_OPT_NO_RESP = "COAP.NO-RESPONSE"
T_COAP_OPT_END = "COAP.End"

T_FUNCTION_VAR = "var"
T_FUNCTION_TKL = "tkl"

T_FUNCTION_VAR = "var"
T_FUNCTION_TKL = "tkl"


T_DIR_UP = "UP"
T_DIR_DW = "DW"
T_DIR_BI = "BI"

T_MO_EQUAL = "EQUAL"
T_MO_IGNORE = "IGNORE"
T_MO_MSB = "MSB"
T_MO_MMAP = "MATCH-MAPPING"
T_MO_MATCH_REV_RULE = "REV-RULE-MATCH"

T_CDA_NOT_SENT = "NOT-SENT"
T_CDA_VAL_SENT = "VALUE-SENT"
T_CDA_MAP_SENT = "MAPPING-SENT"
T_CDA_LSB = "LSB"
T_CDA_COMP_LEN = "COMPUTE-LENGTH"
T_CDA_COMP_CKSUM = "COMPUTE-CHECKSUM"
T_CDA_DEVIID = "DEVIID"
T_CDA_APPIID = "APPIID"
T_CDA_LORA_DEVIID = "COMPUTE-DEVIID"
T_CDA_REV_COMPRESS = "REV-COMPRESSED-SENT"

T_ALGO = "ALGO"
T_ALGO_DIRECT = "DIRECT"
T_ALGO_COAP_OPT = "COAP_OPTION"

T_META = "META"
T_UP_RULES = "UP_RULES"
T_DW_RULES = "DW_RULES"
T_LAST_USED = "LAST_USED"

T_ACTION = "Action"

T_COMP = "Compression"
T_NO_COMP = "NoCompression"
T_FRAG = "Fragmentation"
T_FRAG_MODE = "FRMode"
T_FRAG_NO_ACK = "NoAck"              #YANG  no-ack
T_FRAG_ACK_ALWAYS = "AckAlways"
T_FRAG_ACK_ON_ERROR = "AckOnError"
T_FRAG_DIRECTION = "FRDirection"     #YANG direction
T_FRAG_PROF = "FRModeProfile"
T_FRAG_DTAG_SIZE = "dtagSize"        #YANG dtag-size
T_FRAG_W_SIZE = "WSize"              #YANG w-size
T_FRAG_FCN = "FCNSize"               #YANG fcn-size
T_FRAG_WINDOW_SIZE = "windowSize"    #YANG window-size
T_MAX_INTER_FRAME = "MaxInterFrame"  #YANG max-interleaved-frames
T_FRAG_ACK_BEHAVIOR = "ackBehavior"  #YANG ack-behavior
T_FRAG_AFTER_ALL1 = "afterAll1"
T_FRAG_AFTER_ALL0 = "afterAll0"
T_FRAG_AFTER_ANY = "afterAny"
T_FRAG_TILE = "tileSize"             #YANG tile-size
T_FRAG_MIC = "MICALgorithm"          #YANG rcs-algorithm
T_MAX_PACKET_SIZE = "MaxPcktSize"    #YANG maximum-packet-size
T_MAX_INTER_FRAME = "MaxInterFrame"  #YANG max-interleaved-frames
T_FRAG_MAX_RETRY = "maxRetry"        #YANG max-ack-requests
T_FRAG_TIMEOUT  = "timeout"          #YANG retransmission-timer
T_FRAG_L2WORDSIZE = "L2WordSize"     #YANG l2-word-size
T_FRAG_LAST_TILE_IN_ALL1 = "lastTileInAll1" #YANG tile-in-all-1
T_FRAG_RFC8724 = "RCS_CRC32"

# --------------------- FEC section !!

T_FRAG_FEC = "ForwardErrorCorrection"           #TypeRule  
T_FRAG_FEC_BOUNDTO_ID = "BoundToID"             #Corresponds to the rule ID the FEC rule is bound to 
T_FRAG_FEC_BOUNDTO_LENGTH = "BoundToLength"     #Corresponds to the rule Length the FEC rule is bound to 
T_FRAG_FEC_XORFRAGS = "XorFrags"                #The number of fragments to be sent before sending the redondent frag

# --------------------- end of FEC section !!

T_POSITION_CORE = "core"
T_POSITION_DEVICE = "device"

T_INDEXES = "Indexes"
T_CMD_INDIRECT = "INDIRECT"


SID = 100000

YANG_ID = {
    "module" : [SID, "ietf-schc"],
    "TBD" : [SID+1, "ack-behavior-after-All0"],
    "TBD" : [SID+2, "ack-behavior-after-All1"],
    "TBD" : [SID+3, "ack-behavior-base-type"],
    "TBD" : [SID+4, "ack-behavior-by-layer2"],
    "TBD" : [SID+5, "all1-data-base-type"],
    "TBD" : [SID+6, "all1-data-no"],
    "TBD" : [SID+7, "all1-data-sender-choice"],
    "TBD" : [SID+8, "all1-data-yes"],
    T_CDA_APPIID : [SID+9, "cda-appiid"],
    "TBD" : [SID+10, "cda-base-type"],
    T_CDA_COMP_CKSUM : [SID+11, "cda-compute"],
    T_CDA_COMP_LEN : [SID+12, "cda-compute"],
    T_CDA_DEVIID : [SID+13, "cda-deviid"],
    T_CDA_LSB : [SID+14, "cda-lsb"],
    T_CDA_MAP_SENT : [SID+15, "cda-mapping-sent"],
    T_CDA_NOT_SENT : [SID+16, "cda-not-sent"],
    T_CDA_VAL_SENT : [SID+17, "cda-value-sent"],
     "TBD" : [SID+18, "di-base-type"],   
    T_DIR_BI : [SID+19, "di-bidirectional"],
    T_DIR_DW : [SID+20, "di-down"],
    T_DIR_UP : [SID+21, "di-up"],
    "TBD" : [SID+22, "fid-base-type"],   
    "TBD" : [SID+23, "fid-coap-base-type"],   
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
    "TBD":                    [SID+40, "fid-coap-option-oscore-flags"],
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
    T_IPV6_APP_IID : [SID+56, "fid-ipv6-appiid"],
    T_IPV6_APP_PREFIX : [SID+57, "fid-ipv6-appprefix"],
    "TBD" : [SID+58, "fid-ipv6-base-type"],   
    T_IPV6_DEV_IID : [SID+59, "fid-ipv6-deviid"],
    T_IPV6_DEV_PREFIX : [SID+60, "fid-ipv6-devprefix"],
    T_IPV6_FL : [SID+61, "fid-ipv6-flowlabel"],
    T_IPV6_HOP_LMT : [SID+62, "fid-ipv6-hoplimit"],
    T_IPV6_NXT : [SID+63, "fid-ipv6-nextheader"],
    T_IPV6_LEN : [SID+64, "fid-ipv6-payload-length"],
    T_IPV6_TC : [SID+65, "fid-ipv6-trafficclass"],
    "TBD" : [SID+66, "fid-ipv6-trafficclass-ds"],
    "TBD" : [SID+67, "fid-ipv6-trafficclass-ecn"],
    T_IPV6_VER : [SID+68, "fid-ipv6-version"],
    T_UDP_APP_PORT : [SID+69, "fid-udp-app-port"],
     "TBD" : [SID+70, "fid-udp-base-type"],      
    T_UDP_CKSUM : [SID+71, "fid-udp-checksum"],
    T_UDP_DEV_PORT : [SID+72, "fid-udp-dev-port"],
    T_UDP_LEN : [SID+73, "fid-udp-length"],
    "TBD" : [SID+74, "fl-base-type"],      
    T_FUNCTION_TKL : [SID+75, "fl-token-length"],
    T_FUNCTION_VAR : [SID+76, "fl-variable"],
    T_FRAG_ACK_ALWAYS : [SID+77, "fragmentation-mode-ack-always"],
    T_FRAG_ACK_ON_ERROR : [SID+78, "fragmentation-mode-ack-on-error"],
    "TBD" : [SID+79, "fragmentation-mode-base-type"],
    T_FRAG_NO_ACK : [SID+80, "fragmentation-mode-no-ack"],
    "TBD" : [SID+81, "mo-base-type"],      
    T_MO_EQUAL : [SID+82, "mo-equal"],
    T_MO_IGNORE : [SID+83, "mo-ignore"],
    T_MO_MMAP : [SID+84, "mo-match-mapping"],
    T_MO_MSB : [SID+85, "mo-msb"],
    T_FRAG_RFC8724 : [SID+86, "rcs-crc32"],
    "TBD" : [SID+87, "rcs-algorithm-base-type"],
    "TBD" : [SID+88, "compression"],
    "TBD" : [SID+89, "fragmentation"],
    "TBD" : [SID+90, "/ietf-schc:schc"],
    "TBD" : [SID+91, "/ietf-schc:schc/rule"],
    "TBD" : [SID+92, "/ietf-schc:schc/rule/ack-behavior"],
    "TBD" : [SID+93, "/ietf-schc:schc/rule/direction"],
    "TBD" : [SID+94, "/ietf-schc:schc/rule/dtag-size"],
    "TBD" : [SID+95, "/ietf-schc:schc/rule/entry"],
    "TBD" : [SID+96, "/ietf-schc:schc/rule/entry/comp-decomp-action"],
    "TBD" : [SID+97, "/ietf-schc:schc/rule/entry/comp-decomp-action-value"],
    "TBD" : [SID+98, "/ietf-schc:schc/rule/entry/comp-decomp-action-value/position"],
    "TBD" : [SID+99, "/ietf-schc:schc/rule/entry/comp-decomp-action-value/value"],
    "TBD" : [SID+100, "/ietf-schc:schc/rule/entry/direction-indicator"],
    "TBD" : [SID+101, "/ietf-schc:schc/rule/entry/field-id"],
    "TBD" : [SID+102, "/ietf-schc:schc/rule/entry/field-length"],
    "TBD" : [SID+103, "/ietf-schc:schc/rule/entry/field-position"],
    "TBD" : [SID+104, "/ietf-schc:schc/rule/entry/matching-operator"],
    "TBD" : [SID+105, "/ietf-schc:schc/rule/entry/matching-operator-value"],
    "TBD" : [SID+106, "/ietf-schc:schc/rule/entry/matching-operator-value/position"],
    "TBD" : [SID+107, "/ietf-schc:schc/rule/entry/matching-operator-value/value"],
    "TBD" : [SID+108, "/ietf-schc:schc/rule/entry/target-value"],
    "TBD" : [SID+109, "/ietf-schc:schc/rule/entry/target-value/position"],
    "TBD" : [SID+110, "/ietf-schc:schc/rule/entry/target-value/value"],
    "TBD" : [SID+111, "/ietf-schc:schc/rule/fcn-size"],
    "TBD" : [SID+112, "/ietf-schc:schc/rule/fragmentation-mode"],
    "TBD" : [SID+113, "/ietf-schc:schc/rule/inactivity-timer"],
    "TBD" : [SID+114, "/ietf-schc:schc/rule/l2-word-size"],
    "TBD" : [SID+115, "/ietf-schc:schc/rule/max-ack-requests"],
    "TBD" : [SID+116, "/ietf-schc:schc/rule/max-interleaved-frames"],
    "TBD" : [SID+117, "/ietf-schc:schc/rule/maximum-packet-size"],
    "TBD" : [SID+118, "/ietf-schc:schc/rule/rcs-algorithm"],
    "TBD" : [SID+119, "/ietf-schc:schc/rule/retransmission-timer"],
    "TBD" : [SID+120, "/ietf-schc:schc/rule/rule-id-length"],
    "TBD" : [SID+121, "/ietf-schc:schc/rule/rule-id-value"],
    "TBD" : [SID+122, "/ietf-schc:schc/rule/tile-in-All1"],
    "TBD" : [SID+123, "/ietf-schc:schc/rule/tile-size"],
    "TBD" : [SID+124, "/ietf-schc:schc/rule/w-size"],
    "TBD": [SID+125, "/ietf-schc:schc/rule/window-size"],
    # from OAM 
    T_ICMPV6_CODE: [None, "fid-icmpv6-code"],
    T_ICMPV6_TYPE: [None, "fid-icmpv6-type"],
    T_ICMPV6_IDENT: [None, "fid-icmpv6-identifier"],
    T_ICMPV6_SEQNO: [None, "fid-icmpv6-sequence"],
    T_ICMPV6_CKSUM: [None, "fid-icmpv6-checksum"],

}

import ipaddress

def adapt_value(value, length=None, FID=None): 
    """transform any value of any type in the smallest bytearray.
    FID allows to convert properly the string to IPv6 address."""

    if type(value) is list:
        result = []
        for e in value:
            result.append(adapt_value(e, length, FID))

        return value
    
    if type(value) is int:

        if FID in [T_IPV6_APP_IID, T_IPV6_APP_PREFIX, T_IPV6_DEV_IID, T_IPV6_DEV_PREFIX] and length != None:
            return value.to_bytes(length//8, byteorder='big')
        
        size = 0
        v = value
        while v != 0:
            v = v >> 8
            size += 1

        if size == 0: # when value == 0 store 0
            size=1 

        return value.to_bytes (size, byteorder='big')
    if type(value) is str:
        if FID in [T_IPV6_APP_IID, T_IPV6_APP_PREFIX, T_IPV6_DEV_IID, T_IPV6_DEV_PREFIX]:
            # string has to be converted as IPv6 addresses

            slash_pos = value.find("/") 
            if slash_pos != -1:
                # a prefix is given, remove / to be compatible with ip_address
                value = value[:slash_pos]

            addr = ipaddress.ip_address(value)
            if addr.version != 6: # expect an IPv6 address
                raise ValueError ("only IPv6 is supported, can not support {}".format(addr.version))

            if FID in [T_IPV6_DEV_PREFIX, T_IPV6_APP_PREFIX]: #prefix top 8
                return addr.packed[:8]
            elif FID in [T_IPV6_DEV_IID, T_IPV6_APP_IID]: #IID bottom 8
                return addr.packed[8:]
            else:
                raise ValueError ("{} Fid not found".format(FID))   
        else: # a regular string
            return value.encode()              
    elif type(value) is bytes:
        return value
    elif value == None:
        return None
    else:
        raise ValueError("Unknown type", type(value))
