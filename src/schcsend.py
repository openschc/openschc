#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg
from schctile import TileList
from schctest import mic_crc32

#---------------------------------------------------------------------------
# XXX: put rule_manager

Rule = namedtuple("Rule", "rule_id_size dtag_size window_size"
                  + " fcn_size mode tile_size mic_algorithm")

def rule_from_dict(rule_as_dict):
    rule_as_dict = { k.replace("-","_"): v for k,v in rule_as_dict.items() }
    return Rule(**rule_as_dict)

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

    def get_mic(self, extra_bits=0):
        mic_target = self.packet + (b"\x00" * (roundup(extra_bits,
                            self.rule.mic_word_size)//self.rule.mic_word_size))
        mic = mic_crc32.get_mic(mic_target)
        return mic.to_bytes(4, "big")

    def start_sending(self):
        self.send_frag()

    def send_frag(self):
        raise NotImplementedError("it is implemented at the subclass.")

class FragmentNoAck(FragmentBase):

    def set_packet(self, packet):
        self.packet = packet[:]
        self.packet_bb = BitBuffer(packet)
        # update dtag for next
        self.dtag += 1
        if self.dtag > pow(2,self.rule.dtag_size-1):
            self.dtag = 0

    def send_frag(self):
        # get contiguous tiles as many as possible fit in MTU.
        remaining_size = (self.protocol.layer2.get_mtu_size() -
                          schcmsg.get_header_size(self.rule))
        if self.packet_bb.count_remaining_bits() != 0:
            # regular frag.
            if remaining_size > self.packet_bb.count_remaining_bits():
                # put all remaining bits into the tile.
                tile = self.packet_bb.get_bits_as_buffer(
                        self.packet_bb.count_remaining_bits())
            else:
                # put remaining_size of bits of packet into the tile.
                tile = self.packet_bb.get_bits_as_buffer(remaining_size)
            fcn = 0
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, rule_id=self.rule.rule_id, dtag=self.dtag,
                    win=None,
                    fcn=fcn,
                    mic=None,
                    payload=tile.get_content())
            # save the last window tiles.
            self.last_tile = tile
            transmit_callback = self.event_sent_frag
        else:
            # make All-1 frag.
            assert self.last_tile is not None
            assert self.mic_sent is None
            last_payload_size = (schcmsg.get_header_size(self.rule) +
                                 self.last_tile.count_added_bits())
            # calculate extra_bits (= packet_size - last_payload_size)
            self.mic_sent = self.get_mic(extra_bits=(
                    roundup(last_payload_size, self.rule.l2_word_size) -
                    last_payload_size))
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, rule_id=self.rule.rule_id, dtag=self.dtag,
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

    def set_packet(self, packet):
        #self.rule_only_for_hackathon103 = rule # XXX this must be removed.
        self.packet = packet[:]
        self.all_tiles = TileList(self.rule, self.packet)
        # update dtag for next
        self.dtag += 1
        if self.dtag > pow(2,self.rule.dtag_size-1):
            self.dtag = 0

    def send_frag(self):
        # get contiguous tiles as many as possible fit in MTU.
        mtu_size = self.protocol.layer2.get_mtu_size()
        window_tiles, nb_remaining_tiles, remaining_size = self.all_tiles.get_tiles(mtu_size)
# XXX
# what is the window number for the ALL-1 MIC ?
#
# e.g. N = 2 bits.
# ## 6 tiles. 3 tiles in each fragment.
#
# Window #|  0  |  1  |
#   Tile #|2|1|0|2|1|0|
#         |-----|-----|-----|
#   Frag# |  1  |  2  |  3  |
#  Window |  0  |  1  | 1?? |
#     FCN |  2  |  2  |ALL-1|
# Payload |2 1 0|2 1 0| MIC |
#
# ## 5 tiles. 3 tiles in 1st frag., 2 tiles in 2nd frag.
#
# Window# |  0  | 1 |
#   Tile# |2|1|0|2|1|
#         |-----|---|-------|
#   Frag# |  1  | 2 |   3   |
#       W | 0   | 1 |  1??? |
#     FCN |2    |2  | ALL-1 |
# Payload |2 1 0|2 1|  MIC  |
#
# ## 5 tiles. 2 tiles in 1st/2nd frag., MIC and the last tile in 3rd frag.
#
# Window# |  0  | 1 |       |
#   Tile# |2|1|0|2|1|       |
#         |---|---|---------|
#   Frag# | 1 | 2 |    3    |
#       W | 0 | 0 |   1???  |
#     FCN |2  |0  |  ALL-1  |
# Payload |2 1|0 2|1  MIC   |
        if window_tiles is not None:
            assert self.mic_sent is None
            fcn = window_tiles[0]["t-num"]
            if nb_remaining_tiles > 0:
                # regular frag.
                # MIC will be sent in next.
                pass
            else:
                if remaining_size >= schcmsg.get_mic_size_in_bits(self.rule):
                    # make All-1 frag with the tiles.
                    last_payload_size = (schcmsg.get_header_size(self.rule) +
                                        schcmsg.get_mic_size_in_bits(self.rule) +
                                        TileList.get_tile_size(window_tiles))
                    # calculate extra_bits (= packet_size - last_payload_size)
                    self.mic_sent = self.get_mic(extra_bits=(
                            roundup(last_payload_size, self.rule.l2_word_size) -
                            last_payload_size))
                    fcn = schcmsg.get_fcn_all_1(self.rule)
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, rule_id=self.rule.rule_id, dtag=self.dtag,
                    win=window_tiles[0]["w-num"],
                    fcn=fcn,
                    mic=self.mic_sent,
                    payload=TileList.get_bytearray(window_tiles))
            # save the last window tiles.
            self.last_window_tiles = window_tiles
        else:
            # only MIC will be sent since all tiles has been sent.
            assert self.last_window_tiles is not None
            if self.mic_sent is not None:
                # MIC has been sent already.
                # XXX need to wait for the ACK at least.  here ?
                return
            # make All-1 frag.
            win = 0 # in case when there is no SCHC packet.
            win = self.last_window_tiles[0]["w-num"]
            last_payload_size = (schcmsg.get_header_size(self.rule) +
                                 TileList.get_tile_size(self.last_window_tiles))
            # calculate extra_bits (= packet_size - last_payload_size)
            self.mic_sent = self.get_mic(extra_bits=(
                    roundup(last_payload_size, self.rule.l2_word_size) -
                    last_payload_size))
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, rule_id=self.rule.rule_id, dtag=self.dtag,
                    win=win,
                    fcn=schcmsg.get_fcn_all_1(self.rule),
                    mic=self.mic_sent)
        # send
        src_dev_id = self.protocol.layer2.mac_id
        args = (schc_frag.packet.get_content(), src_dev_id, None,
                self.event_sent_frag)
        print("DEBUG: send_frag:", schc_frag.packet)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args)

    def event_sent_frag(self, status): # status == nb actually sent (for now)
        self.update_frags_sent_flag()
        self.send_frag()

    def update_frags_sent_flag(self):
        self.all_tiles.update_sent_flag()

    def recv_ack(self, packet, peer_iid=None):
        print("DEBUG: recv_ack:", packet)  # XXX
        message = schcmsg.frag_sender_rx(packet, self.rule, self.dtag)

        print("parsed message:", message.__dict__, message.payload.__dict__)

        if message.cbit == 0:
            self.all_tiles.unset_sent_flag(message.win, message.bitmap)
            self.send_frag()
        elif message.cbit == 1:
            #XXX
            pass
        else:
            #XXX
            pass

    def recv_frag(self, packet, peer_iid=None):
        s = self.find_session(peer_iid=peer_iid)
        if s is None:
            # add it as a new session.
            # XXX rule = rulemanager.find_rule(...)
            rule = self.rule_only_for_hackathon103
            s = fragment_receiver(packet, peer_iid=peer_iid,
                                  config=self.config, rule=rule,
                                  scheduler=self.scheduler,
                                  layer2=self.layer2)
            return
        s.recv_frag(packet)

    def find_session(self, peer_iid=None):
        if peer_iid:
            for i in self.session_list:
                if i.peer_iid == peer_iid:
                    return i
            else:
                return None
        else:
            # XXX
            return None

#---------------------------------------------------------------------------
