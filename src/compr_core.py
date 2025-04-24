"""
.. module:: compr_core
   :platform: Python, Micropython
"""
from gen_base_import import *
from gen_utils import dprint
from gen_parameters import *

import pprint



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

    def __init__(self, protocol=None):
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
            T_CDA_REV_COMPRESS: self.tx_cda_compress
            }

    def init(self):
        pass

    def tx_cda_not_sent(self, field, rule, output, device_id=None):
        pass

    def tx_cda_val_sent(self, field, rule, output, device_id=None):
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

    def tx_cda_map_sent(self, field, rule, output, device_id=None):
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

    def tx_cda_lsb(self, field, rule, output, device_id=None):
        assert rule[T_MO] == T_MO_MSB
 
        lsb_size = field[1] - rule[T_MO_VAL]

        value = field[0]
        
        while len(value) < field[1]//8: #zeros on the right may be removed
            value = b'\x00' + value

        if rule[T_FL] == T_FUNCTION_VAR:
            assert (lsb_size%8 == 0) #var implies bytes

            output.add_length(lsb_size//8)

        bit_position = rule[T_MO_VAL]

        while bit_position < len(value)*8:
            pos_byte = bit_position//8   # go to the byte to send
            pos_bit  = 7-bit_position%8  # in that byte how many bits left

            bit_value = value[pos_byte] & (1 << pos_bit)

            #print (bit_position, pos_byte, pos_bit, bit_value)
            output.set_bit(bit_value)

            bit_position += 1

    def tx_cda_compress(self, field, rule, output, device_id=None):
        x, d_is = self.protocol._apply_compression(device_id, field[0], reverse_direction=True)
        print (x)
        if rule[T_FL] == "var":
            output.add_length(len(x._content))

        compr_payload=x._content

        for i in range (0, len(compr_payload)):
            output.add_bits(compr_payload[i], 8)
            output.display()


    def tx_cda_notyet(self, field, rule, output, device_id=None):
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

    def compress(self, rule, parsed_packet, data, direction=T_DIR_UP, device_id = None, verbose=False):
        """
        Take a compression rule and a parsed packet and return a SCHC pkt
        """
        assert direction in [T_DIR_UP, T_DIR_DW]
        output_bbuf = BitBuffer()
        # set ruleID first.
        if rule[T_RULEID] is not None and rule[T_RULEIDLENGTH] is not None:
            output_bbuf.add_bits(rule[T_RULEID], rule[T_RULEIDLENGTH])
            #dprint("rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
            #output_bbuf.display(format="bin")

        for r in rule["Compression"]:
            #print("rule item:", r)

            if r[T_DI] in [T_DIR_BI, direction]:
                if (r[T_FID], r[T_FP]) in parsed_packet:
                    #dprint("in packet")
                    self.__func_tx_cda[r[T_CDA]](field=parsed_packet[(r[T_FID], r[T_FP])],
                                                rule = r,
                                                output= output_bbuf,
                                                device_id=device_id)
                else: # not find in packet, but is variable length can be coded as 0
                    #dprint("send variable length")
                    self.__func_tx_cda[T_CDA_VAL_SENT](field = [0, 0, "Null Field"], rule = r, output = output_bbuf)
            else:
                #dprint("rule skipped, bad direction")
                pass
            if verbose:
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
            if type(rule[T_TV]) == bytes:
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
            size_byte = self.parsed_packet[(T_COAP_TKL, 1)][0]
            size = int.from_bytes(size_byte, "big")*8
            #print("token size", size)
        elif type (rule[T_FL]) == int:
            size = rule[T_FL]
        else:
            raise ValueError("cannot read field length")
        #in_bbuf.display("bin")
        val = in_bbuf.get_bits(size)
        val_ba = adapt_value(val)

        return [val_ba, size]


    def rx_cda_map_sent(self, rule, in_bbuf):
        # 7.5.5.  mapping-sent CDA
        # The number of bits sent is the minimal size for coding all the
        # possible indices.

        assert (type(rule[T_TV]) is list)

        read_size = len(bin(len(rule[T_TV])-1)[2:])
        index = in_bbuf.get_bits(read_size)


        if index < len(rule[T_TV]):
            value = rule[T_TV][index]
            size = len(value)*8
        else:
            print("Warning: Mapping index ({}) larger than TV size ({}), set to None".format(index, len(rule[T_TV])))
            value = None
            size = 0

        return [value, size]

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

        value = int.from_bytes(rule[T_TV], "big")

        for i in range(total_size, send_length, -1):
            bit = value & (0x01 << (i-1))
            tmp_bbuf.set_bit(bit)

        val = in_bbuf.get_bits(send_length)
        tmp_bbuf.add_value(val, send_length)

        return [bytes(tmp_bbuf.get_remaining_content()), total_size]

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
            #dprint(r)
            if r[T_DI] in [T_DIR_BI, direction]:
                full_field = self.__func_rx_cda[r[T_CDA]](r, schc)
                #dprint("<<<", full_field)
                self.parsed_packet[(r[T_FID], r[T_FP])] = full_field
                #pprint.pprint (self.parsed_packet)

        return self.parsed_packet

#---------------------------------------------------------------------------
