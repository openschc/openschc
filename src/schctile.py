import schcmsg
from schctest import pybinutil as bu # XXX

#---------------------------------------------------------------------------

class TileList():

    def __init__(self, rule, packet):
        t_size = rule.tile_size
        t_init_num = schcmsg.get_max_MAX_WIN_FCN(rule)
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
            if t_num == 0:
                t_num = t_init_num
                w_num += 1
            else:
                t_num -= 1
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

    def update_sent_flag(self):
        for t in self.tile_list:
            if t["ready_to_be_sent"] == True:
                t["sent"] = True

    @staticmethod
    def get_bytearray(tiles):
        buf = bytearray()
        pos = 0
        for t in tiles:
            bu.bit_set(buf, pos, t["tile"], extend=True)
            pos += len(t["tile"])
        return buf

