
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

class FragmentAckOnError():
    def __init__(self, protocol, rule, profile=None):
        self.protocol = protocol
        self.rule = rule
        self.profile = profile
        self.dtag = 0
        self.event_timeout = 5
        self.retry_counter = 0
        self.mic_sent = None
        self.padding_last_window = None

    def set_packet(self, packet):
        #self.rule_only_for_hackathon103 = rule # XXX this must be removed.
        self.all_tiles = TileList(self.rule, packet)
        # update dtag for next
        self.dtag += 1
        if self.dtag > pow(2,self.rule.dtag_size-1):
            self.dtag = 0

# Draft-17:
#   The bits on which the MIC is computed MUST be the SCHC Packet
#   concatenated with the padding bits that are appended to the Payload
#   of the SCHC Fragment that carries the last tile.
#
# XXX padding bits of the last fragment for MIC calculation.
# 
# MTU = 56 bits
# Header size = 11 bits
# The SCHC packet size = 9 bytes (72 bits).
# The tile size = 30 bits.
# The last tile size = 12 bits
# MIC size = 32 bits
# 
#             1         2         3        4        5        6        7
#      01234567 012 34567 0123456 7 01234567 01234567 01234567 01234567
#     +--------+--- -----+------- -+--------+--------+--------+--------+
#     |   Header   |     Tile    |       Remaining space               |
#     +--------+--- -----+------- -+--------+--------+--------+--------+
#     |  11 bits   |    12 bits  |             33 bits                 |
# 
# There is enough space to put MIC.
# How to calculate MIC and where is the MIC put in the remaining space ?
# 
# When the Receiver receives the SCHC fragment, how to know where MIC is ?
# The receiver can not know the size of the last tile.
# 
#             1         2         3        4        5        6         7
#      01234567 012 34567 0123456 7 01234567 01234567 01234567 0123456 7
#     +--------+--- -----+------- -+--------+--------+--------+------- -+
#     |   Header   |     Tile    |                 MIC                |0|
#     +--------+--- -----+------- -+--------+--------+--------+------- -+
#     |  11 bits   |    12 bits  |             33 bits                  |
# 
    def get_mic(self):
        # XXX need to get the CORRECT padding size. see comment above.
        mic_target = TileList.get_bytearray(self.all_tiles.get_all_tiles())
        mic = mic_crc32.get_mic(mic_target)
        return mic.to_bytes(4, "big")

    def send_frag(self):
        # get contiguous tiles as many as possible fit in MTU.
        mtu_size = self.protocol.layer2.get_mtu_size()
        window_tiles, nb_remaining_tiles = self.all_tiles.get_tiles(mtu_size)
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
            remaining_space = mtu_size - len(window_tiles) * self.rule.tile_size
            if (nb_remaining_tiles == 0 and
                remaining_space >= schcmsg.get_mic_size_in_bits(self.rule)):
                # make All-1 frag.
                self.mic_sent = self.get_mic()
                fcn = schcmsg.get_fcn_all_1(self.rule)
            else:
                # regular frag.
                fcn = window_tiles[0]["t-num"]
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, rule_id=self.rule.rule_id, dtag=self.dtag,
                    win=window_tiles[0]["w-num"],
                    fcn=fcn,
                    mic=self.mic_sent,
                    payload=TileList.get_bytearray(window_tiles))
            # save the last window tiles.
            self.last_window_tiles = window_tiles
        else:
            # all tiles has been sent.
            if self.mic_sent is not None:
                # MIC has been sent already.
                # XXX need to wait for the ACK at least.  here ?
                return
            # make All-1 frag.
            self.mic_sent = self.get_mic()
            win = 0 # in case when there is no SCHC packet.
            if self.last_window_tiles is not None:
                win = self.last_window_tiles[0]["w-num"]
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, rule_id=self.rule.rule_id, dtag=self.dtag,
                    win=win,
                    fcn=schcmsg.get_fcn_all_1(self.rule),
                    mic=self.mic_sent)
        # send
        src_dev_id = self.protocol.layer2.mac_id
        args = (schc_frag.packet.get_content(), src_dev_id, None,
                self.event_sent_frag)
        print("DEBUG: send_frag:", schc_frag.packet.get_content())
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args)

    def start_sending(self):
        self.send_frag()

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

# temporary class before merging after hackathon
class SCHCProtocolSender(schc.SCHCProtocol):
    '''
    assuming that there is only one session to be handled.
    '''
    def __init__(self, *args, **kwargs):
        schc.SCHCProtocol.__init__(self, *args, **kwargs)
        self.session = FragmentAckOnError(self, None) # XXX:hack

    def set_frag_rule(self, rule): #XXX: hack
        schc.SCHCProtocol.set_frag_rule(self, rule)
        self.session.rule = rule

    def send_packet(self, packet, peer_iid=None):
        # Should do:
        # - compression
        # - fragmentation
        # (and sending packets)
        #compression_rule = XXX
        #self.compression_manager.compress(compression_rule)
        packet = packet[:]  # Null compression

        # XXX:TODO select the rule
        self.session.set_packet(packet)
        self.scheduler.add_event(0, self.session.start_sending, tuple())
        '''
        if not self.rule["ack-after-recv-all1"]:
            self.event_timeout = self.scheduler.add_event(
                    3, self.recv_ack_timeout, None)
        '''

    '''
    def recv_ack_timeout(self):
        # XXX check the retry counter.
        if self.retry_coounter > self.rule["retry-counter"]:
            print("DEBUG: stop sending due to limit the retry counter.")
            # XXX send_sender_abort()
            return
        self.send_frag(self.peer_iid)
    '''

    def event_receive_packet(self, peer_id, raw_packet):
        '''
        if self.session.is_ack_timeout():
            print("DEBUG: ack timeout. XXX send sender-abort.")
            return
        '''
        print("DEBUG: S<R: [mac%s] -> SCHC[mac:%s] %s"
              % (self.layer2.iid, peer_id, packet))
        self.session.process_packet(raw_packet)
        self.session.recv_ack(packet, peer_iid=self.layer2.iid)

#---------------------------------------------------------------------------
