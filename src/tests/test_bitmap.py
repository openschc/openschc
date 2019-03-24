import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")

from schcbitmap import find_missing_tiles, make_bit_list
from bitarray import BitBuffer
if sys.implementation.name != "micropython":
    import pytest


def check_bitmaps(bitmaps, expected):
    print("bitmaps:", bitmaps)
    for i in bitmaps:
        bm = []
        for j in range(i[1].count_added_bits()):
            bm.append(i[1].get_bits(1, j))
        bitmap_str = lambda x: "".join("{}".format(_) for _ in x)
        print("\t{{ w:{} bm:{} }}".format(i[0], bitmap_str(bm)))
    assert str(bitmaps) == str(expected)


def test_fragment_bitmap_01():
    print("## bit list")
    tile_list = [
                { "w-num": 0, "t-num": 6, "nb_tiles": 3 },
                { "w-num": 0, "t-num": 3, "nb_tiles": 4 },
                { "w-num": 1, "t-num": 6, "nb_tiles": 3 },
                { "w-num": 1, "t-num": 3, "nb_tiles": 3 },
                { "w-num": 3, "t-num": 5, "nb_tiles": 2 },
                { "w-num": 3, "t-num": 7, "nb_tiles": 1 },
            ]
    bit_list = make_bit_list(tile_list, 3, 7)
    expected_list = {
        0: [1, 1, 1, 1, 1, 1, 1],
        1: [1, 1, 1, 1, 1, 1, 0],
        2: [0, 0, 0, 0, 0, 0, 0],
        3: [0, 1, 1, 0, 0, 0, 1],
        }

    for i in bit_list.items():
        print(i)
    assert bit_list == expected_list


def test_fragment_bitmap_02():
    print("## find_missing_tiles:")
    tile_list = [
                { "w-num": 0, "t-num": 6, "nb_tiles": 3 },
                { "w-num": 0, "t-num": 3, "nb_tiles": 4 },
                { "w-num": 1, "t-num": 6, "nb_tiles": 3 },
                { "w-num": 1, "t-num": 3, "nb_tiles": 3 },
                { "w-num": 3, "t-num": 5, "nb_tiles": 2 },
                { "w-num": 3, "t-num": 7, "nb_tiles": 1 },
            ]
    bitmaps = find_missing_tiles(tile_list, 3, 7)
    expected = [
        (1, BitBuffer([1, 1, 1, 1, 1, 1, 0])),
        (2, BitBuffer([0, 0, 0, 0, 0, 0, 0])),
        (3, BitBuffer([0, 1, 1, 0, 0, 0, 1]))
        ]
    check_bitmaps(bitmaps, expected)


def test_fragment_bitmap_03():
    print("""## Figure 27 in draft-17""")
    N = 3
    WINDOW_SIZE = 7
    nb_tiles = 11
    tile_list = [
        {"w-num": 0, "t-num": 6, "nb_tiles": 1 },
        {"w-num": 0, "t-num": 5, "nb_tiles": 1 },
        #{"w-num": 0, "t-num": 4, "nb_tiles": 1 },
        {"w-num": 0, "t-num": 3, "nb_tiles": 1 },
        #{"w-num": 0, "t-num": 2, "nb_tiles": 1 },
        {"w-num": 0, "t-num": 1, "nb_tiles": 1 },
        {"w-num": 0, "t-num": 0, "nb_tiles": 1 },
        {"w-num": 1, "t-num": 6, "nb_tiles": 1 },
        {"w-num": 1, "t-num": 5, "nb_tiles": 1 },
        #{"w-num": 1, "t-num": 4, "nb_tiles": 1 },
        {"w-num": 1, "t-num": 7, "nb_tiles": 1 },
        ]

    bitmaps = find_missing_tiles(tile_list, N, WINDOW_SIZE)
    expected = [
        (0, BitBuffer([1, 1, 0, 1, 0, 1, 1])), 
        (1, BitBuffer([1, 1, 0, 0, 0, 0, 1]))
        ]
    check_bitmaps(bitmaps, expected)

    tile_list.append({"w-num": 0, "t-num": 4, "nb_tiles": 1 })
    tile_list.append({"w-num": 0, "t-num": 2, "nb_tiles": 1 })
    bitmaps = find_missing_tiles(tile_list, N, WINDOW_SIZE)
    expected = [
        (1, BitBuffer([1, 1, 0, 0, 0, 0, 1]))
        ]
    check_bitmaps(bitmaps, expected)

    tile_list.append({"w-num": 1, "t-num": 4, "nb_tiles": 1 })
    bitmaps = find_missing_tiles(tile_list, N, WINDOW_SIZE)
    expected = [
        (1, BitBuffer([1, 1, 1, 0, 0, 0, 1]))
        ]
    check_bitmaps(bitmaps, expected)

def test_fragment_bitmap_04():
    print("""## Figure 28 in draft-17""")
    N = 5 # all-1 = 31
    WINDOW_SIZE = 28
    tile_list = [
        {"w-num": 0, "t-num": 27, "nb_tiles": 4 },
        {"w-num": 0, "t-num": 23, "nb_tiles": 4 },
        {"w-num": 0, "t-num": 19, "nb_tiles": 4 },
        #{"w-num": 0, "t-num": 15, "nb_tiles": 4 },
        {"w-num": 0, "t-num": 11, "nb_tiles": 4 },
        {"w-num": 0, "t-num":  7, "nb_tiles": 4 },
        {"w-num": 0, "t-num":  3, "nb_tiles": 4 },
        {"w-num": 1, "t-num": 27, "nb_tiles": 4 },
        {"w-num": 1, "t-num": 23, "nb_tiles": 4 },
        {"w-num": 1, "t-num": 19, "nb_tiles": 4 },
        {"w-num": 1, "t-num": 15, "nb_tiles": 4 },
        {"w-num": 1, "t-num": 11, "nb_tiles": 4 },
        {"w-num": 1, "t-num":  7, "nb_tiles": 4 },
        #{"w-num": 1, "t-num":  3, "nb_tiles": 4 },
        {"w-num": 2, "t-num": 27, "nb_tiles": 4 },
        {"w-num": 2, "t-num": 23, "nb_tiles": 4 },
        {"w-num": 2, "t-num": 19, "nb_tiles": 1 },
        {"w-num": 2, "t-num": 18, "nb_tiles": 1 },
        {"w-num": 2, "t-num": 17, "nb_tiles": 1 },
        {"w-num": 2, "t-num": 16, "nb_tiles": 1 },
        {"w-num": 2, "t-num": 15, "nb_tiles": 1 },
        {"w-num": 2, "t-num": 14, "nb_tiles": 1 },
        #{"w-num": 2, "t-num": 13, "nb_tiles": 1 },
        {"w-num": 2, "t-num": 12, "nb_tiles": 1 },
        {"w-num": 2, "t-num": 31, "nb_tiles": 1 },
        ]

    bitmaps = find_missing_tiles(tile_list, N, WINDOW_SIZE)
    expected = [
        (0, BitBuffer([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1])),
        (1, BitBuffer([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 0, 0, 0, 0])),
        (2, BitBuffer([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 1]))]
    check_bitmaps(bitmaps, expected)

    tile_list.append({"w-num": 0, "t-num": 15, "nb_tiles": 4 })
    bitmaps = find_missing_tiles(tile_list, N, WINDOW_SIZE)
    expected = [
        (1, BitBuffer([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 0, 0, 0, 0])),
        (2, BitBuffer([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 1]))]
    check_bitmaps(bitmaps, expected)

    tile_list.append({"w-num": 1, "t-num":  3, "nb_tiles": 4 })
    bitmaps = find_missing_tiles(tile_list, N, WINDOW_SIZE)
    expected = [
        (2, BitBuffer([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 1]))]
    check_bitmaps(bitmaps, expected)

    tile_list.append({"w-num": 2, "t-num": 13, "nb_tiles": 1 })
    bitmaps = find_missing_tiles(tile_list, N, WINDOW_SIZE)
    expected = [
        (2, BitBuffer([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 1]))]
    check_bitmaps(bitmaps, expected)


# for micropython and other tester.
if __name__ == "__main__":
    test_fragment_bitmap_01()
    test_fragment_bitmap_02()
    test_fragment_bitmap_03()
    test_fragment_bitmap_04()
