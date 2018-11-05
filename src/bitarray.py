
BITS_PER_BYTE = 8

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


class BitBuffer:
    """BitBuffer manage a buffer bit per bit. """

    def __init__(self, content=b""):
        self._content = bytearray(content)
        self._wpos = len(content)*8  # read position
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
            
        
# to be rewritten
    def add_bytes(self, raw_data, position=None):
        for raw_byte in raw_data:
            self.add_bits(raw_byte, BITS_PER_BYTE, position=position)

    def get_bits(self, nb_bits=1, position=None):
        """ return a integer containinng nb_bits from the position"""

        if self._rpos + nb_bits > self._wpos:  # go after buffer
            raise ValueError ("data out of buffer")

        if position == None:
            value = 0x00
        
            for i in range(0, nb_bits):
                value <<=1
                byte_index = self._rpos >> 3
                offset     = 7 - (self._rpos & 7)

                bit = self._content[byte_index] & (0x01 << offset)
            
                if (bit != 0):
                    value |= 0x01

                self._rpos += 1

            return value
            
        bits_as_long, added_nb_bits = self.content.pop(0)
        assert nb_bits == added_nb_bits
        return bits_as_long

    
#not implemented
    def get_bits_as_buffer(self, nb_bits):
        result = FakeBitBuffer()
        while result.count_bits() < nb_bits:
            __, next_nb_bits = self.content[0]
            bits = self.get_bits(next_nb_bits)
            result.add_bits(bits, next_nb_bits)
        return result

    def get_content(self):
        return self._content


    def count_bits(self):
        return self._wpos

    def display(self):
        print ("{}/{}".format(self._content, self._wpos))
        
    
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
    bb.align()

    bb.display()

    for i in range(0, 13):
        print(bb.get_bits(8))
        
