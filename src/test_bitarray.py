import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")

from base_import import *  # used for now for differing modules in py/upy
if sys.implementation.name != "micropython":
    import pytest


def make_bits_list():
    bits_list = [
        (0xf, 4),
        (0,   0),
        (0,   2),
        (0,   0),
        (0x1, 2),
        (0,   0),
        (0x3, 2),
        (0,   0),
    ]
    for i in range(3):
        bits_list.append((0,   1))
        bits_list.append((0x1, 1))
    for i in range(1, 128):
        v = (2**i)-2
        assert ((v+2) >> i) == 1  # no overflow
        bits_list.append((v, i))

    return bits_list


def test_bitbuffer_consistency():
    bits_list = make_bits_list()
    #bitbuffer = BitBuffer(should_record_add=True)
    bitbuffer = BitBuffer()
    for bits, nb_bits in bits_list:
        bitbuffer.add_bits(bits, nb_bits)

    padding_bitsize = bitbuffer.ensure_padding()
    content = bitbuffer.get_content()
    bitbuffer2 = BitBuffer(content)

    for i, (bits, nb_bits) in enumerate(bits_list):
        with_sub_buffer = ((i % 2) == 0)
        #with_sub_buffer = False
        if with_sub_buffer:
            sub_bitbuffer = bitbuffer2.get_bits_as_buffer(nb_bits)
            bits2 = sub_bitbuffer.get_bits(nb_bits)
        else:
            bits2 = bitbuffer2.get_bits(nb_bits)
        assert bits == bits2  # XXX: raise exception instead when wrong

    #print(bitbuffer2)

    assert bitbuffer2.get_bits(padding_bitsize) == 0
    assert len(bitbuffer2.get_content()) == 0  # XXX: raise exception when not


def test_check_newbitbuffer_consistency():
    bits_list = make_bits_list()
    print (bits_list)

    bitbuffer = BitBuffer()
    for bits, nb_bits in bits_list:
        bitbuffer.add_bits(bits, nb_bits)

    bitbuffer.display()

    content = bitbuffer.get_content()
    bitbuffer2 = BitBuffer(content)
    for bits, nb_bits in bits_list:
        bits2 = bitbuffer2.get_bits(nb_bits)
        print (bits, nb_bits, bits2)
        assert bits == bits2  # XXX: raise exception
#    assert len(bitbuffer2.get_content()) == 0  # XXX: raise exception


# for micropython and other tester.
if __name__ == "__main__":
    test_bitbuffer_consistency()
    test_check_newbitbuffer_consistency()
