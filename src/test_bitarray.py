
from base_import import *  # used for now for differing modules in py/upy


def test_BitBuffer():
    bits_list = [
        (0xf, 4),
        (0,   2),
        (0x1, 2),
        (0x3, 2)
    ]
    for i in range(3):
        bits_list.append((0,   1))
        bits_list.append((0x1, 1))
    for i in range(1, 128):
        v = (2**i)-2
        assert ((v+2) >> i) == 1  # no overflow
        bits_list.append((v, i))

    bitbuffer = BitBuffer()
    for bits, nb_bits in bits_list:
        bitbuffer.add_bits(bits, nb_bits)

    content = bitbuffer.get_content()
    bitbuffer2 = BitBuffer(content)
    for bits, nb_bits in bits_list:
        bits2 = bitbuffer2.get_bits(nb_bits)
        assert bits == bits2  # XXX: raise exception

    assert len(bitbuffer2.get_content()) == 0  # XXX: raise exception


test_BitBuffer()
