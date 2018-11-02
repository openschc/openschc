pybitutil
=========

simple bit manipulation utilities in python.

## USAGE

To use this package, you have to import it.

    >>> import pybinutil

or

    >>> from pybinutil import bitutil
    >>> from pybinutil import byteutil

See test-pybinutil.py for detail.

## pybinutil.bitutil

Ask help(bitutil) for detail.

    bit_count(n, bit_len, zero=False)
        count the number of bits in the bit string.
    
    bit_find(n, bit_len, val=None)
        find a bit or a set of bits from the most left.
    
    bit_get(ba, pos, val=None, integer=False)
        get a bit at the position in the bytearray.
    
    bit_set(ba, pos, val=None)
        set a bit or a set of bits at the position in the bytearray.
    
    int_to_bit(n, nbits, lsb0=True)
        convert the integer into a bit string of the number of bits specified.
    
    rzfill(s, w)
        same to rzfill().
    
    zfill(s, w)
        same to zfill().

## pybinutil.byteutil

Ask help(byteutil) for detail.

    bit_to(b, nbytes, bigendian=True)
        convert the bit string into bytearray().
    
    hex_to(hexstr, nbytes=None, bigendian=True)
        convert the hex string into bytearray().
    
    int_to(n, nbytes=None, bigendian=True)
        convert the integer into bytearray().
    
    to_bit(ba)
        convert bytearray() into a continuous bit string without leading "0b".
    
    to_hex(ba)
        convert bytearray() into a hex string.
    
    to_int(ba, reverse=False)
        convert bytearray() into an integer.


