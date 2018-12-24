#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg
from schcbitmap import find_missing_tiles, sort_tile_list
from schctest import mic_crc32

#---------------------------------------------------------------------------

class ReassembleBase:

    def __init__(self, protocol, context, rule, dtag, sender_L2addr):
        self.protocol = protocol
        self.context = context
        self.rule = rule
        self.dtag = dtag
        self.sender_L2addr = sender_L2addr
        self.tile_list = []
        self.mic_received = None

    def get_mic(self, mic_target, extra_bits=0):
        assert isinstance(mic_target, bytearray)
        mic = mic_crc32.get_mic(mic_target)
        print("Recv MIC {}, base = {}".format(mic, mic_target))
        return mic.to_bytes(4, "big")

    def cancel_timer(self):
        # XXX cancel timer registered.
        pass

#---------------------------------------------------------------------------

class ReassemblerNoAck(ReassembleBase):

    def receive_frag(self, bbuf, dtag):
        # XXX context should be passed from the lower layer.
        # XXX and pass the context to the parser.
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        print("receiver frag received:", schc_frag.__dict__)
        assert schc_frag.fcn is not None
        self.tile_list.append(schc_frag.payload)
        fcn_all_1 = schcmsg.get_fcn_all_1(self.rule)
        if schc_frag.fcn == fcn_all_1:
            print("ALL1 received")
            # MIC calculation
            schc_packet = BitBuffer()
            for i in self.tile_list:
                schc_packet += i
            mic_calced = self.get_mic(schc_packet.get_content())
            if schc_frag.mic != mic_calced:
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag.mic, mic_calced))
                return
            # decompression
            self.protocol.process_decompress(self.context, self.sender_L2addr,
                                             schc_packet)
            return
        print("---", schc_frag.fcn)

#---------------------------------------------------------------------------

class ReassemblerAckOnError(ReassembleBase):

    # In ACK-on-Error, a fragment contains tiles belonging to different window.
    # A type of data structure holding tiles in each window is not suitable.  
    # So, here just appends a fragment into the tile_list like No-ACK.
    def receive_frag(self, bbuf, dtag):
        schc_frag = schcmsg.frag_receiver_rx(self.rule, bbuf)
        print("receiver frag received:", schc_frag.__dict__)
        assert schc_frag.fcn is not None
        # append the payload to the tile list.
        # padding truncation is done later. see below.
        nb_tiles = schc_frag.payload.count_added_bits()//self.rule["tileSize"]
        # Note that nb_tiles is the number of tiles which is exact number of the
        # size of the tile.  the tile of which the size is less than the size
        # is not included.
        self.tile_list.append({
                "w-num": schc_frag.win,
                "t-num": schc_frag.fcn,
                "nb_tiles": nb_tiles,
                "raw_tiles":schc_frag.payload})
        self.tile_list = sort_tile_list(self.tile_list, self.rule["FCNSize"])
        if self.mic_received is not None:
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            if self.mic_received == mic_calced:
                self.finish(schc_packet, schc_frag)
            else:
                # XXX waiting for the fragments requested by ACK.
                # during MAX_ACK_REQUESTS
                print("waiting for more fragments.")
        elif schc_frag.fcn == schcmsg.get_fcn_all_1(self.rule):
            print("ALL1 received")
            self.mic_received = schc_frag.mic
            schc_packet, mic_calced = self.get_mic_from_tiles_received()
            if schc_frag.mic == mic_calced:
                self.finish(schc_packet, schc_frag)
            else:
                print("ERROR: MIC mismatched. packet {} != result {}".format(
                        schc_frag.mic, mic_calced))
                bit_list = find_missing_tiles(self.tile_list,
                                              self.rule["FCNSize"],
                                              schcmsg.get_fcn_all_1(self.rule))
                assert bit_list is not None
                for bl_index in range(len(bit_list)):
                    print("missing wn={} bitmap={}".format(bit_list[bl_index][0],
                                                           bit_list[bl_index][1]))
                    # XXX compress bitmap if needed.
                    # ACK failure message
                    schc_ack = schcmsg.frag_receiver_tx_all1_ack(
                            schc_frag.rule,
                            schc_frag.dtag,
                            win=bit_list[bl_index][0],
                            cbit=0,
                            bitmap=bit_list[bl_index][1])
                    print("ACK failure message:", schc_ack.__dict__)
                    src_dev_id = self.protocol.layer2.mac_id
                    args = (schc_ack.packet.get_content(), src_dev_id,
                            None, None)
                    self.protocol.scheduler.add_event(
                            0, self.protocol.layer2.send_packet, args)
                    # XXX need to keep the ack message for the ack request.
                return
        print("---", schc_frag.fcn)

    def finish(self, schc_packet, schc_frag):
        # decompression
        self.protocol.process_decompress(self.context, self.sender_L2addr,
                                         schc_packet)
        # ACK message
        schc_ack = schcmsg.frag_receiver_tx_all1_ack(
                schc_frag.rule,
                schc_frag.dtag,
                schc_frag.win,
                cbit=1)
        print("ACK sent:", schc_ack.__dict__)
        src_dev_id = self.protocol.layer2.mac_id
        args = (schc_ack.packet.get_content(), src_dev_id, None, None)
        self.protocol.scheduler.add_event(0,
                                            self.protocol.layer2.send_packet,
                                            args)
        # XXX need to keep the ack message for the ack request.

    def get_mic_from_tiles_received(self):
        # MIC calculation.
        # The truncation of the padding should be done here
        # because the padding of the last tile must be included into the
        # MIC calculation.  However, the fact that the last tile is
        # received can be known after the All-1 fragment is received.
        schc_packet = BitBuffer()
        for i in self.tile_list[:-2]:
            # it needs to copy the buffer as it will be reused later.
            tiles = i["raw_tiles"].copy().get_bits_as_buffer(
                i["nb_tiles"]*self.rule["tileSize"])
            schc_packet += tiles
        # check the size of the padding in the All-1 fragment.
        if (self.tile_list[-1]["raw_tiles"].count_added_bits() <
            self.rule["L2WordSize"]):
            # the last tile exists in the fragment before the All-1
            # fragment and the payload has to add as it is.
            # the All-1 fragment doesn't need to taken into account
            # of the MIC calculation.
            schc_packet += self.tile_list[-2]["raw_tiles"]
        else:
            # the last tile exists in the All-1 fragment.
            # it needs to truncate the padding in the fragment before that.
            i = self.tile_list[-2]
            schc_packet += i["raw_tiles"].get_bits_as_buffer(
                i["nb_tiles"]*self.rule["tileSize"])
            schc_packet += self.tile_list[-1]["raw_tiles"]
        # get the target of MIC from the BitBuffer.
        print("MIC calculation:")
        for _ in self.tile_list:
            print(_)
        mic_calced = self.get_mic(schc_packet.get_content())
        return schc_packet, mic_calced

#---------------------------------------------------------------------------
