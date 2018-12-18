#---------------------------------------------------------------------------

from base_import import *

import schcmsg

#---------------------------------------------------------------------------

all1 = lambda N: (1<<N)-1

def sort_tile_list(tile_list, N):
    def sort_fcn(n):
        """ sort the list into the FCN order.
        All ones of FCN is put at the end of the list, otherwise, it is
        descending order.  i.e. [ 6, 5, 4, 3, 2, 1, 0, 7 ]
        """
        if all1(N) == n:
            return n
        return -n
    #
    return sorted(tile_list, key=(lambda a: (a["w-num"],sort_fcn(a["t-num"]))))

#---------------------------------------------------------------------------

def make_bit_list(tile_list, N, window_size):
    """ make a bit list for each window from the tile_list, and return it.
    the bit list is going to be used to make the bitmap.
    The tile_list passed in the argument should be formed like below.
    Note that if nb_tiles doesn't exist, it is assumed as one.
        [
            { "w-num": 0, "t-num": 6, "nb_tiles": 3 },
            { "w-num": 0, "t-num": 3, "nb_tiles": 3 },
            { "w-num": 2, "t-num": 5, "nb_tiles": 2 },
            { "w-num": 2, "t-num": 7, "nb_tiles": 1 },
        ]
    In this example, the the bit list will be
        {
            0: [1, 1, 1, 1, 1, 1, 0],
            1: [0, 0, 0, 0, 0, 0, 0],
            2: [1, l, l, 0, 0, 0, 1],
        }
    """
    max_fcn = window_size - 1
    bit_list = {}
    wni = 0
    sorted_tile_list = sort_tile_list(tile_list, N)
    # main
    tni = max_fcn
    for t in sorted_tile_list:
        bl = bit_list.setdefault(wni, [])
        wn = t["w-num"]
        tn = t["t-num"]
        nbt = t.get("nb_tiles", 1)
        # all-1
        if tn == all1(N):
            while tni > 0:
                bl.append(0)
                tni -= 1
            if nbt == 1:
                bl.append(1)
                break
        # regular
        if wni < wn:
            #print("MBL00 wn:tn:nb=", wni, tni, bl)
            while wni < wn:
                bl = bit_list.setdefault(wni, [])
                while tni > 0:
                    bl.append(0)
                    tni -= 1
                bl.append(0)
                wni += 1
                tni = max_fcn
                #print("MBL01 wn:tn:nb=", wni, tni, bl)
        #print("MBL1 nb=", nbt)
        assert wni == wn
        bl = bit_list.setdefault(wni, [])
        while tni > tn:
            bl.append(0)
            tni -= 1
            #print("MBL2 wn:tn:nb=", wni, tni, bl)
        for _ in range(nbt):
            bl.append(1)
            if tni == 0:
                #print("MBL3 wn:tn:nb=", wni, tni, bl)
                wni += 1
                bl = bit_list.setdefault(wni, [])
                tni = max_fcn
            else:
                #print("MBL4 wn:tn:nb=", wni, tni, bl)
                tni -= 1
    return bit_list

#---------------------------------------------------------------------------

def find_missing_tiles(tile_list, N, window_size):
    """ find missing tiles in the tile_list.
    return the set of bitmaps for each window in which any tiles are missing.
    the bitmap is tranformed into BitBuffer like below.
        [
            (0, BitBuffer([1, 1, 1, 1, 1, 1, 0])),
            (2, BitBuffer([1, l, l, 0, 0, 0, 1])),
        ]
    In this example, the bitmap will be "1110001".
    """
    bit_list = make_bit_list(tile_list, N, window_size)
    ret = []
    for i in sorted(bit_list.items()):
        if not all(i[1]):
            ret.append((i[0], BitBuffer(i[1])))
    return ret

#---------------------------------------------------------------------------
