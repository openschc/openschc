#---------------------------------------------------------------------------

from base_import import *

class Compression:
    def __init__(self, protocol):
        self.protocol = protocol

    def compress(self, context, packet_bbuf):
        # XXX do more work
        assert isinstance(packet_bbuf, BitBuffer)
        meta_info = {}
        result = BitBuffer()
        rule = context["comp"]
        if rule["ruleID"] is not None and rule["ruleLength"] is not None:
            result.add_bits(rule["ruleID"], rule["ruleLength"])
        result += packet_bbuf
        self.protocol.log("compress", "{}=>{},{}".format(
            packet_bbuf, result, meta_info))
        return result, meta_info

    def decompress(self, context, packet_bbuf):
        # XXX do more work
        assert isinstance(packet_bbuf, BitBuffer)
        meta_info = {}
        result = packet_bbuf.copy()
        rule = context["comp"]
        self.protocol.log("decompress", "{}=>{},{}".format(
            packet_bbuf, result, meta_info))
        return result, meta_info

#---------------------------------------------------------------------------
