"""
.. module::frag_rcs_crc32 
   :platform: Python, Micropython

"""
try:
    from binascii import crc32
except ImportError:
    from ubinascii import crc32

def get_mic(data, crc0=0):
    """ return the mic encoded into 32 bits. """
    return crc32(data, crc0)

def get_mic_size():
    return 32


