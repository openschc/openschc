"""
.. module:: frag_bitmap
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from gen_base_import import *
from gen_utils import dprint

import frag_msg

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
        dprint("t:{}".format(t))
        bl = bit_list.setdefault(wni, [])
        wn = t["w-num"]
        tn = t["t-num"]
        nbt = t.get("nb_tiles", 1)
        # all-1
        if tn == all1(N):
            dprint("----all ones found:wn:{}, tn:{}, nbt:{}, tni:{}".format(wn,tn,nbt,tni))
            #if the number of tiles is smaller than max_fcn,
            #and there is a tile in the ALL-1, the bit that should be 
            #set to one is not the last one, but the ones next to the
            #previous tile number
            #example, tiles 1 tile in ALL-1
            dprint("nb_tiles {}".format(nbt))
            if len(sorted_tile_list) == 1:
                #just the all-1 message was received all other fragments were lost
                #bitmap sould be [0,0,0,0,0,1]
                for _ in range(max_fcn-1):
                    #add zeros to all other tiles 
                    bl.append(0)
                #add the last bit as 1 -> fcn = 7
                #bl.append(1)
            if nbt >= 1:
                dprint("a tile in the last fragment")
                if max_fcn - 1 != tni:
                    dprint("tile is the last of the packet, should be number {}".format(tni))
                    for _ in range(tni): # from 0 to tni.
                        # add zeros to all other tiles
                        bl.append(0)
                #if more than one tile is in the ALL-1 message
                for _ in range(nbt):
                    dprint("append 1")
                    bl.append(1)
                break
            else:
                while tni-1 > 0:
                    bl.append(0)
                    tni -= 1
                if nbt == 1:
                    dprint("append 1")
                    bl.append(1)
                    break
        # regular
        if wni < wn:
            dprint("MBL00 wn:tn:nb=", wni, tni, bl)
            while wni < wn:
                bl = bit_list.setdefault(wni, [])
                while tni > 0:
                    dprint("padding")
                    bl.append(0)
                    tni -= 1
                bl.append(0)
                wni += 1
                tni = max_fcn
                dprint("MBL01 wn:tn:nb=", wni, tni, bl)
        dprint("MBL1 nb=", nbt)
        #assert wni == wn
        bl = bit_list.setdefault(wni, [])
        while tni > tn:
            bl.append(0)
            tni -= 1
            dprint("MBL2 wn:tn:nb=", wni, tni, bl)
        for _ in range(nbt):
            bl.append(1)
            if tni == 0:
                dprint("MBL3 wn:tn:nb=", wni, tni, bl)
                wni += 1
                bl = bit_list.setdefault(wni, [])
                tni = max_fcn
            else:
                dprint("MBL4 wn:tn:nb=", wni, tni, bl)
                tni -= 1
    return bit_list

# def make_bit_list(tile_list, N, window_size):
#     """ make a bit list for each window from the tile_list, and return it.
#     the bit list is going to be used to make the bitmap.
#     The tile_list passed in the argument should be formed like below.
#     Note that if nb_tiles doesn't exist, it is assumed as one.
#         [
#             { "w-num": 0, "t-num": 6, "nb_tiles": 3 },
#             { "w-num": 0, "t-num": 3, "nb_tiles": 3 },
#             { "w-num": 2, "t-num": 5, "nb_tiles": 2 },
#             { "w-num": 2, "t-num": 7, "nb_tiles": 1 },
#         ]
#     In this example, the the bit list will be
#         {
#             0: [1, 1, 1, 1, 1, 1, 0],
#             1: [0, 0, 0, 0, 0, 0, 0],
#             2: [1, l, l, 0, 0, 0, 1],
#         }
#     """
#     max_fcn = window_size - 1
#     bit_list = {}
#     wni = 0
#     sorted_tile_list = sort_tile_list(tile_list, N)
#     # main
#     tni = max_fcn
#     for t in sorted_tile_list:
#         bl = bit_list.setdefault(wni, [])
#         wn = t["w-num"]
#         tn = t["t-num"]
#         nbt = t.get("nb_tiles", 1)
#         # all-1
#         if tn == all1(N):
#             while tni > 0:
#                 bl.append(0)
#                 tni -= 1
#             if nbt == 1:
#                 bl.append(1)
#                 break
#         # regular
#         if wni < wn:
#             #dprint("MBL00 wn:tn:nb=", wni, tni, bl)
#             while wni < wn:
#                 bl = bit_list.setdefault(wni, [])
#                 while tni > 0:
#                     bl.append(0)
#                     tni -= 1
#                 bl.append(0)
#                 wni += 1
#                 tni = max_fcn
#                 #dprint("MBL01 wn:tn:nb=", wni, tni, bl)
#         #dprint("MBL1 nb=", nbt)
#         assert wni == wn
#         bl = bit_list.setdefault(wni, [])
#         while tni > tn:
#             bl.append(0)
#             tni -= 1
#             #dprint("MBL2 wn:tn:nb=", wni, tni, bl)
#         for _ in range(nbt):
#             bl.append(1)
#             if tni == 0:
#                 #dprint("MBL3 wn:tn:nb=", wni, tni, bl)
#                 wni += 1
#                 bl = bit_list.setdefault(wni, [])
#                 tni = max_fcn
#             else:
#                 #dprint("MBL4 wn:tn:nb=", wni, tni, bl)
#                 tni -= 1
#     return bit_list


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
    modified to because the last 1 when only there is one window was not set
    to one when the all-1 arrives
        [
            (0, BitBuffer([1, 1, 1, 1, 1, 1, 0])),
            (2, BitBuffer([1, l, l, 0, 0, 0, 1])),
        ]
    In this example, the bitmap will be "1110001".
    There are problems to create an ack when the all has not arrived and 
    an ack request is received.
    """
    bit_list = make_bit_list(tile_list, N, window_size)
    dprint('find_missing_tiles bit_list -> {}, lenght: {}'.format(bit_list, len(bit_list)))
    ret = []
    for i in sorted(bit_list.items()):
        dprint(" i, all(i[1]) {},{}".format(i,all(i[1])))
        if not all(i[1]):
            ret.append((i[0], BitBuffer(i[1])))
        #else:
        #    ret.append((i[0], BitBuffer(i[1])))
    dprint("find_missing_tiles ret -> {}".format(ret))
    #input("")
    return ret

def find_missing_tiles_no_all_1(tile_list, N, window_size):
    """ find missing tiles in the tile_list.
    return the set of bitmaps for each window in which any tiles are missing.
    the bitmap is tranformed into BitBuffer like below.
        [
            (0, BitBuffer([1, 1, 1, 1, 1, 1, 0])),
            (2, BitBuffer([1, l, l, 0, 0, 0, 1])),
        ]
    In this example, the bitmap will be "1110001".
    modified to because the last 1 when only there is one window was not set
    to one when the all-1 arrives
        [
            (0, BitBuffer([1, 1, 1, 1, 1, 1, 0])),
            (2, BitBuffer([1, l, l, 0, 0, 0, 1])),
        ]
    In this example, the bitmap will be "1110001".
    There are problems to create an ack when the all has not arrived and 
    an ack request is received.
    """
    bit_list = make_bit_list_no_all_1(tile_list, N, window_size)
    dprint('find_missing_tiles_no_all_1 - bit_list -> {}, lenght: {}'.format(bit_list, len(bit_list)))
    ret = []
    for i in sorted(bit_list.items()):
        dprint(" i, all(i[1]) {},{}".format(i,all(i[1])))
        if not all(i[1]):
            ret.append((i[0], BitBuffer(i[1])))
        else:
            ret.append((i[0], BitBuffer(i[1])))
    dprint("find_missing_tiles_no_all_1 ret -> {}".format(ret))
    #input('')
    return ret

def make_bit_list_no_all_1(tile_list, N, window_size):
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
        dprint("t:{}".format(t))
        bl = bit_list.setdefault(wni, [])
        wn = t["w-num"]
        tn = t["t-num"]
        nbt = t.get("nb_tiles", 1)
        # all-1
        if tn == all1(N):
            dprint("all ones found:wn:{}, tn:{}, nbt:{}, tni:{}".format(wn,tn,nbt,tni))
            #if the number of tiles is smaller than max_fcn,
            #and there is a tile in the ALL-1, the bit that should be 
            #set to one is not the last one, but the ones next to the
            #previous tile number
            #example, tiles 1 tile in ALL-1
            dprint("nb_tiles {}".format(nbt))
            if len(sorted_tile_list) == 1:
                #just the all-1 message was received all other fragments were lost
                #bitmap sould be [0,0,0,0,0,1]
                for _ in range(max_fcn):
                    #add zeros to all other tiles 
                    bl.append(0)
                #add the last bit as 1 -> fcn = 7
                #bl.append(1)
            if nbt >= 1:
                dprint("a tile in the last fragment")
                if max_fcn - 1 != tni:
                    dprint("tile is the last of the packet, should be number {}".format(tni))    
                #if more than one tile is in the ALL-1 message
                for _ in range(nbt):
                    dprint("append 1")
                    bl.append(1)
                break
            else:
                while tni-1 > 0:
                    bl.append(0)
                    tni -= 1
                if nbt == 1:
                    dprint("append 1")
                    bl.append(1)
                    break
        # regular
        if wni < wn:
            dprint("MBL00 wn:tn:nb=", wni, tni, bl)
            while wni < wn:
                bl = bit_list.setdefault(wni, [])
                while tni > 0:
                    dprint("padding")
                    bl.append(0)
                    tni -= 1
                bl.append(0)
                wni += 1
                tni = max_fcn
                dprint("MBL01 wn:tn:nb=", wni, tni, bl)
        dprint("MBL1 nb=", nbt)
        assert wni == wn
        bl = bit_list.setdefault(wni, [])
        while tni > tn:
            bl.append(0)
            tni -= 1
            dprint("MBL2 wn:tn:nb=", wni, tni, bl)
        for _ in range(nbt):
            bl.append(1)
            if tni == 0:
                dprint("MBL3 wn:tn:nb=", wni, tni, bl)
                wni += 1
                bl = bit_list.setdefault(wni, [])
                tni = max_fcn
            else:
                dprint("MBL4 wn:tn:nb=", wni, tni, bl)
                tni -= 1
    if len(bl) != max_fcn:
        #bitmap should be larger
        dprint("max_fcn:{} bl:{} tni:{} ".format(max_fcn, bl,tni))
        while tni != 0:
            bl.append(0)
            tni -= 1
            dprint("tni:{}".format(tni))
        
        dprint("max_fcn:{} bl:{} tni:{} ".format(max_fcn, bl,tni))
 
        dprint("bl:{}".format(bl))
    return bit_list

def find_missing_tiles_mic_ko_yes_all_1(tile_list, N, window_size):
    """ find missing tiles in the tile_list.
    return the set of bitmaps for each window in which any tiles are missing.
    the bitmap is tranformed into BitBuffer like below.
        [
            (0, BitBuffer([1, 1, 1, 1, 1, 1, 0])),
            (2, BitBuffer([1, l, l, 0, 0, 0, 1])),
        ]
    In this example, the bitmap will be "1110001".
    modified to because the last 1 when only there is one window was not set
    to one when the all-1 arrives
        [
            (0, BitBuffer([1, 1, 1, 1, 1, 1, 0])),
            (2, BitBuffer([1, l, l, 0, 0, 0, 1])),
        ]
    In this example, the bitmap will be "1110001".
    There are problems to create an ack when the all has not arrived and 
    an ack request is received.
    The problem with this bitmap is that is not recognized by the method
    in the sender that checks what tiles are missing. It will compare the following:
        received bitmap : (0, BitBuffer([1, l, l, 0, 0, 0, 1]))
        sender bitmap: (0,BitBuffer([1, 1, 1, 1]))
    Also when the ALL-1 is received, the mic is ko and the resulting bit_list
    is [], there is a problem since some tiles are missing the result bitmap is
 
        received bitmap : (0, BitBuffer([1, l, l, 0, 0, 0, 0]))
        sender bitmap: (0,BitBuffer([1, 1, 1, 1]))
    """
    #case when the bit_list is return empty from find_missing_tiles (meaning there are no missing tiles)
    #but since the MIC is KO there are some missing tiles
    bit_list = make_bit_list_mic_ko(tile_list, N, window_size)
    dprint('find_missing_tiles_mic_ko_yes_all_1 - bit_list -> {}, lenght: {}'.format(bit_list, len(bit_list)))
    ret = []
    for i in sorted(bit_list.items()):
        dprint(" i, all(i[1]) {},{}".format(i,all(i[1])))
        if not all(i[1]):
            ret.append((i[0], BitBuffer(i[1])))
        #else:
        #    ret.append((i[0], BitBuffer(i[1])))
    dprint("find_missing_tiles_mic_ko_yes_all_1 ret -> {}".format(ret))
    #input('')
    return ret
 
def make_bit_list_mic_ko(tile_list, N, window_size):
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
    dprint("make_bit_list_mic_ko")
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
        # all-1
        if tn == all1(N):
            dprint("all ones found:wn:{}, tn:{}, nbt:{}, tni:{}".format(wn,tn,nbt,tni))
            #if the number of tiles is smaller than max_fcn,
            #and there is a tile in the ALL-1, the bit that should be 
            #set to one is not the last one, but the ones next to the
            #previous tile number
            #example, tiles 1 tile in ALL-1
            #input('Only received the all-1, added the 1 for the tiles and the last pos')
            dprint("nb_tiles {} len(sorted_tile_list):{}".format(nbt,len(sorted_tile_list)))
            if len(sorted_tile_list) == 1:
                #just the all-1 message was received all other fragments were lost
                #bitmap sould be [0,0,0,0,0,1] if only one tile in the all-1 message
                for _ in range(max_fcn-nbt+1):
                    #add zeros to all other tiles, until the tiles in the all-1 
                    bl.append(0)
                for _ in range(nbt):
                    #add ones for the tiles in the ALL-1
                    dprint("append 1")
                    bl.append(1)
                #add the last bit as 1 -> fcn = 7
                #bl.append(1)
                dprint(bl)
                #input('Only received the all-1, added the 1 for the tiles and the last pos')
                break
            elif nbt >= 1:
                #more fragments arrived and not only the all-1
                dprint("a tile in the last fragment but we dont know the tile number")
                if max_fcn - 1 != tni:
                    #checks the position, if all other tiles have arrived
                    dprint("tile is the last of the packet, should be number {}".format(tni))    
                for _ in range(tni):
                    bl.append(0) 
                #if more than one tile is in the ALL-1 message
                for _ in range(nbt):
                    dprint("append 1")
                    bl.append(1)
                dprint(bl)
                #input('added the 1 for the tiles and the last pos')                
                break
            else:
                while tni-1 > 0:
                    bl.append(0)
                    tni -= 1
 
                if nbt == 1:
                    #will never be True 
                    dprint("append 1")
                    bl.append(1)
                break
        # if tn == all1(N):
        #     while tni > 0:
        #         bl.append(0)
        #         tni -= 1
        #     if nbt == 1:
        #         bl.append(1)
        #         break
        # regular
        if wni < wn:
            dprint("MBL00 wn:tn:nb=", wni, tni, bl)
            while wni < wn:
                bl = bit_list.setdefault(wni, [])
                while tni > 0:
                    bl.append(0)
                    tni -= 1
                bl.append(0)
                wni += 1
                tni = max_fcn
                dprint("MBL01 wn:tn:nb=", wni, tni, bl)
        dprint("MBL1 nb=", nbt)
        #assert wni == wn
        bl = bit_list.setdefault(wni, [])
        while tni > tn:
            bl.append(0)
            tni -= 1
            dprint("MBL2 wn:tn:nb=", wni, tni, bl)
        for _ in range(nbt):
            bl.append(1)
            if tni == 0:
                dprint("MBL3 wn:tn:nb=", wni, tni, bl)
                wni += 1
                bl = bit_list.setdefault(wni, [])
                tni = max_fcn
            else:
                dprint("MBL4 wn:tn:nb=", wni, tni, bl)
                tni -= 1
    return bit_list
    """
    max_fcn = window_size - 1
    bit_list = {}
    wni = 0
    sorted_tile_list = sort_tile_list(tile_list, N)
    # main
    tni = max_fcn
    for t in sorted_tile_list:
        dprint("t:{}".format(t))
        bl = bit_list.setdefault(wni, [])
        wn = t["w-num"]
        tn = t["t-num"]
        nbt = t.get("nb_tiles", 1)
        # all-1
        if tn == all1(N):
            dprint("all ones found:wn:{}, tn:{}, nbt:{}, tni:{}".format(wn,tn,nbt,tni))
            #if the number of tiles is smaller than max_fcn,
            #and there is a tile in the ALL-1, the bit that should be 
            #set to one is not the last one, but the ones next to the
            #previous tile number
            #example, tiles 1 tile in ALL-1
            dprint("nb_tiles {}".format(nbt))
            if len(sorted_tile_list) == 1:
                #just the all-1 message was received all other fragments were lost
                #bitmap sould be [0,0,0,0,0,1]
                for _ in range(max_fcn-1):
                    #add zeros to all other tiles 
                    bl.append(0)
                #add the last bit as 1 -> fcn = 7
                #bl.append(1)
            if nbt >= 1:
                dprint("a tile in the last fragment")
                if max_fcn - 1 != tni:
                    dprint("tile is the last of the packet, should be number {}".format(tni))    
                #if more than one tile is in the ALL-1 message
                for _ in range(nbt):
                    dprint("append 1")
                    bl.append(1)
                break
            else:
                while tni-1 > 0:
                    bl.append(0)
                    tni -= 1
                if nbt == 1:
                    dprint("append 1")
                    bl.append(1)
                    break
        # regular
        if wni < wn:
            dprint("MBL00 wn:tn:nb=", wni, tni, bl)
            while wni < wn:
                bl = bit_list.setdefault(wni, [])
                while tni > 0:
                    dprint("padding")
                    bl.append(0)
                    tni -= 1
                bl.append(0)
                wni += 1
                tni = max_fcn
                dprint("MBL01 wn:tn:nb=", wni, tni, bl)
        dprint("MBL1 nb=", nbt)
        assert wni == wn
        bl = bit_list.setdefault(wni, [])
        while tni > tn:
            bl.append(0)
            tni -= 1
            dprint("MBL2 wn:tn:nb=", wni, tni, bl)
        for _ in range(nbt):
            bl.append(1)
            if tni == 0:
                dprint("MBL3 wn:tn:nb=", wni, tni, bl)
                wni += 1
                bl = bit_list.setdefault(wni, [])
                tni = max_fcn
            else:
                dprint("MBL4 wn:tn:nb=", wni, tni, bl)
                tni -= 1
    return bit_list
    """



    
#---------------------------------------------------------------------------
