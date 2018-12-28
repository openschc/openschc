from base_import import *
import ipaddress
import struct

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

T_PROTO_UDP = "UDP"
T_UDP_DEV_PORT = "UDP.DEV_PORT"
T_UDP_APP_PORT = "UDP.APP_PORT"
T_UDP_LEN = "UDP.LEN"
T_UDP_CKSUM = "UDP.CKSUM"

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
        self.__func_tx_mo = {
            T_MO_EQUAL : self.tx_mo_equal,
            T_MO_IGNORE : self.tx_mo_ignore,
            T_MO_MSB : self.tx_mo_msb,
            T_MO_MMAP: self.tx_mo_mmap,
            }
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

    def compare_value(self, rule, hdr_val, target_val):
        assert isinstance(hdr_val, int)
        if rule[T_FID] in [T_IPV6_DEV_PREFIX, T_IPV6_APP_PREFIX]:
            assert isinstance(target_val, str)
            # XXX needs to support any bit length.
            assert rule[T_FL]%8 == 0
            size = rule[T_FL]//8
            hv = hdr_val.to_bytes(size, "big")
            a = ipaddress.ip_network(target_val, strict=False)
            tv = a[0].packed[:size]
        elif rule[T_FID] in [T_IPV6_DEV_IID, T_IPV6_APP_IID]:
            assert isinstance(target_val, str)
            # XXX needs to support any bit length.
            assert rule[T_FL]%8 == 0
            size = rule[T_FL]//8
            hv = hdr_val.to_bytes(size, "big")
            tv = ipaddress.ip_address(target_val).packed[size:]
        else:
            hv = hdr_val
            tv = target_val
        print("MO {}: {} == {}".format(rule[T_MO], hv, tv))
        return hv == tv

    def tx_mo_equal(self, rule, pkt):
        hv = pkt.get_bits(rule[T_FL])
        tv = rule[T_TV]
        if self.compare_value(rule, hv, tv):
            return True, tv
        return False, None

    def tx_mo_ignore(self, rule, pkt):
        """ always return True and header value. """
        # needs to read the bits in order to skip the field.
        hv = pkt.get_bits(rule[T_FL])
        print("MO ignore", hv, None)
        return True, hv

    def tx_mo_msb(self, rule, pkt):
        hv = pkt.get_bits(rule[T_MO_VAL])
        tv = rule[T_TV]
        # needs to read the remaining bits in order to skip the field.
        pkt.get_bits(rule[T_FL] - rule[T_MO_VAL])
        print("MO msb({})".format(rule[T_MO_VAL]), hv, tv)
        if hv == tv:
            return True, tv
        return False, None

    def tx_mo_mmap(self, rule, pkt):
        """ return the index in the mapping table if a header value is matched. """
        hv = pkt.get_bits(rule[T_FL])
        for i in range(len(rule[T_TV])):
            tv = rule[T_TV][i]
            if self.compare_value(rule, hv, tv):
                return True, i
        return False, None

    def tx_cda_not_sent(self, rule, val, bbuf):
        pass

    def tx_cda_val_sent(self, rule, val, bbuf):
        # XXX not implemented that the variable length size.
        bbuf.add_bits(val, rule[T_FL])

    def tx_cda_map_sent(self, rule, val, bbuf):
        # 7.5.5.  mapping-sent CDA
        # The number of bits sent is the minimal size for coding all the
        # possible indices.
        size = len(bin(len(rule[T_TV]))[2:])
        bbuf.add_bits(val, size)

    def tx_cda_lsb(self, rule, val, bbuf):
        assert rule[T_MO] == T_MO_MSB
        size = rule[T_FL] - rule[T_MO_VAL]
        bbuf.add_bits(val, size)

    def tx_cda_notyet(self, rule, val, bbuf):
        raise NotImplementedError

    def compress(self, context, packet_bbuf, di=T_DIR_UP):
        """ compress the data in the packet_bbuf according to the rule_set.
        check if the all of the rules in the rule set are matched with the packet.
        return the compressed data to be sent if matched.
        or return None if not.
        regarding to the di, the address comparion is like below:
            di     source address      destination address
            T_DIR_DW  APP_PREFIX/APP_IID  DEV_PREFIX/DEV_IID
            T_DIR_UP  DEV_PREFIX/DEV_IID  APP_PREFIX/APP_IID
        """
        assert isinstance(packet_bbuf, BitBuffer)
        assert di in [T_DIR_UP, T_DIR_DW]
        input_bbuf = packet_bbuf.copy()
        output_bbuf = BitBuffer()
        rule = context["comp"]
        # set ruleID first.
        if rule["ruleID"] is not None and rule["ruleLength"] is not None:
            output_bbuf.add_bits(rule["ruleID"], rule["ruleLength"])
        for r in rule["compression"]["rule_set"]:
            # compare each rule with input_bbuf.
            # XXX need to handle "DI"
            print("rule item:", r)
            result, val = self.__func_tx_mo[r[T_MO]](r, input_bbuf)
            print("result", result, val)
            if result == False:
                # if any of MO functions is failed, return None.
                # this rule should not be applied.
                return None
            # if match the rule, call CDA.
            self.__func_tx_cda[r[T_CDA]](r, val, output_bbuf)
        if input_bbuf.count_remaining_bits() > 0:
            output_bbuf += input_bbuf
        # if all process have been succeeded, return the data.
        self.protocol._log("compress: {}=>{}".format(
            packet_bbuf, output_bbuf))
        return output_bbuf

#---------------------------------------------------------------------------

class Decompressor:

    def __init__(self, protocol):
        self.protocol = protocol
        self.init()
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

    def init(self):
        self.src_prefix = None   # the size must be of 8 bytes.
        self.src_iid = None
        self.dst_prefix = None   # the size must be of 8 bytes.
        self.dst_iid = None
        self.ipv6_payload = None
        self.next_proto = None
        self.cksum_field_offset = 0

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

    def cda_copy_field(self, rule, out_bbuf, target_val):
        """ copy the appropriate target_val and return it. """
        if rule[T_FID] in [T_IPV6_DEV_PREFIX, T_IPV6_APP_PREFIX]:
            assert isinstance(target_val, str)
            # don't need to consider the prefix length less than 64
            # because ipaddress.ip_network expands the taret_val into 128bits.
            a = ipaddress.ip_network(target_val, strict=False)
            tv = a[0].packed[:64]
            out_bbuf.add_bytes(tv)
        elif rule[T_FID] in [T_IPV6_DEV_IID, T_IPV6_APP_IID]:
            assert isinstance(target_val, str)
            tv = ipaddress.ip_address(target_val).packed[64:]
            out_bbuf.add_bytes(tv)
        else:
            tv = target_val
            out_bbuf.add_bits(tv, rule[T_FL])
        self.protocol._log("MO {}: copy {}".format(rule[T_MO], tv))
        return tv

    def rx_cda_not_sent(self, rule, in_bbuf, out_bbuf):
        return self.cda_copy_field(rule, out_bbuf, rule[T_TV])

    def rx_cda_val_sent(self, rule, in_bbuf, out_bbuf):
        # XXX not implemented that the variable length size.
        val = in_bbuf.get_bits(rule[T_FL])
        out_bbuf.add_bits(val, rule[T_FL])
        return val

    def rx_cda_map_sent(self, rule, in_bbuf, out_bbuf):
        # 7.5.5.  mapping-sent CDA
        # The number of bits sent is the minimal size for coding all the
        # possible indices.
        size = len(bin(len(rule[T_TV]))[2:])
        val = in_bbuf.get_bits(size)
        return self.cda_copy_field(rule, out_bbuf, rule[T_TV][val])

    def rx_cda_lsb(self, rule, in_bbuf, out_bbuf):
        assert rule[T_MO] == T_MO_MSB
        #
        # the value should consist of:
        #
        #    |<------------ T_FL ------------>|
        #    |<-- T_MO_VAL -->|
        #    |      T_TV      |  field value  |
        #
        out_bbuf.add_bits(rule[T_TV], rule[T_MO_VAL])
        size = rule[T_FL] - rule[T_MO_VAL]
        val = in_bbuf.get_bits(size)
        out_bbuf.add_bits(val, size)
        return val

    def rx_cda_comp_len(self, rule, in_bbuf, out_bbuf):
        # will update the length field later.
        out_bbuf.add_bits(0, rule[T_FL])

    def rx_cda_comp_cksum(self, rule, in_bbuf, out_bbuf):
        # will update the length field later.
        out_bbuf.add_bits(0, rule[T_FL])

    def decompress(self, context, packet_bbuf, di=T_DIR_DW):
        """ decompress the data in the packet_bbuf according to the rule_set.
        return the decompressed data.
        or return None if any error happens.
        Note that it saves the content of packet_bbuf.

        XXX how to consider the IPv6 extension headers.
        """
        assert isinstance(packet_bbuf, BitBuffer)
        assert di in [T_DIR_UP, T_DIR_DW]
        input_bbuf = packet_bbuf.copy()
        output_bbuf = BitBuffer()
        rule = context["comp"]
        # skip ruleID if needed.
        if rule["ruleID"] is not None and rule["ruleLength"] is not None:
            rule_id = input_bbuf.get_bits(rule["ruleLength"])
            if rule_id != rule["ruleID"]:
                self.protocol._log("rule_id doesn't match. {} != {}".format(
                        rule_id, rule["ruleID"]))
                return None
        for r in rule["compression"]["rule_set"]:
            # XXX need to handle "DI"
            self.protocol._log("rule item: {}".format(r))
            # if match the rule, call CDA.
            val = self.__func_rx_cda[r[T_CDA]](r, input_bbuf, output_bbuf)
            # update info to build the IPv6 pseudo header.
            if r[T_FID] == T_IPV6_NXT:
                self.next_proto = val
            elif r[T_FID] == T_IPV6_DEV_PREFIX:
                if di == T_DIR_UP:
                    self.src_prefix = val
                else:
                    self.dst_prefix = val
            elif r[T_FID] == T_IPV6_DEV_IID:
                if di == T_DIR_UP:
                    self.src_iid = val
                else:
                    self.dst_iid = val
            elif r[T_FID] == T_IPV6_APP_PREFIX:
                if di == T_DIR_UP:
                    self.dst_prefix = val
                else:
                    self.src_prefix = val
            elif r[T_FID] == T_IPV6_APP_IID:
                if di == T_DIR_UP:
                    self.dst_iid = val
                else:
                    self.src_iid = val
            elif r[T_FID].startswith(T_PROTO_ICMPV6):
                self.cksum_field_offset = 42
            elif r[T_FID].startswith(T_PROTO_UDP):
                self.cksum_field_offset = 46
            #
        if input_bbuf.count_remaining_bits() > 0:
            output_bbuf += input_bbuf
        # update the ipv6 payload.
        self.ipv6_payload = output_bbuf.get_content()[40:]
        # update the field of IPv6 length.
        output_bbuf.add_bits(len(self.ipv6_payload), 16, position=32)
        # update the checksum field of the upper layer.
        if self.cksum_field_offset:
            assert self.ipv6_payload is not None
            cksum = self.cal_checksum(self.build_ipv6_pseudo_header() + self.ipv6_payload)
            output_bbuf.add_bits(cksum, 16, position=self.cksum_field_offset)
        # if all process have been succeeded, return the data.
        self.protocol._log("decompress: {}=>{}".format(
            packet_bbuf, output_bbuf))
        return output_bbuf

#---------------------------------------------------------------------------
