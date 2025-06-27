"""
.. module:: gen_bitarray
    :platform: Code running on MicroPython
    :synopsis: SCHC Bit Buffer Management

"""
from contextlib import redirect_stdout

import sys
# micropython doesn't have fromhex()
from binascii import unhexlify

BITS_PER_BYTE = 8

class BitBuffer:

    def __init__(self, content=b""):
        """ BitBuffer manage a buffer bit per bit.
        The content should be either a list, a string, or a bytearray.
        If the content is a string, it must consist of below format:
            e.g.
            "b'\x01\x02\x03\x04'/32"
            "b'\xd2\x01\x00'/17"
        If the content is a list, each item (0 or others) is dealt as a bit.
        Or, the content should be any objects which can be passed to bytes
        or bytearray.

        _content: bytearray holding the bits including padding.
        _wpos: always indicating the last next bit position.
        _rpos: indicating the bit position to be read for get_bits().

                     _rpos      _wpos
                       v          v
                  bit# 01234567 01234567
                      :--------:--------:  --> _content : bytearray()
           bits added  01011110 001
                       |----------|        --> count_added_bits() = 11
                                  |----|   --> count_padding_bits() = 5
                       |----------|        --> count_remaining_bits() = 11

        once get_bits(3) is called.  the variables will change like below.

                        _rpos   _wpos
                          v       v
                  bit# 01234567 01234567
                      :--------:--------:
                       01011110 001.....
                       |----------|        --> count_added_bits() = 11
                                  |----|   --> count_padding_bits() = 5
                          |-------|        --> count_remaining_bits() = 8

        XXX proposed the expecting behavior. need to be considered.
        set_*(): _wpos doesn't change. except when it add a bit at the tail.
        add_*(): _wpos doesn't change. except when it add a bit at the tail.
        get_*(): increment _rpos()
        copy_*(): _rpos doesn't change.

        """
        if isinstance(content, list):
            self._content = bytearray()
            self._wpos = 0
            self._rpos = 0
            for i in range(len(content)):
                self.set_bit(content[i])
        elif isinstance(content, str):
            c,b = content.split("/")
            c = c.encode("unicode_escape").decode("utf-8")[2:-1]
            if content.find("\\") > 0:
                # it looks a raw literal.
                self._content = bytearray(unhexlify(c.replace("\\\\x","")))
            else:
                self._content = bytearray(unhexlify(c.replace("\\x","")))
            self._wpos = int(b)
            self._rpos = 0
        else:
            self._content = bytearray(content)
            self._wpos = len(content)*8  # write position
            self._rpos = 0  # read position

    def set_bit(self, bit, position=None):
        """ if bit is not 0, set a bit on at the specified position.
        Otherwise, set a bit off.
        if position is not specified, the target bit is the bit specified by
        _wpos, i.e. at the end of buffer, and as the result, _wpos is
        incremented. """
        # XXX needs to check whether it works as defined above.
        if position == None:
            byte_index = (self._wpos >> 3)
            offset = 7 - (self._wpos & 7)

            if len(self._content) < (byte_index + 1):
                self._content.append(0)

            if bit != 0:
                self._content[byte_index] |= (1 << offset)

            self._wpos += 1
        else:
            if position > self._wpos:
                for k in range (0, position - self._wpos):
                    self.set_bit (0)
                self.set_bit(bit)
            else:
                byte_index = (position >> 3)
                offset = 7 - (position & 7)

                msk = 0xFF ^ (0x01 << offset)

                self._content[byte_index] = self._content[byte_index] & msk

                if bit != 0:
                    self._content[byte_index] |= (1 << offset)

    def add_bits(self, bits_as_long, nb_bits, position=None):
        """ write a nb_bits less significant bits of an integer in the buffer.
        if position is not specified, the nb_bits are added at the end of the
        buffer.  if position is specified the nb_bits are set at the buffer
        position. Position defines the position if the most significant bit. """
        if position == None:
            for i in range(nb_bits, 0, -1):
                self.set_bit(bits_as_long & (0x01 << (i-1)))

        else:
            for i in range(0, nb_bits):
                self.set_bit(bits_as_long & (0x01 << (nb_bits-i -1)), position=position+i)

    def add_value(self, value, nb_bits, position=None):
        if type (value) == int:
            self.add_bits(value, nb_bits, position=None)
        elif type (value) == bytes:
            self.add_bits(int.from_bytes(value, "big"), nb_bits, position=None)
        elif type (value) == BitBuffer:
            self.add_value(bytes(value.get_content()), nb_bits, position)
        elif type (value) == str:
            self.add_value(bytes(value, "utf-8"), nb_bits, position)
        else:
            raise ValueError("Unknown type {}".format(type(value)))

    def add_length(self, size):
        """add to the buffer the length with the draft coding:

          The size (using the unit defined in the FL) is encoded as follows:

            o  If the size is between 0 and 14, it is sent as a 4-bits unsigned
                integer.

            o  For values between 15 and 254, 0b1111 is transmitted and then the
                size is sent as an 8 bits unsigned integer.

            o  For larger values of the size, 0xfff is transmitted and then the
                next two bytes contain the size value as a 16 bits unsigned
                integer.

        """
        if size < 0xF:
            #print ("size =======>", size)
            self.add_bits(size, 4)
        elif size < 0xFF:
            #print ("size =================>", size)
            self.add_bits(0x0F, 4)
            self.add_bits(size, 8)
        elif size < 0xFFFF:
            self.add_bits(0xFFF, 12)
            self.add_bits(size, 16)
        else:
            raise ValueError ("Size is too large, should be < 0xFFFF")
         
    def get_length (self):
        val = self.get_bits(4)
        if val == 0xF:
            val = self.get_bits(8)
            if val == 0xFF:
                val = self.get_bits(16)
        return val

    def add_bytes(self, bytes_data, position=None):
        """ write bytes_data as a bytearray into the buffer. """
        bits_as_long = 0
        for i in bytes_data:
            bits_as_long = (bits_as_long << 8) | i
        self.add_bits(bits_as_long, 8*len(bytes_data), position=position)

    def set_read_position(self, value):
        self._rpos = value

    def get_bits(self, nb_bits=1, position=None):
        """ return an integer containinng nb_bits from the position.
        The most left bit is 0.
        if position is not specified, _rpos is incremented so that next
        calling get_bits() without position automatically takes the next bit."""

        value = 0x00

        if position == None:
            if self._rpos + nb_bits > self._wpos:
                # go after buffer # XXX: > or >=?
                raise ValueError ("data out of buffer")

            for i in range(0, nb_bits):
                value <<=1
                byte_index = self._rpos >> 3
                offset     = 7 - (self._rpos & 7)

                bit = self._content[byte_index] & (0x01 << offset)

                if (bit != 0):
                    value |= 0x01

                self._rpos += 1

            return value
        else:
            if position + nb_bits > self._wpos:  # go after buffer
                raise ValueError ("data out of buffer")

            for pos in range(position, position + nb_bits):
                value <<=1
                byte_index = pos >> 3
                offset = 7 - (pos & 7)

                bit = self._content[byte_index] & (0x01 << offset)

                if (bit != 0):
                    value |= 0x01

            return value


    def get_remaining_content(self):
        res = bytearray()

        while self._wpos - self._rpos >= 8:
            x = self.get_bits(nb_bits=8)
            #print (hex(x))
            res.append(x)

        return res

# Used by test procedures
    def get_bits_as_buffer(self, nb_bits=None):
        """ _rpos does change.
        If nb_bits is None, return all remaining bits.
        """
        result = BitBuffer()
        if nb_bits is None:
            nb_bits = self.count_remaining_bits()
        result.add_bits(self.get_bits(nb_bits), nb_bits)
        return result

    def ensure_padding(self):
        count = self.count_padding_bits()
        self.add_bits(0, count)
        return count

    def get_content(self):
        """ return a bytearray containing the remaining bits in _content aligned
        to the byte boundary.
        Note that the number of remaining bits will be lost.
        """
        assert self._rpos % BITS_PER_BYTE == 0
        #nb_bits = self.count_remaining_bits()
        #assert nb_bits % BITS_PER_BYTE == 0
        return self._content[self._rpos // BITS_PER_BYTE:]

    def count_remaining_bits(self):
        """return the number of the remaining bits from
        the position of self._rpos to _wpos. """
        #return len(self._content)*BITS_PER_BYTE - self._rpos
        return self._wpos - self._rpos

    def count_padding_bits(self):
        return (BITS_PER_BYTE-self._wpos) % BITS_PER_BYTE

    def count_added_bits(self):
        """return the number of significant bits from the most left bit."""
        return self._wpos

    def to_bit_list(self, position=None):
        """ return the content in a list of bits. """
        bit_list = []
        if position is None:
            position = self._rpos
        for i in range(position, self._wpos):
            bit_list.append(self.get_bits(1, i))
        return bit_list

# 

    def display(self, format=None, file=sys.stdout):
        """ Display the content, if format is set to "bin" the 
        buffer is in binary, underline shows its size.
        """
        if format == None or format == "hex":
            print ("{}/{}".format("".join(["%02x"%_ for _ in self._content]), self._wpos), file=file)

        if format == "bin":
            for x in self._content:
                print ("{:08b}".format(x), end = "", file=file)
            print ("/{}".format(self._wpos), file=file)
            print ('='*self._rpos, end="", file=file)
            print ("-"*(self._wpos-self._rpos), file=file)

    def save_to_file(self, file_descriptor, format = None):
        """ Save the content to file descriptor, if format is set to "bin" the
        buffer is in binary, underline shows its size.
        """
        with redirect_stdout(file_descriptor):
            self.display(format, file=file_descriptor)


    def allones(self, position=None):
        """ check whether the bits from the position set all 1 or not.
        if they are all ones, return True.  Otherwise, return False.
        if the position is not set, it will checks from _rpos. """
        if position is None:
            position = self._rpos
        for i in range(position, self._wpos):
            if self.get_bits(1, i) == 0:
                return False
        return True

    def copy(self, position=None):
        """ return BitBuffer like get_bits_as_buffer(),
        but _rpos doesn't change. """
        ret = BitBuffer(self._content)
        ret._wpos = self._wpos
        if position is None:
            ret._rpos = self._rpos
        else:
            if ret._wpos > position:
                ret._rpos = position
            else:
                raise ValueError("position is too biig.")
        return ret

    def __repr__(self):
        if self._wpos == 0:
            nb_bits = 0
        else:
            nb_bits = self._wpos - self._rpos
        if self._rpos == 0:
            ap = ""
        else:
            ap = "[{}:{}]".format(self._rpos, self._wpos)
        return "b'{}'/{}{}".format("".join([ "\\x{:02x}".format(i) for i in
                                       self._content ]), nb_bits, ap)

    def __add__(self, other):
        """ copy self._content into another BitBuffer and add other into it.
        Assumed that the remaining bits of other is less than 256 bytes.
        REMOVED THE ASSERT -> was causing problems for files larger than 250 bytes
        """
        new_buf = self.copy()
        other_copy = other.copy()
        remaining_bits = other_copy.count_remaining_bits()
        #assert remaining_bits < 255*8 
        new_buf.add_bits(other_copy.get_bits(remaining_bits),
                         remaining_bits)
        return new_buf

if __name__ == "__main__":
    bb = BitBuffer()
    for i in range(0,32):
        bb.set_bit(1)
    bb.set_bit(1, position=80 )
    bb.display()
    bb.set_bit(0, position=7 )
    bb.display()

    bb.add_bits(0x01, 4)
    bb.display()

    bb.add_bits(0x01, 3, position=100)
    bb.display()

    bb.add_bits(1, 2)
    bb.ensure_padding()


    bb.add_bits(1, 2)
    bb.add_bits(1, 2)
    bb.display()

    test_fec = []
    test_fec.append(bb)
    print(test_fec)

    bb2 = bb.get_content()
    bb3 = bb.get_content()


    print("test : ", bb2 )
    print("test2 : ", bb3 )

    def xor_bytes(a: bytearray, b: bytearray) -> bytearray:
        if len(a) != len(b):
            raise ValueError("Les bytearrays doivent avoir la même taille pour le XOR.")
        return bytearray(x ^ y for x, y in zip(a, b))

    res = BitBuffer(xor_bytes(bb2, bb3))
    #res.ensure_padding()

    print("Résultat :", res)
    #print("Hex :", res.hex())

#---------------------------------------------------------------------------
