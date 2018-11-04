
from base_import import *  # used for now for differing modules in py/upy


def check_bitbuffer_consistency(addition_list):
    bits_list = addition_list
    bitbuffer = BitBuffer(should_record_add=True)
    for bits, nb_bits in bits_list:
        bitbuffer.add_bits(bits, nb_bits)

    print("(0)", bitbuffer)
    padding_bitsize = bitbuffer.ensure_padding()
    content = bitbuffer.get_content()
    print("(1)", bitbuffer)

    bitbuffer2 = BitBuffer(content)
    print(bitbuffer._log)

    for i, (bits, nb_bits) in enumerate(bits_list):
        print("PRE", bitbuffer, nb_bits)
        #with_sub_buffer = ((i % 2) == 0)
        with_sub_buffer = True
        if with_sub_buffer:
            sub_bitbuffer = bitbuffer2.get_bits_as_buffer(nb_bits)
            print("->", sub_bitbuffer)
            bits2 = sub_bitbuffer.get_bits(nb_bits)
            print("-> +", sub_bitbuffer)
        else:
            bits2 = bitbuffer2.get_bits(nb_bits)
        print("YOW", bits, bits2)
        assert bits == bits2  # XXX: raise exception instead when wrong

    print(bitbuffer._log)

    assert bitbuffer2.count_bits() == padding_bitsize
    assert bitbuffer2.get_bits(padding_bitsize) == 0
    assert len(bitbuffer2.get_content()) == 0  # XXX: raise exception when not


def test_BitBuffer():
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

    #bits_list = [(127,7), (1,1)]
    bits_list = bits_list[28:29]
    check_bitbuffer_consistency(bits_list)

test_BitBuffer()
