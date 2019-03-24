import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")

from bitarray import BitBuffer
if sys.implementation.name != "micropython":
    import pytest


# XXX better to separate into each test case.
def test_bitarray2():
    print("""
    ## set_bit()
        """)
    a = BitBuffer()
    a.set_bit(0)
    a.set_bit(0)
    a.set_bit(1)
    a.set_bit(1)
    a.set_bit(1)
    a.set_bit(0)
    a.set_bit(1)
    print(a.get_content()) # 0011 1010 : \x3a
    print(a)
    assert str(a) == r"b'\x3a'/7"

    a.set_bit(1, 0)
    a.set_bit(0, 3)
    print(a.get_content()) # 1010 1010 : \xaa
    print(a)
    assert str(a) == r"b'\xaa'/7"

    print("""
    ## add_bits()
        """)
    a = BitBuffer()
    a.add_bits(7, 4) # rule : 0111
    a.add_bits(2, 3) # dtag : 010
    print("added bits:", a.count_added_bits())
    print("padding bits:", a.count_padding_bits())
    print("remaining bits:", a.count_remaining_bits())
    assert a.count_added_bits() == 7
    assert a.count_padding_bits() == 1
    assert a.count_remaining_bits() == 7
    a.add_bits(3, 3) # win  : 011
    a.add_bits(6, 3) # fcn  : 110
    print(a.get_content())
    print(a)
    # 0111 0100 1111 0000 : \x74f0

    assert str(a) == r"b'\x74\xf0'/13"

    print("""
    ## copy()
        """)
    c = BitBuffer(bytearray([1,2,3,4,5]))
    c.add_bits(5,6)
    d = c.copy()
    print(c)
    print(d)
    assert str(c) == str(d)
    assert id(c) != id(d)
    assert id(c._content) != id(d._content)
    k = 100
    al = [BitBuffer(bytearray([_ for _ in range(16)])) for _ in range(k)]
    b = BitBuffer()
    for i in al:
        b += i
    c = BitBuffer(bytearray([_%16 for _ in range(16*k)]))
    print(c)
    assert str(b) == str(c)

    print("""
    ## get_bits()
        """)
    b = a.copy()
    print(a)
    print(b)
    print(b.get_bits(4), ": rule = 7, rpos =", b._rpos)
    print(b.get_bits(3), ": dtag = 2, rpos =", b._rpos)
    print("added bits:", b.count_added_bits())
    print("padding bits:", b.count_padding_bits())
    print("remaining bits:", b.count_remaining_bits())
    assert b.count_added_bits() == 13
    assert b.count_padding_bits() == 3
    assert b.count_remaining_bits() == 6
    print(b.get_bits(3), ": win  = 3, rpos =", b._rpos)
    print(b.get_bits(3), ": fcn  = 6, rpos =", b._rpos)
    print("remaining bits:", b.count_remaining_bits())
    assert b.count_remaining_bits() == 0

    print("""
    ## get_bits(position)
        """)
    b = a.copy()
    print(b.get_bits(4, 0), ": rule = 7, rpos =", b._rpos)
    print(b.get_bits(3, 4), ": dtag = 2, rpos =", b._rpos)
    print("added bits:", b.count_added_bits())
    print("padding bits:", b.count_padding_bits())
    print("remaining bits:", b.count_remaining_bits())
    assert b.count_added_bits() == 13
    assert b.count_padding_bits() == 3
    assert b.count_remaining_bits() == 13
    print(b.get_bits(3, 7), ": win  = 3, rpos =", b._rpos)
    print(b.get_bits(3,10), ": fcn  = 6, rpos =", b._rpos)
    print("remaining bits:", b.count_remaining_bits())
    assert b.count_remaining_bits() == 13

    print("""
    ## get_bits_as_buffer()
        """)
    b = a.copy()
    b.get_bits(1)
    print(b)
    # a = b'\x74\xf0'/12[1:13]
    #     0111 0100 1111 0000
    # b = b'\xe9\xe0'/12
    #     1110 1001 1110 0000
    c = b.get_bits_as_buffer(3)
    print(c)
    assert str(c) == r"b'\xe0'/3"
    c = b.get_bits_as_buffer()
    print(c)
    assert str(c) == r"b'\x4f\x00'/9"

    print("""
    ## __add__
        """)
    # the header size is 27 bits.
    # frag: 0000 0001 0000 0002 0000 0003 111
    c = BitBuffer(bytearray([1,2,3]))
    c.add_bits(7, 5)
    print("a =", c)
    print("c =", c)
    b = a + c
    print("a + c =", b)
    print("c =", c)
    assert str(b) == r"b'\x74\xf0\x08\x10\x19\xc0'/42"

    print("""
    ### to_bit_list()
        """)
    a = BitBuffer([0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0])
    print(a)
    bl = a.to_bit_list()
    print(bl)
    assert bl == [0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0]

    print("""
    ### allones()
        """)
    a = BitBuffer([1, 1, 1, 1])
    print(a, a.allones())
    assert True == a.allones()
    a = BitBuffer([1, 1, 1, 1, 0])
    print(a, a.allones())
    assert False == a.allones()
    a = BitBuffer([0, 1, 1, 1, 1])
    print(a,"[1:]", a.allones(1))
    assert True == a.allones(1)

    print("""
    ## add_bytes()
        """)
    a = BitBuffer(bytearray([1,2]))
    print(a)
    a.add_bytes(bytearray([3,4]))
    print(a)
    assert str(a) == r"b'\x01\x02\x03\x04'/32"
    a = BitBuffer([0,1,0,1])
    print(a)
    a.add_bytes(bytearray([3,4]))
    print(a)
    assert str(a) == r"b'\x50\x30\x40'/20"


# for micropython and other tester.
if __name__ == "__main__":
    test_bitarray2()
