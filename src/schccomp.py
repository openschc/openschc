from base_import import *

import pprint

T_RULEID = "RuleID"
T_RULEIDLENGTH = "RuleIDLength"

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
T_COAP_OPT_IF_MATCH =  "COAP.If-Match"
T_COAP_OPT_URI_HOST = "COAP.Uri-Host"
T_COAP_OPT_ETAG = "COAP.ETag"
T_COAP_OPT_IF_NONE_MATCH =  "COAP.If-None-Match"
T_COAP_OPT_OBS =  "COAP.Observe"
T_COAP_OPT_URI_PORT =  "COAP.Uri-Port"
T_COAP_OPT_LOC_PATH = "COAP.Location-Path"
T_COAP_OPT_URI_PATH =  "COAP.URI-PATH"
T_COAP_OPT_CONT_FORMAT =  "COAP.CONTENT-FORMAT"
T_COAP_OPT_MAX_AGE =  "COAP.Max-Age"
T_COAP_OPT_URI_QUERY =  "COAP.URI-QUERY"
T_COAP_OPT_ACCEPT =  "COAP.Accept"
T_COAP_OPT_LOC_QUERY =  "COAP.Location-Query"
T_COAP_OPT_BLOCK2 =  "COAP.Block2"
T_COAP_OPT_BLOCK1 =  "COAP.Block1"
T_COAP_OPT_SIZE2 =  "COAP.Size2"
T_COAP_OPT_PROXY_URI =  "COAP.Proxy-Uri"
T_COAP_OPT_PROXY_SCHEME =  "COAP.Proxy-Scheme"
T_COAP_OPT_SIZE1 =  "COAP.Sizel"
T_COAP_OPT_NO_RESP = "COAP.No-Response"
T_COAP_OPT_END = "COAP.END"


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

T_FRAG = "Fragmentation"
T_FRAG_MODE = "FRMode"
T_FRAG_PROF = "FRModeProfile"
T_FRAG_DTAG = "dtagSize"
T_FRAG_W = "WSize"
T_FRAG_FCN = "FCNSize"
T_FRAG_ACK_BEHAVIOR = "ackBehavior"
T_FRAG_TILE = "tileSize"
T_FRAG_MIC  = "MICALgorithm"
T_FRAG_MAX_RETRY = "maxRetry"
T_FRAG_TIMEOUT  = "timeout"

from rulemanager import *


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
        print (field)
        if rule[T_FL] == "var":
            print ("VARIABLE")
            assert (field[1]%8 == 0)
            size = field[1]//8 # var unit is bytes
            output.add_length(size)

            if size == 0:
                return

        if type(field[0]) is int:
            print ("+++", bin(field[0]), field[1])
            output.add_bits(field[0], field[1])
        elif type(field[0]) == str:
            assert (field[1] % 8 == 0) # string is a number of bytes
            for i in range(field[1]//8):
                print (i, field[0][i])
                output.add_bytes(field[0][i].encode("utf-8"))
        else:
            raise ValueError("CA value-sent unknown type")

    def tx_cda_map_sent(self, field, rule, output):
        # 7.5.5.  mapping-sent CDA
        # The number of bits sent is the minimal size for coding all the
        # possible indices.

        target_value = rule[T_TV]
        assert (type(target_value) == list)

        size = len(bin(len(target_value)-1)[2:])

        print ("size of ", target_value, "is ", size)

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
        print ("size =", size)

        if rule[T_FL] == "var":
            assert (size%8 == 0) #var implies bytes

            output.add_length(size//8)

        if type(full_value) == int:
            for i in range(size):
                output.set_bit(full_value & 0x01)
                full_value >>= 1
        elif type(full_value) == str:
            print (rule[T_TV], field[0])
            for i in range(rule[T_MO_VAL]//8, field[1]//8):
                print (i, "===>", field[0][i] )
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
    #         print("rule item:", r)
    #         result, val = self.__func_tx_mo[r[T_MO]](r, input_bbuf)
    #         print("result", result, val)
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
            print("rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
            output_bbuf.display(format="bin")

        for r in rule["Compression"]:
            print("rule item:", r)

            if r[T_DI] in [T_DIR_BI, direction]:
                if (r[T_FID], r[T_FP]) in parsed_packet:
                    print ("in packet")
                    self.__func_tx_cda[r[T_CDA]](field=parsed_packet[(r[T_FID], r[T_FP])],
                                                rule = r,
                                                output= output_bbuf)
                else: # not find in packet, but is variable length can be coded as 0
                    print("send variable length")
                    self.__func_tx_cda[T_CDA_VAL_SENT](field = [0, 0, "Null Field"], rule = r, output = output_bbuf)
            else:
                print ("rule skipped, bad direction")

            output_bbuf.display(format="bin")

        output_bbuf.add_bytes(data)

        return output_bbuf

#---------------------------------------------------------------------------

class Decompressor:

    def __init__(self, protocol):
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
        return (rule[T_TV], rule[T_FL])

    def rx_cda_val_sent(self, rule, in_bbuf):
        # XXX not implemented that the variable length size.

        if rule[T_FL] == "var":
            size = in_bbuf.get_length()*8
            print ("siZE = ", size)
            if size == 0:
                return (None, 0)
        elif rule[T_FL] == "tkl":
            size = self.parsed_packet[(T_COAP_TKL, 1)][0]*8
            print ("token size", size)
        elif type (rule[T_FL]) == int:
            size = rule[T_FL]
        else:
            raise ValueError("cannot read field length")
        in_bbuf.display("bin")
        val = in_bbuf.get_bits(size)

        return (val, size)


    def rx_cda_map_sent(self, rule, in_bbuf):
        # 7.5.5.  mapping-sent CDA
        # The number of bits sent is the minimal size for coding all the
        # possible indices.


        size = len(bin(len(rule[T_TV])-1)[2:])
        val = in_bbuf.get_bits(size)

        print ("====>", rule[T_TV][val], len(rule[T_TV][val]), rule[T_FL])

        if rule[T_FL] == "var":
            size = len(rule[T_TV][val])
        else:
            size = rule[T_FL]

        return (rule[T_TV][val], size)

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

        return (bytes(tmp_bbuf.get_content()), total_size)

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
            print (r)
            if r[T_DI] in [T_DIR_BI, direction]:
                full_field = self.__func_rx_cda[r[T_CDA]](r, schc)
                print ("<<<", full_field)
                self.parsed_packet[(r[T_FID], r[T_FP])] = full_field
                pprint.pprint (self.parsed_packet)

        return self.parsed_packet

#---------------------------------------------------------------------------
