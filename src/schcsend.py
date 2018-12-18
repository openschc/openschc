#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg
from schctile import TileList
from schcbitmap import make_bit_list
from schctest import mic_crc32

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

# XXX should move it to bitarray or schcmsg.
def roundup(v, w=8):
    a, b = (v//w, v%w)
    return a*w+(w if b else 0)

#---------------------------------------------------------------------------

class FragmentBase():
    def __init__(self, protocol, rule, profile=None):
        self.protocol = protocol
        self.rule = rule
        self.profile = profile
        self.dtag = 0
        self.event_timeout = 5
        self.retry_counter = 0
        self.mic_sent = None
        self.event_id_ack_waiting = None

    def set_packet(self, packet_bbuf):
        """ store the packet of bitbuffer for later use,
        return dtag for the packet """
        self.packet_bbuf = packet_bbuf.copy()
        self.mic_base = packet_bbuf.get_content()[:]
        # update dtag for next
        self.dtag += 1
        if self.dtag > schcmsg.get_max_dtag(self.rule):
            self.dtag = 0

    def get_mic(self, extra_bits=1):
        mic_target = self.mic_base
        mic_target += b"\x00" * (roundup(
                extra_bits, self.rule["MICWordSize"])//self.rule["MICWordSize"])
        mic = mic_crc32.get_mic(mic_target)
        print("Send MIC {}, base = {}".format(mic, mic_target))
        return mic.to_bytes(4, "big")

    def start_sending(self):
        self.send_frag()

    def cancel_timer(self):
        # XXX cancel timer registered.
        pass

    def send_frag(self):
        raise NotImplementedError("it is implemented at the subclass.")

class FragmentNoAck(FragmentBase):

    def send_frag(self):
        # get contiguous tiles as many as possible fit in MTU.
        remaining_size = (self.protocol.layer2.get_mtu_size() -
                          schcmsg.get_sender_header_size(self.rule))
        if self.packet_bbuf.count_remaining_bits() != 0:
            # regular frag.
            if remaining_size > self.packet_bbuf.count_remaining_bits():
                # put all remaining bits into the tile.
                tile = self.packet_bbuf.get_bits_as_buffer(
                        self.packet_bbuf.count_remaining_bits())
            else:
                # put remaining_size of bits of packet into the tile.
                tile = self.packet_bbuf.get_bits_as_buffer(remaining_size)
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, dtag=self.dtag,
                    win=None,
                    fcn=0,
                    mic=None,
                    payload=tile)
            # save the last window tiles.
            self.last_tile = tile
            transmit_callback = self.event_sent_frag
        else:
            # make All-1 frag.
            assert self.last_tile is not None
            assert self.mic_sent is None
            last_payload_size = (schcmsg.get_sender_header_size(self.rule) +
                                 self.last_tile.count_added_bits())
            # calculate extra_bits (= packet_size - last_payload_size)
            self.mic_sent = self.get_mic(extra_bits=(
                    roundup(last_payload_size, self.rule["L2WordSize"]) -
                    last_payload_size))
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, dtag=self.dtag,
                    win=None,
                    fcn=schcmsg.get_fcn_all_1(self.rule),
                    mic=self.mic_sent)
            transmit_callback = None
        # send
        src_dev_id = self.protocol.layer2.mac_id
        args = (schc_frag.packet.get_content(), src_dev_id, None,
                transmit_callback)
        print("DEBUG: send_frag:", schc_frag.packet)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args)

    def event_sent_frag(self, status): # status == nb actually sent (for now)
        self.send_frag()

#---------------------------------------------------------------------------

class FragmentAckOnError(FragmentBase):

    def set_packet(self, packet_bbuf):
        super().set_packet(packet_bbuf)
        self.all_tiles = TileList(self.rule, packet_bbuf)
        # XXX
        # check whether the size of the last tile is less than L2 word
        # AND the tile number is zero
        # because draft-17 doesn't specify how to handle it.
        a = self.all_tiles.get_all_tiles()
        if (a[-1]["t-num"] == 0 and
            a[-1]["tile"].count_added_bits() < self.rule["L2WordSize"]):
            raise NotImplementedError("{}".format(
                    """the size of the last tile with the tile number 0 must
                    be equal to or greater than L2 word size."""))
        # make the bitmap
        self.bit_list = make_bit_list(self.all_tiles.get_all_tiles(),
                                      self.rule["FCNSize"],
                                      schcmsg.get_fcn_all_1(self.rule))
        print("bit_list:", self.bit_list)

    def send_frag(self):
        # get contiguous tiles as many as possible fit in MTU.
        mtu_size = self.protocol.layer2.get_mtu_size()
        window_tiles, nb_remaining_tiles, remaining_size = self.all_tiles.get_tiles(mtu_size)
        if window_tiles is not None:
            # even when mic is sent, it comes here in the retransmission.
            fcn = window_tiles[0]["t-num"]
            all_1 = False
            if (nb_remaining_tiles == 0 and
                len(window_tiles) == 1 and
                remaining_size >= schcmsg.get_mic_size_in_bits(self.rule)):
                # the All-1 fragment can carry only one tile of which the size
                # is less than L2 word size.
                all_1 = True
                # make the All-1 frag with this tile.
                last_payload_size = (
                        schcmsg.get_sender_header_size(self.rule) +
                        schcmsg.get_mic_size_in_bits(self.rule) +
                        TileList.get_tile_size(window_tiles))
                # calculate the significant padding bits.
                self.mic_sent = self.get_mic(extra_bits=(
                        roundup(last_payload_size, self.rule["L2WordSize"]) -
                        last_payload_size))
                self.event_id_ack_waiting = self.protocol.scheduler.add_event(
                        10, self.ack_timeout, tuple())
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, dtag=self.dtag,
                    win=window_tiles[0]["w-num"],
                    fcn=schcmsg.get_fcn_all_1(self.rule) if all_1 else fcn,
                    mic=self.mic_sent if all_1 else None,
                    payload=TileList.concat(window_tiles))
            # save the last window tiles.
            self.last_window_tiles = window_tiles
        elif self.mic_sent is not None:
            # it looks that all fragments have been sent.
            print("xxx how should i do after all fragments have been sent ?")
            return
        else:
            # Here, only MIC will be sent since all tiles has been sent.
            assert self.last_window_tiles is not None
            # As the MTU would be changed anytime AND the size of the
            # significant padding bits would be changed, therefore the MIC
            # calculation may be needed again.
            # XXX maybe it's better to check whether the size of MTU is change
            # or not when the previous MIC was calculated..
            last_payload_size = (schcmsg.get_sender_header_size(self.rule) +
                                 TileList.get_tile_size(self.last_window_tiles))
            # calculate extra_bits (= packet_size - last_payload_size)
            self.mic_sent = self.get_mic(extra_bits=(
                    roundup(last_payload_size, self.rule["L2WordSize"]) -
                    last_payload_size))
            # check the win number.
            # if the last tile number is zero, here window number has to be
            # incremented.
            win = self.last_window_tiles[0]["w-num"]
            if self.last_window_tiles[0]["t-num"] == 0:
                win += 1
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, dtag=self.dtag,
                    win=win,
                    fcn=schcmsg.get_fcn_all_1(self.rule),
                    mic=self.mic_sent)
            self.event_id_ack_waiting = self.protocol.scheduler.add_event(
                    10, self.ack_timeout, tuple())

        # send
        src_dev_id = self.protocol.layer2.mac_id
        args = (schc_frag.packet.get_content(), src_dev_id, None,
                self.event_sent_frag)
        print("frag sent:", schc_frag.__dict__)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args)

    def cancel_ack_timeout(self):
        if self.event_id_ack_waiting is None:
            print("WARNING: event_id_ack_waiting is not set.")
        self.protocol.scheduler.cancel_event(self.event_id_ack_waiting)

    def ack_timeout(self):
        print("ACK timeout")
        print("retransmit or remove the session ?")

    def event_sent_frag(self, status): # status == nb actually sent (for now)
        self.send_frag()

    def receive_frag(self, bbuf, dtag):
        # the ack timer can be cancelled here, because it's been done whether
        # both rule_id and dtag in the fragment are matched to this session
        # at process_received_packet().
        self.cancel_ack_timeout()
        #
        schc_frag = schcmsg.frag_sender_rx(self.rule, bbuf)
        print("sender_rx", schc_frag.__dict__)
        if (schc_frag.win == schcmsg.get_win_all_1(self.rule) and
            schc_frag.cbit == 1 and
            schc_frag.payload.allones() == True):
            print("Receiver Abort rid={} dtag={}".format(
                    self.rule.ruleID, self.dtag))
            return
        if schc_frag.cbit == 1:
            print("ACK Success rid={} dtag={}".format(
                    self.rule.ruleID, self.dtag))
            return
        if schc_frag.cbit == 0:
            print("ACK Failure rid={} dtag={}".format(
                    self.rule.ruleID, self.dtag))
            self.resend_frag(schc_frag)
            return

    def resend_frag(self, schc_frag):
        print("recv bitmap:", (schc_frag.win, schc_frag.bitmap.to_bit_list()))
        print("sent bitmap:", (schc_frag.win, self.bit_list[schc_frag.win]))
        self.all_tiles.unset_sent_flag(schc_frag.win,
                                       schc_frag.bitmap.to_bit_list())
        self.send_frag()

