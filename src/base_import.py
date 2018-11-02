# Import all external modules, with proper try/except in order to allow
# for code running on both Micropython and Python

try:
    import time
except ImportError:
    import utime as time

from bitarray import FakeBitBuffer as BitBuffer
