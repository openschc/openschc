"""
.. module:: schctile
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from base_import import *

import schcmsg

#---------------------------------------------------------------------------

class TileList():

    # XXX it is almost about the sender side, should be moved into schcsend.py.
    # XXX may it be used in NO-ACK ?
    def __init__(self, rule, packet_bbuf, max_fcn = None):
        self.rule = rule
        self.t_size = rule["tileSize"]
        self.max_fcn = max_fcn if max_fcn is not None else schcmsg.get_max_fcn(rule) 
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
                #dont know why it is a special case, if the ALL-1 is received with a tile
                #then it should always be one, if the tile is consired received by the method
                #below, then it should not be false

                #i think the problem is when the sender does not know if it is the last one
                #so the the bitmap is received with the max_fcn bit on 1, but since there are
                #less tiles than the max_fcn. it does not look for that bit
                print("last tile case")
                #self.all_tiles[-1]["sent"] = False
                return
            # normal case.
            counter = 0
            print('unset_sent_flag_do')
            for t in self.all_tiles:
                if t["w-num"] == wn:
                    if t["t-num"] == self.max_fcn - tn:
                        counter += 1
                        print('counter = {}, t-num {}, tn {}'.format(counter, t["t-num"],tn))
                        t["sent"] = False
                    elif t["t-num"] == self.max_fcn:
                        print("t-num {} == max_fcn {}".format(t["t-num"],self.max_fcn))
        
        print("unset_sent_flag")
        print("bit_list -> {}".format(bit_list))
        print("self.max_w_num:{} win:{}, len(bit_list[:-1]):{}".format(self.max_w_num, win, len(bit_list[:-1])))
        if self.max_w_num == win:
            # last window
            print("last window")
            print("self.all_tiles -> {}".format(self.all_tiles))

            for bi in range(len(bit_list)):
                print("bi -> {}".format(bi))
                if bit_list[bi] == 0:
                    
                    unset_sent_flag_do(win, bi)
            #unset_sent_flag_do(win, None)
            if bit_list[-1] == 1:
                print("Problem in tx, the last bit is set as 1")
                print("self.all_tiles -> {}".format(self.all_tiles))
                self.all_tiles[-1]["sent"] = True
                #unset_sent_flag_do()
        else:
            print("not last window")
            for bi in range(len(bit_list)):
                if bit_list[bi] == 0:
                    unset_sent_flag_do(win, bi)
        print("self.all_tiles -> {}".format(self.all_tiles))
        #input('tiles after for')

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
