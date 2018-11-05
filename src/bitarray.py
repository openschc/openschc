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

    def count_bits(self):
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
        assert result.count_bits() == nb_bits
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

#---------------------------------------------------------------------------

class NewBitBuffer:
    """BitBuffer manage a buffer bit per bit. """

    def __init__(self, content=b""):
        self._content = bytearray(content)
        self._wpos = 0  # read position
        self._rpos = 0  # write position

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



    def add_bytes(self, raw_data, position=None):
        for raw_byte in raw_data:
            self.add_bits(raw_byte, BITS_PER_BYTE, position=position)

    def get_bits(self, nb_bits):
        bits_as_long, added_nb_bits = self._content.pop(0)
        assert nb_bits == added_nb_bits
        return bits_as_long

    def get_bits_as_buffer(self, nb_bits):
        result = BitBuffer()
        while result.count_bits() < nb_bits:
            __, next_nb_bits = self._content[0]
            bits = self.get_bits(next_nb_bits)
            result.add_bits(bits, next_nb_bits)
        return result

    def get_content(self):
        return self._content

    def count_bits(self):
        result = 0
        for value, size in self._content:
            result += size
        return result

    def ensure_padding(self):
        pass  # In this class, this is ensured by design

if __name__ == "__main__":
    print ("here")
    bb = BitBuffer()
    for i in range(0,32):
        bb.set_bit(1)
    bb.set_bit(1, position=80 )
    print ("->", bb.get_content())
    bb.set_bit(0, position=7 )
    print ("->", bb.get_content())

    bb.add_bits(0x01, 4)
    print ("->", bb.get_content())

    bb.add_bits(0x01, 3, position=40)
    print ("->", bb.get_content())

#---------------------------------------------------------------------------
