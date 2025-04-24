"""
.. module: gen_base_import
   :platform: Micropython/Python
   :synopsis: Common import file providing differentiation between python and micropython

"""
# Import all external modules with proper try/except in order to allow
# for code running on both Micropython and Python
# Import some internal modules (fake/temporary versions)

import sys

if sys.implementation.name == "micropython":
    import utime as time
    import ujson as json
    from ucollections import namedtuple
    import urandom
    import ustruct as struct
    import usocket as socket
else:
    import time
    import json
    from collections import namedtuple
    import random as random
    import struct
    import socket

# --- sched
#sys.path.append("../../micropython-lib/heapq") # XXX (for pyssched)
#sys.path.append("../../micropython-lib/ffilib") # XXX (for time)
#sys.path.append("../../micropython-lib/time") # XXX (for pyssched)

###sys.path.append("../../micropython-lib/sched") # XXX
###import sched # empty...
#sys.path.append("schctest/pyssched")
#import pyssched as sched

# --- default imports

from gen_bitarray import BitBuffer
from frag_rcs_crc32 import get_mic, get_mic_size

def b2hex(b):
    """This function replace the bytes.hex() function provided in Python3.5 and later

    .. note::

       Micropython (Python 3.4) doesn't support bytes.hex().

    Args:
       b (bytes): the byte chain to convert to hexadecimal representation

    Returns:
       str : The string representation of the converted hex

    Example:
    
    >>> print b2hex(b'123')
    '313233'
    """
    return "".join(["%02x"%_ for _ in b])
