#---------------------------------------------------------------------------

from base_import import *

class Compression:
    def __init__(self, protocol):
        self.protocol = protocol

    def compress(self, packet_bbuf):
        # XXX do more work
        assert isinstance(packet_bbuf, BitBuffer)
        meta_info = {}
        result = packet_bbuf.copy()
        self.protocol.log("compress", "{}=>{},{}".format(
            packet_bbuf, result, meta_info))
        return result, meta_info

    def decompress(self, packet_bbuf):
        # XXX do more work
        assert isinstance(packet_bbuf, BitBuffer)
        meta_info = {}
        result = packet_bbuf.copy()
        self.protocol.log("decompress", "{}=>{},{}".format(
            packet_bbuf, result, meta_info))
        return result, meta_info

#---------------------------------------------------------------------------
