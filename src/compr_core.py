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

T_FID = "FID"
T_FL = "FL"
T_FP = "FP"
T_DI = "DI"
T_TV = "TV"
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

T_CDA_NOT_SENT = "NOT-SENT"
T_CDA_VAL_SENT = "VALUE-SENT"
T_CDA_MAP_SENT = "MAPPING-SENT"
T_CDA_LSB = "LSB"
T_CDA_COMP_LEN = "COMPUTE-LENGTH"
T_CDA_COMP_CKSUM = "COMPUTE-CHECKSUM"
T_CDA_DEVIID = "DEVIID"
T_CDA_APPIID = "APPIID"
T_CDA_LORA_DEVIID = "COMPUTE-DEVIID"

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
T_FRAG_DTAG                  = "dtagSize" # FIXME should be T_FRAG_DTAG_SIZE
T_FRAG_W                     = "WSize" # FIXME should be T_FRAG_W_SIZE
T_FRAG_FCN = "FCNSize"
T_FRAG_WINDOW_SIZE = "windowSize"
T_FRAG_ACK_BEHAVIOR = "ackBehavior"
T_FRAG_TILE = "tileSize"
T_FRAG_MIC = "MICALgorithm"
T_MAX_PACKET_SIZE = "MaxPktSize"
T_WINDOW_SIZE = "WindowSize"
T_MAX_INTER_FRAME = "MaxInterFrame"
T_FRAG_MAX_RETRY = "maxRetry"
T_FRAG_TIMEOUT  = "timeout"
T_FRAG_L2WORDSIZE = "L2WordSize"
T_FRAG_LAST_TILE_IN_ALL1 = "lastTileInAll1"
T_FRAG_RFC8724 = "RCS_CRC32"

T_POSITION_CORE = "core"
T_POSITION_DEVICE = "device"

T_INDEXES = "Indexes"
T_CMD_INDIRECT = "INDIRECT"

"""
100000     module ietf-schc
100001     identity ack-behavior-after-All0
100002     identity ack-behavior-after-All1
100003     identity ack-behavior-base-type
100004     identity ack-behavior-by-layer2
100005     identity all1-data-base-type
100006     identity all1-data-no
100007     identity all1-data-sender-choice
100008     identity all1-data-yes
100009     identity cda-appiid
100010     identity cda-base-type
100011     identity cda-compute-checksum
100012     identity cda-compute-length
100013     identity cda-deviid
100014     identity cda-lsb
100015     identity cda-mapping-sent
100016     identity cda-not-sent
100017     identity cda-value-sent
100018     identity di-base-type
100019     identity di-bidirectional
100020     identity di-down
100021     identity di-up
100022     identity fid-base-type
100023     identity fid-coap-base-type
100024     identity fid-coap-code
100025     identity fid-coap-code-class
100026     identity fid-coap-code-detail
100027     identity fid-coap-mid
100028     identity fid-coap-option-accept
100029     identity fid-coap-option-block1
100030     identity fid-coap-option-block2
100031     identity fid-coap-option-content-format
100032     identity fid-coap-option-etag
100033     identity fid-coap-option-if-match
100034     identity fid-coap-option-if-none-match
100035     identity fid-coap-option-location-path
100036     identity fid-coap-option-location-query
100037     identity fid-coap-option-max-age
100038     identity fid-coap-option-no-response
100039     identity fid-coap-option-observe
100040     identity fid-coap-option-oscore-flags
100041     identity fid-coap-option-oscore-kid
100042     identity fid-coap-option-oscore-kidctx
100043     identity fid-coap-option-oscore-piv
100044     identity fid-coap-option-proxy-scheme
100045     identity fid-coap-option-proxy-uri
100046     identity fid-coap-option-size1
100047     identity fid-coap-option-size2
100048     identity fid-coap-option-uri-host
100049     identity fid-coap-option-uri-path
100050     identity fid-coap-option-uri-port
100051     identity fid-coap-option-uri-query
100052     identity fid-coap-tkl
100053     identity fid-coap-token
100054     identity fid-coap-type
100055     identity fid-coap-version
100056     identity fid-ipv6-appiid
100057     identity fid-ipv6-appprefix
100058     identity fid-ipv6-base-type
100059     identity fid-ipv6-deviid
100060     identity fid-ipv6-devprefix
100061     identity fid-ipv6-flowlabel
100062     identity fid-ipv6-hoplimit
100063     identity fid-ipv6-nextheader
100064     identity fid-ipv6-payloadlength
100065     identity fid-ipv6-trafficclass
100066     identity fid-ipv6-trafficclass-ds
100067     identity fid-ipv6-trafficclass-ecn
100068     identity fid-ipv6-version
100069     identity fid-udp-app-port
100070     identity fid-udp-base-type
100071     identity fid-udp-checksum
100072     identity fid-udp-dev-port
100073     identity fid-udp-length
100074     identity fl-base-type
100075     identity fl-token-length
100076     identity fl-variable
100077     identity fragmentation-mode-ack-always
100078     identity fragmentation-mode-ack-on-error
100079     identity fragmentation-mode-base-type
100080     identity fragmentation-mode-no-ack
100081     identity mo-base-type
100082     identity mo-equal
100083     identity mo-ignore
100084     identity mo-match-mapping
100085     identity mo-msb
100086     identity rcs-RFC8724
100087     identity rcs-algorithm-base-type
100088     feature compression
100089     feature fragmentation
100090     data /ietf-schc:schc
100091     data /ietf-schc:schc/rule
100092     data /ietf-schc:schc/rule/ack-behavior
100093     data /ietf-schc:schc/rule/direction
100094     data /ietf-schc:schc/rule/dtag-size
100095     data /ietf-schc:schc/rule/entry
100096     data /ietf-schc:schc/rule/entry/comp-decomp-action
100097     data /ietf-schc:schc/rule/entry/comp-decomp-action-value
100098     data /ietf-schc:schc/rule/entry/comp-decomp-action-value/position
100099     data /ietf-schc:schc/rule/entry/comp-decomp-action-value/value
100100     data /ietf-schc:schc/rule/entry/direction-indicator
100101     data /ietf-schc:schc/rule/entry/field-id
100102     data /ietf-schc:schc/rule/entry/field-length
100103     data /ietf-schc:schc/rule/entry/field-position
100104     data /ietf-schc:schc/rule/entry/matching-operator
100105     data /ietf-schc:schc/rule/entry/matching-operator-value
100106     data /ietf-schc:schc/rule/entry/matching-operator-value/position
100107     data /ietf-schc:schc/rule/entry/matching-operator-value/value
100108     data /ietf-schc:schc/rule/entry/target-value
100109     data /ietf-schc:schc/rule/entry/target-value/position
100110     data /ietf-schc:schc/rule/entry/target-value/value
100111     data /ietf-schc:schc/rule/fcn-size
100112     data /ietf-schc:schc/rule/fragmentation-mode
100113     data /ietf-schc:schc/rule/inactivity-timer
100114     data /ietf-schc:schc/rule/l2-word-size
100115     data /ietf-schc:schc/rule/max-ack-requests
100116     data /ietf-schc:schc/rule/max-interleaved-frames
100117     data /ietf-schc:schc/rule/maximum-packet-size
100118     data /ietf-schc:schc/rule/rcs-algorithm
100119     data /ietf-schc:schc/rule/retransmission-timer
100120     data /ietf-schc:schc/rule/rule-id-length
100121     data /ietf-schc:schc/rule/rule-id-value
100122     data /ietf-schc:schc/rule/tile-in-All1
100123     data /ietf-schc:schc/rule/tile-size
100124     data /ietf-schc:schc/rule/w-size
100125     data /ietf-schc:schc/rule/window-size
"""
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
        # size = field[1] - rule[T_MO_VAL]
        # full_value = field[0]
        # dprint("size =", size)

        # if rule[T_FL] == "var":
        #     assert (size%8 == 0) #var implies bytes

        #     output.add_length(size//8)

        # if type(full_value) == int:
        #     for i in range(size):
        #         output.set_bit(full_value & 0x01)
        #         full_value >>= 1
        # elif type(full_value) == str:
        #     dprint(rule[T_TV], field[0])
        #     for i in range(rule[T_MO_VAL]//8, field[1]//8):
        #         dprint(i, "===>", field[0][i] )
        #     pass
        # else:
        #     raise ValueError("CA value-sent unknown type")

        full_value = field[0]
        start_byte = rule[T_MO_VAL]//8 # go to the byte to send
        last_byte  = field[1]//8
        start_bit  = 7-rule[T_MO_VAL]%8  # in that byte how many bits left
        size = field[1] - rule[T_MO_VAL]

        if rule[T_FL] == "var":
            assert (size%8 == 0) #var implies bytes

            output.add_length(size//8)

        print(field)

        for i in range (start_bit, -1, -1):
            print (i, 1 << i, full_value[start_byte] & (1 << i))
            output.set_bit(full_value[start_byte] & (1 << i))

        print (start_byte+1, last_byte)
        for i in range (start_byte+1, last_byte):
            print (i, chr(full_value[i]))
            output.add_bits(full_value[i], 8)





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
            print("rule item:", r)

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

            output_bbuf.display(format="bin")

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
            output_bbuf.display(format="bin")

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


    # def cal_checksum(self, packet):
    #     # RFC 1071
    #     assert isinstance(packet, bytearray)
    #     packet_size = len(packet)
    #     if packet_size%2:
    #         cksum = sum(struct.unpack(">{}H".format(packet_size//2), packet[:-1]))
    #         cksum += (packet[-1]<<8)&0xff00
    #     else:
    #         cksum = sum(struct.unpack(">{}H".format(packet_size//2), packet))
    #     while cksum>>16:
    #         cksum = (cksum & 0xFFFF) + (cksum >> 16 & 0xFFFF)
    #     return ~cksum & 0xFFFF

    # def build_ipv6_pseudo_header(self):
    #     assert self.src_prefix is not None
    #     assert self.src_iid is not None
    #     assert self.dst_prefix is not None
    #     assert self.dst_iid is not None
    #     assert self.ipv6_payload is not None
    #     assert self.next_proto is not None
    #     phdr = bytearray([0]*40)
    #     phdr[ 0: 8] = self.src_prefix
    #     phdr[ 8:16] = self.src_iid
    #     phdr[16:24] = self.src_prefix
    #     phdr[24:32] = self.src_iid
    #     phdr[32:36] = struct.pack(">I",len(self.ipv6_payload))
    #     phdr[39] = self.next_proto
    #     return phdr

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

        #dprint("====>", rule[T_TV][val], len(rule[T_TV][val]), rule[T_FL])
 

        if rule[T_FL] == "var":
            size = len(rule[T_TV][val]) * 8
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
        elif type(rule[T_TV]) is bytes:
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
