import sys

CRC32_MIC_SIZE = 32

if "implementation" in dir(sys) and sys.implementation.name == "micropython":
    from ubinascii import crc32
    def get_mic(data, crc0=0):
        return crc32(data, crc0)
else:
    from binascii import crc32
    def get_mic(data, crc0=0):
        '''
        data: a bytes-like object.
        return
            an integer of the mic, which is decoded into 32 bits.
            size of the mic, i.e. 32
        '''
        return crc32(data, crc0)

def get_mic_size():
    return CRC32_MIC_SIZE
