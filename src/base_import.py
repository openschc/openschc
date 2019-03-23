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

from bitarray import BitBuffer
from mic_crc32 import get_mic, get_mic_size

def b2hex(b):
    """
    As Micropython (Python 3.4) doesn't support bytes.hex().
    """
    return "".join(["%02x"%_ for _ in b])
