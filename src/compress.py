#---------------------------------------------------------------------------

from base_import import *

class Compression:
    def __init__(self, protocol):
        self.protocol = protocol

    def compress(self, packet):
        # XXX do more work
        meta_info = {}
        result = BitBuffer(packet)
        self.protocol.log("compress", "{}=>{},{}".format(
            repr(packet), result, meta_info))
        return BitBuffer(packet), meta_info

    def decompress(self, packet_bbuf):
        # XXX do more work
        meta_info = {}
        result = bbuf[:]
        self.protocol.log("decompress", "{}=>{},{}".format(
            repr(packet), result, meta_info))
        return BitBuffer(packet), meta_info

#---------------------------------------------------------------------------
