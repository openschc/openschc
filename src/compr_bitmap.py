"""
.. module:: compr_bitmap
   :platform: Python, Micropython

"""
# XXX need to consider the byte boundary.

from gen_utils import dprint

def compress_bitmap(bbuf):
    """
    N FCN
    1 1
        0 0 b'\x00'/1 b'\x00'/1
        1 1 b'\x80'/1 b'\x80'/1

    2 111
        011 01  b'\x60'/3 b'\x40'/2
        101 101 b'\xa0'/3 b'\xa0'/3
        110 110 b'\xc0'/3 b'\xc0'/3
        111 1   b'\xe0'/3 b'\x80'/1

    3 1111111
        0111111 01      b'\x7e'/7 b'\x40'/2
        1011111 101     b'\xbe'/7 b'\xa0'/3
        1101111 1101    b'\xde'/7 b'\xd0'/4
        1110111 11101   b'\xee'/7 b'\xe8'/5
        1111011 111101  b'\xf6'/7 b'\xf4'/6
        1111101 1111101 b'\xfa'/7 b'\xfa'/7
        1111110 1111110 b'\xfc'/7 b'\xfc'/7
        1111111 1       b'\xfe'/7 b'\x80'/1
    """
    #dprint("x0 b =", bbuf, "rpos=",bbuf._rpos, "wpos=",bbuf._wpos)
    i = bbuf.count_added_bits()
    while i > 0:
        i -= 1
        if bbuf.get_bits(1,position=i) == 0:
            break
        #dprint("x1 =", bbuf.get_bits(1,position=i-1))
        if bbuf.get_bits(1,position=i-1) == 0:
            break
    #dprint("x3 b =", bbuf, "i=", i, "rpos=",bbuf._rpos, "wpos=",bbuf._wpos)
    return bbuf.get_bits_as_buffer(i+1)

if __name__ == "__main__":
    from gen_bitarray import BitBuffer

    def test1():
        def compress_bitmap_str(b):
            i = len(b)
            while i > 0:
                if b[i-1] == "0":
                    break
                i -= 1
            return b[:i+1]

        def gen_bits_str(N):
            if N < 1:
                return ""
            if N == 1:
                yield "0"
                yield "1"
            else:
                p = (1<<N)-2
                # 2, 6, 14
                for i in range(p+1):
                    yield "1"*i + "0" + "1"*(p-i)
                yield "1"*(p+1)

        for n in range(5):
            for i in gen_bits_str(n):
                dprint(i, compress_bitmap_str(i))

    def test2():
        def gen_bits(N):
            #
            if N < 1:
                return None
            if N == 1:
                b = BitBuffer()
                b.set_bit(0)
                yield b
                b = BitBuffer()
                b._wpos = 0
                b.set_bit(1)
                yield b
            else:
                p = (1<<N)-2
                for i in range(p+1):
                    b = BitBuffer()
                    b.add_bits(pow(2,i)-1, i)
                    b.set_bit(0)
                    b.add_bits(pow(2,p-i)-1, p-i)
                    yield b
                b = ()
                b.add_bits(pow(2,p+1)-1, p+1)
                yield b

        for n in range(5):
            dprint("n=",n)
            for i in gen_bits(n):
                dprint(i, compress_bitmap(i))

    #test1()
    test2()

