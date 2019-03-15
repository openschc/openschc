#---------------------------------------------------------------------------

from base_import import *

import schcmsg

#---------------------------------------------------------------------------

class TileList():

    # XXX it is almost about the sender side, should be moved into schcsend.py.
    # XXX may it be used in NO-ACK ?
    def __init__(self, rule, packet_bbuf):
        self.rule = rule
        #print('TileList()  Rule: ', rule)
        frag = rule["fragmentation"]
        ModProfil = frag["FRModeProfile"]
        tileSize =  ModProfil["tileSize"]
        #print('tile size = ', tileSize)
        self.t_size = tileSize
        self.max_fcn = schcmsg.get_max_fcn(rule)
        self.all_tiles = []
        w_num = 0
        t_num = self.max_fcn
        # make tiles
        # XXX for now, the packet bitbuffer is going to be divided
        # into the tiles, which are a set of bit buffers too.
        # logically, it doesn't need when tileSize is well utilized.
        bbuf = packet_bbuf.copy()
        nb_full_size_tiles, last_tile_size = (
                bbuf.count_added_bits() // self.t_size,
                bbuf.count_added_bits() % self.t_size)
        assert last_tile_size >= 0
        tiles = [ bbuf.get_bits_as_buffer(self.t_size)
                 for _ in range(nb_full_size_tiles) ]
        if last_tile_size > 0:
            tiles.append(bbuf.get_bits_as_buffer(last_tile_size))
        # make a all_tiles
        for t in tiles:
            #print('w_num:', w_num,'  t_num:', t_num )
            tile_obj = {
                    "w-num": w_num,
                    "t-num": t_num,
                    "tile": t,
                    "sent": False,
                }
            self.all_tiles.append(tile_obj)
            if t_num == 0:
                t_num = self.max_fcn
                w_num += 1
            else:
                t_num -= 1
        if schcmsg.get_win_all_1(rule) < w_num:
            # win_all_1() is assumed to be equal to the max window number.
            raise ValueError(
                    "ERROR: the packet size > WSize. {} > {}".format(
                            w_num, schcmsg.get_win_all_1(rule)))
        self.max_w_num = w_num
        #print("DEBUG: all_tiles:")
        #for i in self.all_tiles:
        #    print("DEBUG:  ", i)

    def get_tiles(self, mtu_size):
        '''
        return the tiles containing the contiguous tiles fitting in mtu_size.
        And, remaiing nb_tiles to be sent in all_tiles.
        '''
        remaining_size = mtu_size - schcmsg.get_sender_header_size(self.rule)
        max_tiles = remaining_size // self.t_size
        tiles = []
        t_prev = None
        #print('header size: ', schcmsg.get_sender_header_size(self.rule))
        #print('mtu_size: ', mtu_size)
        #print('max_tiles: ', max_tiles)
        #print('t_size: ', self.t_size)
        #print('remaining_size: ', remaining_size)

        for i in range(len(self.all_tiles)):
            t = self.all_tiles[i]
            '''
            if t_prev and t_prev["t-num"] + 1 < t["t-num"]:
                break
            '''
            if t["sent"] == False:
                tiles.append(t)
                t["sent"] = True
                t_prev = t
            if len(tiles) == max_tiles:
                break
        if len(tiles) == 0:
            return None, 0, remaining_size
        # return tiles and the remaining bits
        nb_remaining_tiles = len(
                [ _ for _ in self.all_tiles if _["sent"] == False ])
        remaining_size -= self.get_tile_size(tiles)
        return tiles, nb_remaining_tiles, remaining_size

    def get_all_tiles(self):
        return self.all_tiles

    def unset_sent_flag(self, win, bit_list):
        """ set the sent flag to False from True.
        """
        def unset_sent_flag_do(wn, tn):
            if tn is None:
                # special case. i.e. the last tile.
                self.all_tiles[-1]["sent"] = False
                return
            # normal case.
            for t in self.all_tiles:
                if t["w-num"] == wn:
                    if t["t-num"] == self.max_fcn - tn:
                        t["sent"] = False
        #
        if self.max_w_num == win:
            # last window
            for bi in range(len(bit_list[:-1])):
                if bit_list[bi] == 0:
                    unset_sent_flag_do(win, bi)
            unset_sent_flag_do(win, None)
        else:
            for bi in range(len(bit_list)):
                if bit_list[bi] == 0:
                    unset_sent_flag_do(win, bi)

    @staticmethod
    def get_tile_size(tiles):
        size = 0
        for i in tiles:
            size += i["tile"].count_added_bits()
        return size

    @staticmethod
    def concat(tiles):
        bbuf = BitBuffer()
        for t in tiles:
            bbuf += t["tile"]
        return bbuf

#---------------------------------------------------------------------------
