'''
to_foo() measns that a bytearray is converted into a foo.
e.g. to_bitstring() means that a bytearray is converted into a bitstring.
foo_to() meaans that a foo is converted into a bytearray.
'''

def __zfill(s, w):
    '''
    MicroPython doesn't support zfill.
    '''
    return "".join(["0" for i in range(w-len(s))]) + s

def int_to(n, nbytes=None, bigendian=True):
    '''
    convert the integer into bytearray().
    e.g. if n in hex is "123",
    if nbytes is 3 and endian is "big", then it's gonna be "000123".
    if endian is not "big", then it's gonna be "230100".
    '''
    h = "%x" % n
    if nbytes != None:
        h = __zfill(h, 2*nbytes)
    x = [int(h[i:i+2],16) for i in range(0, len(h), 2)]
    return bytearray(x) if bigendian else bytearray(x[::-1])

def bit_to(b, nbytes, bigendian=True):
    '''
    convert the bit string into bytearray().
    '''
    return int_to(int(b,2), nbytes, bigendian=bigendian)

def hex_to(hexstr, nbytes=None, bigendian=True):
    '''
    convert the hex string into bytearray().
    '''
    if nbytes == None:
        nbytes = int(len(hexstr)/2) + (1 if len(hexstr)%2 else 0)
    return int_to(int(hexstr,16), nbytes, bigendian)

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

