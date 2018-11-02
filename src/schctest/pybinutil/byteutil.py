'''
to_foo() measns that a bytearray is converted into a foo.
e.g. to_bitstring() means that a bytearray is converted into a bitstring.
foo_to() meaans that a foo is converted into a bytearray.
'''

def __rjust(s, w, c="0"):
    return "".join([c for i in range(w-len(s))]) + s

def __ljust(s, w, c="0"):
    return s + "".join([c for i in range(w-len(s))])

def __zfill(s, w):
    '''
    MicroPython doesn't support zfill, rjust, ljust of str object.
    '''
    return __rjust(s, w, c="0")

def int_to(n, nbytes=None, ljust=False):
    '''
    convert the integer into bytearray().
    '''
    return bit_to(bin(n)[2:], nbytes, ljust)

def bit_to(b, nbytes=None, ljust=False):
    '''
    convert the bit string into bytearray().
    if nbytes is None, b is put into the bytes as long as maximum.
    if nbytes is less than the length of b, b is truncated according to the
    boolean of ljust.
    if ljust is True, b is aligned to the left.
    '''
    if nbytes is None:
        nbytes = int(len(b)/8)+(1 if len(b)%8 else 0)
    nbits = nbytes*8
    if ljust:
        b2 = b.ljust(nbits,"0")[:nbits]
    else:
        b2 = b.rjust(nbits,"0")[-nbits:]
    return bytearray([int(b2[i:i+8],2) for i in range(0, nbits, 8)])

def hex_to(hexstr, nbytes=None, ljust=False):
    '''
    convert the hex string into bytearray().
    see bit_to()
    '''
    return bit_to(bin(int(hexstr,16))[2:], nbytes, ljust)

def to_int(ba, reverse=False):
    '''
    convert bytearray() into an integer.
    '''
    n = 0
    if reverse:
        ba = ba[::-1]
    for i in ba:
        n = (n<<8) + i
    return n

def to_bit(ba):
    '''
    convert bytearray() into a continuous bit string without leading "0b".
    '''
    return [__zfill(bin(i)[2:],8) for i in ba]

def to_hex(ba):
    '''
    convert bytearray() into a hex string.
    '''
    return ["%02x"%i for i in ba]

