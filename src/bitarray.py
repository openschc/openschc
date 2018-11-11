#---------------------------------------------------------------------------
# C.A. 2018
#---------------------------------------------------------------------------

BITS_PER_BYTE = 8

#---------------------------------------------------------------------------

class FakeBitBuffer:
    """This is a FakeBitBuffer, that does not do actual bit formatting,
    just logs all the bits/nb_bits pairs that have been pushed,
    and can be used to pop them later"""
    def __init__(self, content=[]):
        self.content = content[:]

    def add_bits(self, bits_as_long, nb_bits):
        self.content.append((bits_as_long, nb_bits))

    def add_bytes(self, raw_data):
        for raw_byte in raw_data:
            self.add_bits(raw_byte, BITS_PER_BYTE)

    def get_bits(self, nb_bits):
        bits_as_long, added_nb_bits = self.content.pop(0)
        assert nb_bits == added_nb_bits
        return bits_as_long

    def get_bits_as_buffer(self, nb_bits):
        result = FakeBitBuffer()
        while result.count_bits() < nb_bits:
            __, next_nb_bits = self.content[0]
            bits = self.get_bits(next_nb_bits)
            result.add_bits(bits, next_nb_bits)
        return result

    def get_content(self):
        return self.content[:]

    def count_bits(self):
        result = 0
        for value, size in self.content:
            result += size
        return result

#---------------------------------------------------------------------------

# XXX: need to optimize: add_bytes, get_bytes
# XXX: separate adding/getting

class SlowBitBuffer:
    """This is a BitBuffer based on bytearray.
    One can add/remove bits and bytes.
    """
    def __init__(self, content=None, should_record_add=False):
        if content is not None:
            self.content = content
        else:
            self.content = bytearray()
        self.pending_bits = 0
        self.pending_count = 0
        if should_record_add:
            self._log = []
        else:
            self._log = None

    def add_bits(self, bits, nb_bits):
        if self._log is not None:
            self._log.append(("bits", bits, nb_bits))
        if nb_bits == 0:
            return
        mask = 1<<(nb_bits-1)
        for i in range(nb_bits):
            assert mask != 0
            current_bit = 1 if ((bits & mask) != 0) else 0
            self._add_one_bit(current_bit)
            mask = mask >> 1
        assert mask == 0

    def get_content(self):
        if self.pending_count != 0:
            raise RuntimeError("Unpadded content", self.pending_count)
        return self.content[:]

    def add_bytes(self, raw_data):
        if self._log is not None:
            self._log.append(("bytes", raw_data))
        for raw_byte in raw_data:
            self.add_bits(raw_byte, BITS_PER_BYTE)

    def ensure_padding(self):
        count = 0
        while self.pending_count != 0:
            self._add_one_bit(0)
            count += 1
        return count

    def count_remaining_bits(self):
        return len(self.content)*BITS_PER_BYTE + self.pending_count

    def count_added_bits(self):
        return len(self.content)*BITS_PER_BYTE + self.pending_count

    def get_bits(self, nb_bits):
        if nb_bits == 0:
            return 0
        mask = 1<<(nb_bits-1)
        result = 0
        for i in range(nb_bits):
            assert mask != 0
            if self._get_one_bit() == 1:
                result |= mask
            mask = mask >> 1
        assert mask == 0
        return result

    def get_bits_as_buffer(self, nb_bits):
        result = SlowBitBuffer()
        for bit_index in range(nb_bits):
            result._add_one_bit(self._get_one_bit())
        assert result.count_added_bits() == nb_bits
        result.ensure_padding()  # XXX: result size can be bigger than nb_bit
        return result

    def _push_from_pending(self):
        assert self.pending_count == BITS_PER_BYTE
        self.content.append(self.pending_bits)
        self.pending_bits = 0
        self.pending_count = 0

    def _pop_to_pending(self):
        assert self.pending_count == 0
        self.pending_bits = self.content[0]
        self.content = self.content[1:]
        self.pending_count = BITS_PER_BYTE

    def _add_one_bit(self, one_bit):
        assert one_bit == 0 or one_bit == 1
        assert self.pending_count < BITS_PER_BYTE  # invariant
        self.pending_bits = (self.pending_bits << 1) | one_bit
        self.pending_count += 1
        if self.pending_count >= BITS_PER_BYTE:
            self._push_from_pending()

    def _get_one_bit(self):
        if self.pending_count == 0:
            self._pop_to_pending()
        assert self.pending_count >= 1
        mask = 1 << (self.pending_count-1)
        if self.pending_bits & mask != 0:
            self.pending_bits ^= mask
            result = 1
        else:
            result = 0
        self.pending_count -= 1
        return result

    def __repr__(self):
        #if self._log is not None:
        return "BitBuffer({})".format(self.__dict__)

    def display(self):
        print(self)

#---------------------------------------------------------------------------

class BitBuffer:

    def __init__(self, content=b""):
        """BitBuffer manage a buffer bit per bit.
        content: any objects which can be passed to bytes or bytearray.
        _wpos: always indicating the last next bit position for set_bit()
               without position.
        _rpos: indicating the bit position to be read for get_bits() without
               position.
        """
        self._content = bytearray(content)
        self._wpos = len(content)*8  # write position
        self._rpos = 0  # read position

    def set_bit(self, bit, position=None):
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
        if position is not specified, the nb_bits are added at the end of the buffer.
        if position is specified the nb_bits are set at the buffer position. Position
        defines the position if the most significant bit. """

        if position == None:
            for i in range(nb_bits, 0, -1):
                self.set_bit(bits_as_long & (0x01 << (i-1)))
        else:
            for i in range(0, nb_bits):
                self.set_bit(bits_as_long & (0x01 << (nb_bits-i -1)), position=position+i)


# to be rewritten
    def add_bytes(self, raw_data, position=None):
        for raw_byte in raw_data:
            self.add_bits(raw_byte, BITS_PER_BYTE, position=position)

    def get_bits(self, nb_bits=1, position=None):
        """ return a integer containinng nb_bits from the position"""

        value = 0x00

        if position == None:
            if self._rpos + nb_bits > self._wpos:  # go after buffer # XXX: > or >=?
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

#to be optimized
    def get_bits_as_buffer(self, nb_bits):
        result = BitBuffer()
        for bit_index in range(nb_bits):
            result.add_bits(self.get_bits(1), 1)
        return result

    def ensure_padding(self):
        count = (BITS_PER_BYTE-self._wpos) % BITS_PER_BYTE
        self.add_bits(0, count)
        return count

    def _old_get_content(self):
        return self._content

    def get_content(self):
        assert self._rpos % BITS_PER_BYTE == 0
        #nb_bits = self.count_remaining_bits()
        #assert nb_bits % BITS_PER_BYTE == 0
        return self._content[self._rpos // BITS_PER_BYTE:]

    # Renamed because of bad ambiguity:
    #def count_bits(self):
    #    return self._wpos

    def count_remaining_bits(self):
        '''
        return the number of the significant bits.
        '''
        return len(self._content)*BITS_PER_BYTE - self._rpos

    def count_added_bits(self):
        '''
        return the number of holder space of the significant bits in bits.
        '''
        return self._wpos

    def display(self):
        print ("{}/{}".format(self._content, self._wpos))

    def __repr__(self):
        return "{}/{}".format(self._content, self._wpos)

    def __add__(self, other):
        for bit_index in range(other.count_added_bits()):
            self.add_bits(other.get_bits(1), 1)
        return self

#BitBuffer =
NewBitBuffer = BitBuffer

if __name__ == "__main__":
    bb = NewBitBuffer()
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

    bb.display()

    for i in range(0, 13):
        print(bb.get_bits(8))

#---------------------------------------------------------------------------
