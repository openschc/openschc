
# XXX: copied from byteutils, because no ljust
def my_ljust(b, s, c):
    if len(b) >= s:
        return b
    else:
        return b + (len(b)-s) * c

def my_bit_to(b, nbytes=None, ljust=False):
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
        #b2 = b.ljust(nbits,"0")[:nbits]
        b2 = my_ljust(b, nbits, "0")[:nbits]
    else:
        #b2 = b.rjust(nbits,"0")[-nbits:]
        b2 = my_ljust(b, nbits, "0")[-nbits:]        
    return bytearray([int(b2[i:i+8],2) for i in range(0, nbits, 8)])

