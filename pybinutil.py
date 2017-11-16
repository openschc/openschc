'''
to_foo() measns that a bytearray is converted into a foo.
e.g. to_bitstring() means that a bytearray is converted into a bitstring.
foo_to() meaans that a foo is converted into a bytearray.
'''

def to_bit(buf):
    return [zfill(bin(i)[2:],8) for i in buf]

def int_to(n, nbytes, bigendian=True):
    '''
    e.g. if n in hex is "123",
    if nbytes is 3 and endian is "big", then it's gonna be "000123".
    if endian is not "big", then it's gonna be "230100".
    '''
    h = zfill("%x"%n, 2*nbytes)
    x = [int(h[i:i+2],16) for i in range(0, len(h), 2)]
    return bytearray(x) if bigendian else bytearray(x[::-1])

def to_int(ba, reverse=False):
    n = 0
    if reverse:
        ba = ba[::-1]
    for i in ba:
        n = (n<<8) + i
    return n

def int_to_bit(n, nbits, lsb0=True):
    '''
    e.g. if n is in bit is "0111",
    if nbits is 5 and lsb0 is True, then it's gonna be "00111".
    if lsb0 is False, then its' gonna be "01110".
    '''
    if lsb0:
        return zfill(bin(n)[2:], nbits)
    else:
        return rzfill(bin(n)[2:], nbits)

def bitset(ba, pos, val=None):
    '''
    ba: bytearray
    pos: bit position from the head

        i.e.
         position:   0  1  2  3  4  5  6  7  8  9 10 11 12 13
              bit:   0  0  0  0  0  0  0  0  0  0  0  0  0  0
        bytearray:   --------- 0 ----------|--------- 1 -----

    val: if the type of val is None, this sets a bit on at the position.

        if the type is bool, then at the position,
        this sets a bit off if the val is False,
        otherwise sets a bit on.

        if the type is int,
        or if the type is str (it must consist of "0" and "1"),
        this sets bits from the position.

        e.g. the following operation is gonna be "0000 0011 1100 0000"
            ba = bytearray(2)
            bitset(ba, 6, "1111")
            bitset(ba, 6, 15)
    '''
    p0 = pos >> 3
    p1 = pos % 8
    if not (p0 < len(ba)):
        return ba
    if val is None:
        b = zfill(bin(ba[p0])[2:], 8)
        ba[p0] = int(b[:p1] + "1" + b[p1+1:], 2)
        return ba
    elif type(val) is bool:
        b = zfill(bin(ba[p0])[2:], 8)
        ba[p0] = int(b[:p1] + ("1" if val else "0") + b[p1+1:], 2)
        return ba
    elif type(val) is int:
        return bitset(ba, pos, bin(val)[2:])
    elif type(val) is str:
        guard_pos = len(ba) * 8
        for i in val:
            ba = bitset(ba, pos, (False if i == "0" else True))
            pos += 1
            if guard_pos == pos:
                # don't raise an error anyway.
                break
        return ba
    else:
        raise ValueError("invalid val, not allow %s" % (type(val)))

def bitget(ba, pos, val=None, integer=False):
    '''
    val: if the type of val is None, this gets a value of the bit
        from the position, and return "1" or "0".

        if the type is int, this gets a series of value of the bits
        from the position and return the bit string of the value.

        e.g. if sbitarray is ba = "00001111",
        bitget(ba, 2, 4) is gonna be "0011".
    '''
    p0 = pos >> 3
    p1 = pos % 8
    if val is None:
        b = zfill(bin(ba[p0])[2:], 8)
        ret = ("1" if b[p1] == "1" else "0")
    elif type(val) is int:
        # if the bit length is zero, it returns None.
        if val == 0:
            return None
        # construct the bit string.
        ret = ""
        for i in range(val):
            ret += "1" if bitget(ba, pos+i) == "1" else "0"
    else:
        raise ValueError("invalid val, not allow %s" % (type(val)))
    #
    if integer:
        return int(ret, 2)
    return ret

def rzfill(s, w):
    '''
    pycom doesn't support str.zfill()
    '''
    return s + "".join(["0" for i in range(w-len(s))])

def zfill(s, w):
    '''
    pycom doesn't support str.zfill()
    '''
    return "".join(["0" for i in range(w-len(s))]) + s

