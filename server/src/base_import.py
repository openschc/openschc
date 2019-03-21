# Import all external modules with proper try/except in order to allow
# for code running on both Micropython and Python
# Import some internal modules (fake/temporary versions)

import sys

try:
    import time
except ImportError:
    import utime as time

try:
    import json
except:
    import ujson as json

try:
    from collections import namedtuple
except ImportError:
    from ucollections import namedtuple

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
