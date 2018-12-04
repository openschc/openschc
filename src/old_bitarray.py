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
