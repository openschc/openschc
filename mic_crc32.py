#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

if "implementation" in dir(sys) and sys.implementation.name == "micropython":
    from ubinascii import crc32
    def get_mic(data):
        return crc32(data), 32
else:
    from binascii import crc32
    def get_mic(data):
        '''
        data: a bytes-like object.
        return
            an integer of the mic, which is decoded into 32 bits.
            size of the mic, i.e. 32
        '''
        return crc32(data), 32

