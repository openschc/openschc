
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
