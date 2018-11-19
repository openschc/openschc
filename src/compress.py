#---------------------------------------------------------------------------

from base_import import *

class Compression:
    def __init__(self, protocol):
        self.protocol = protocol

    def compress(self, packet):
        meta_info = {}
        result = BitBuffer(packet)
        self.protocol.log("compress", "{}=>{},{}".format(
            repr(packet), result, meta_info))
        return BitBuffer(packet), meta_info

#---------------------------------------------------------------------------
