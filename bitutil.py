def int_to_bit(n, nbits, lsb0=True):
    '''
    convert the integer into a bit string of the number of bits specified.

    e.g. if n is in bit is "0111",
    if nbits is 5 and lsb0 is True, then it's gonna be "00111".
    if lsb0 is False, then its' gonna be "11100".
    if nbits is less than n in bit, omit the bits. overflow in other word.
    e.g. if n is in bit is "11110000" and nbits is 6, then it gonna be "110000".
    '''
    if lsb0:
        return zfill(bin(n)[2:], nbits)[-nbits:]
    else:
        return zfill(bin(n)[2:], nbits)[-nbits:][::-1]

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

def bit_set(ba, pos, val=None, extend=False):
    '''
    set a bit or a series of bits at the position in the bytearray.
    the position of the most left bit is 0.

    ba: bytearray
    pos: bit position from the head

        i.e.
         position:   0  1  2  3  4  5  6  7  8  9 10 11 12 13
              bit:   0  0  0  0  0  0  0  0  0  0  0  0  0  0
        bytearray:   --------- 0 ----------|--------- 1 -----

    val:
        if the type of val is None, it sets a bit on at the position in the ba.

        if the type is bool, then at the position,
        it sets a bit off if the val is False,
        otherwise sets a bit on.

        if the type is int,
        or if the type is str (it must consist of "0" and "1"),
        this sets bits from the position.

        e.g. the following operation is gonna be "0000 0011 1100 0000"
            ba = bytearray(2)
            bit_set(ba, 6, "1111")
            bit_set(ba, 6, 15)

    extend:
        if True, it extends the size of ba when the position is over the size.
    '''
    p0 = pos >> 3
    p1 = pos % 8
    if extend == True:
        # extend the buffer if needed.
        bit_len = 1
        if isinstance(val, str):
            bit_len = len(val)
        ext_len = (((pos+bit_len+7)&(~7))>>3) - len(ba)
        if ext_len > 0:
            # micropython is required to convert the list into the bytearray.
            # CPython doesn't require so, and converting doesn't affect.
            #ba.extend([0 for i in range(ext_len)])
            ba.extend(bytearray([0 for i in range(ext_len)]))
    elif not (p0 < len(ba)):
        # just return if the buffer size is shoter than the position
        return ba
    #
    if val is None:
        b = zfill(bin(ba[p0])[2:], 8)
        ba[p0] = int(b[:p1] + "1" + b[p1+1:], 2)
        return ba
    elif isinstance(val, bool):
        b = zfill(bin(ba[p0])[2:], 8)
        ba[p0] = int(b[:p1] + ("1" if val else "0") + b[p1+1:], 2)
        return ba
    elif isinstance(val, int):
        return bit_set(ba, pos, bin(val)[2:])
    elif isinstance(val, str):
        guard_pos = len(ba) << 3
        for i in val:
            ba = bit_set(ba, pos, (False if i == "0" else True))
            pos += 1
            if guard_pos == pos:
                # don't raise an error anyway.
                break
        return ba
    else:
        raise ValueError("invalid val, not allow %s" % (type(val)))

def bit_get(ba, pos, val=None, ret_type=bin):
    '''
    get a bit at the position in the bytearray.
    pos: see bit_get().
    val: if the type of val is None, it gets a value of the bit
        from the position, and returns either "1" or "0" in string.
        if the type is a number, it gets a series of the value of the bits
        from the position toward right and return the bit string of the value.
        if the position is greater than the length of ba, it returns None.

        e.g. if ba in bit is "00001111", bit_get(ba, 2, 4) is gonna be "0011".

    ret_type: specify the type of return value.
        either 'int', 'bin', 'bytes', 'hex' is available.
        'bin' means to return a binary string.
        if the type is bytes, the bits are aligned to the left.
        i.e. "0011" is gonna be 0x30.
        default is bin.
    '''
    p0 = pos >> 3
    p1 = pos % 8
    if val is None:
        if p0 < len(ba):
            b = zfill(bin(ba[p0])[2:], 8)
            ret = ("1" if b[p1] == "1" else "0")
        else:
            return None
    elif isinstance(val, int):
        # if the bit length is zero, it returns None.
        if val == 0:
            return None
        # construct the bit string.
        ret = ""
        for i in range(val):
            r = bit_get(ba, pos+i)
            if r != None:
                ret += r
    else:
        raise ValueError("invalid val, not allow %s" % (type(val)))
    #
    if ret_type == int:
        return int(ret, 2)
    elif ret_type == hex:
        return hex(int(ret, 2))[2:]
    elif ret_type == bytes:
        return bit_set(bytearray(1), 0, ret, extend=True)
    elif ret_type == bin:
        return ret
    else:
        raise ValueError("invalid ret_type, not allow %s" % (ret_type))

def bit_find(n, bit_len=0, val=None):
    '''
    find a position where a bit is on bit in n.
    return the number of the position where the bit set.
    and return the number that the bit found in n is turned off.
    however, note that the significant bits is taken from the most right in n.
    the position of the most left bit is 0.
    if there is no bit set, return None.
    XXX not yet supported. but, if val is a bit string,
    it try to find the series of bits in n.
    '''
    if not bit_len:
        bit_len = len(bin(n)[2:])
    for i in range(bit_len):
        x = 2**(bit_len-i-1)
        if n & x:
            return i, n-x
    return None, n

def bit_count(n, bit_len, zero=False):
    '''
    count the number of bits in the bit string.
    if zero is False (default), it counts a bit which is "1".
    if zero is True, it counts a bit which is "0".

    bit_len indicates that the n has the bit width at minimum.
    '''
    b = "0" if zero else "1"
    bs = int_to_bit(n, bit_len)
    nb = 0
    for i in range(len(bs)):
        if bs[i] == b:
            nb += 1
    return nb

