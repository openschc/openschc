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
        #print (x)
        if rule[T_FL] == "var":
            output.add_length(len(x._content))

        compr_payload=x._content

        for i in range (0, len(compr_payload)):
            output.add_bits(compr_payload[i], 8)
            #output.display()


    def tx_cda_notyet(self, field, rule, output, device_id=None):
        raise NotImplementedError



    def compress(self, rule, parsed_packet, data, direction=T_DIR_UP, device_id = None):
        """
        Take a compression rule and a parsed packet and return a SCHC pkt
        """
        assert direction in [T_DIR_UP, T_DIR_DW]

        # set active time for device and time

        output_bbuf = BitBuffer()
        # set ruleID first.

        if rule[T_RULEID] is not None and rule[T_RULEIDLENGTH] is not None:
            output_bbuf.add_bits(rule[T_RULEID], rule[T_RULEIDLENGTH])
            dprint("rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
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

            #output_bbuf.display(format="bin")

        #output_bbuf.add_bytes(data)

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
            #dprint("rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
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
