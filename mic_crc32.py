"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import zlib
"""
def get_mic(data):
    '''
    data: a bytes-like object.
    return
        an integer of the mic, which is decoded into 32 bits.
        size of the mic, i.e. 32
    '''
    #return zlib.crc32(data), 32
    return 0xDEADBEEF, 32
