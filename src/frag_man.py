import sys
from base_import import *

from schctest import pybinutil as bu # XXX

'''
Hackathon13:
    https://github.com/openschc/doc/wiki/IETF-103-Hackathon-LPWAN

ruleID : 6 bits
DTAG: 2 bits
Window: 5 bits
FCN: 3 bits
the above parameters allow having a header aligned on byte boundaries
MAX_WIND_FCN: 6
tile size: 30 bytes
The MIC will be the default MIC specified by the draft.

ruleid DT W     FCN
000111 01 00000 000
'''

# XXX need to be replaced.
def schc_make_packet(config, rule, dtag, tiles):
    # make a header
    rid_bit = bu.int_to_bit(rule["rule-id"], 6)
    dtag_bit = bu.int_to_bit(dtag, 2)
    win_bit = bu.int_to_bit(tiles[0]["w-num"], rule["window-size"])
    fcn_bit = bu.int_to_bit(tiles[0]["t-num"], rule["fcn-size"])
    print("DEBUG: rid:{} dtag:{} win:{} fcn:{}".format(rid_bit, dtag_bit,
                                                       win_bit, fcn_bit))
    header = int("".join([rid_bit, dtag_bit, win_bit, fcn_bit]),2).to_bytes(
            2,byteorder="big")
    # make a payload
    payload = bytearray()
    pos = 0
    for t in tiles:
        bu.bit_set(payload, pos, t["tile"], extend=True)
        pos += len(t["tile"])

    print("DEBUG:", payload)
    return header + payload

# XXX need to be replaced.
def schc_sender_parse(config, rule, payload):
    pass

class tile_list():

    def __init__(self, rule, packet):
        t_size = rule["tile-size"]
        t_init_num = pow(2,rule["fcn-size"]) - 2
        self.tile_list = []
        w_num = 0
        t_num = t_init_num
        for i in range(0, len(packet)*8, t_size):
            # XXX need to use BitBuffer
            t = bu.bit_get(packet, pos=i, val=i+t_size)
            tile_obj = {
                    "w-num": w_num,
                    "t-num": t_num,
                    "tile": t,
                    "sent": False,
                    "ready_to_be_sent": False,
                }
            self.tile_list.append(tile_obj)
            w_num = w_num + 1
            t_num = t_num - 1
            if t_num < 0:
                t_num = t_init_num
        print("DEBUG: tile_list:")
        for i in self.tile_list:
            print("DEBUG:  ", i)

    def get_tiles(self, max_tiles):
        '''
        return the tiles containing the contiguous tiles in maximum
        within max_tiles.
        '''
        tiles = []
        t_prev = None
        for i in range(len(self.tile_list)):
            t = self.tile_list[i]
            if t_prev and t_prev["t-num"] + 1 < t["t-num"]:
                break
            if t["sent"] == False:
                tiles.append(t)
                if t["ready_to_be_sent"] == True:
                    print("XXX invalid state, add it anyway.")
                t["ready_to_be_sent"] = True
                t_prev = t
        if len(tiles) == 0:
            return None
        else:
            return tiles

    def update_sent_flags(self):
        for t in self.tile_list:
            if t["ready_to_be_sent"] == True:
                t["sent"] = True

class fragment_sender():

    def __init__(self, rule, dtag, packet, peer_iid, config=None,
                 scheduler=None, layer2=None):
        self.rule = rule
        self.dtag = dtag
        self.packet = packet
        self.peer_iid = peer_iid
        self.config = config
        self.scheduler = scheduler
        self.layer2 = layer2
        self.tile_list = tile_list(self.rule, self.packet)
        self.send_frag(self.peer_iid)

    def send_frag(self, peer_iid=None):
        frag = self.get_frag()
        if frag is None:
            return  # end of sending frags.
        # XXX send_packet() might need a peer iid to send a fragment.
        # XXX self.layer2.send_packet(frag, peer_iid)
        print("S: [mac%s] -> SCHC[mac:%s] %s"
              % ("00self00", peer_iid, frag))
        self.layer2.send_packet(frag)
        self.tile_list.update_sent_flags()
        if not self.rule["ack-after-recv-all1"]:
            ev = self.scheduler.add_event(3, self.recv_ack_timeout, None)

    def recv_ack_timeout(self):
        # XXX check the retry counter.
        send_frag()

    def get_mtu_size(self):
        '''
        return current L2 mtu size in bits.
        '''
        # XXX
        return 32

    def get_header_size(self):
        '''
        return header size in bits.
        '''
        # XXX
        return 10

    def get_frag(self):
        '''
        get contiguous fragments to be sent.
        '''
        mtu_size = self.get_mtu_size()
        max_tiles = (mtu_size - self.get_header_size()) / self.rule["tile-size"]
        tiles = self.tile_list.get_tiles(max_tiles)
        if tiles is not None:
            return schc_make_packet(self.config, self.rule, self.dtag, tiles)
        else:
            return None

    def recv_ack(self, packet, peer_iid=None):
        print("recv_ack:", packet)  # XXX
        '''
        sh = schc_sender_parse(packet)
        if sh is None:
            return
        if sh.c == 0:
            self.unset_sent_flag(sh.w, sh.bitmap)
            self.send_frag()
        elif sh.c == 1:
            XXX
        else:
            XXX
        '''

class fragment_manager():

    def __init__(self, config, scheduler, layer2):
        self.config = config
        self.scheduler = scheduler
        self.layer2 = layer2
        self.session_list = []
        self.dtag = 0

    def send_packet(self, rule, packet, peer_iid):
        s = fragment_sender(rule, self.dtag, packet, peer_iid,
                    config=self.config, scheduler=self.scheduler,
                    layer2=self.layer2)
        self.session_list.append(s)
        # update dtag for next
        self.dtag += 1
        if self.dtag > pow(2,rule["dtag-size"]-1):
            self.dtag = 0

    def recv_ack(self, packet, peer_iid=None):
        s = self.find_session(peer_iid=peer_iid)
        if s is None:
            # XXX
            return
        s.recv_ack(packet)

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
                


