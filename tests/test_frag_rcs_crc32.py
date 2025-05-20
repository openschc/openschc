from frag_rcs_crc32 import get_mic
from frag_rcs_crc32 import get_mic_size
import pytest
#-----------------Tile--Lists--------------------------------------------------------
list_3W_5T = [
            { "w-num": 1, "t-num": 6 },
            { "w-num": 0, "t-num": 3 },
            { "w-num": 2, "t-num": 5 },
            { "w-num": 1, "t-num": 2 },
            { "w-num": 0, "t-num": 4 }
        ]

list_3W_5T_nb1to3 = [
            { "w-num": 1, "t-num": 4, "nb_tiles": 3 },
            { "w-num": 0, "t-num": 6, "nb_tiles": 2 },
            { "w-num": 2, "t-num": 5, "nb_tiles": 2 },
            { "w-num": 1, "t-num": 7, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 3, "nb_tiles": 3 }
        ]

list_2W_3T_single_nb = [
            { "w-num": 0, "t-num": 3 },
            { "w-num": 1, "t-num": 6, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 0 }
        ]

list_2W_3T_wrongkey_wnum = [
            { "w-num": 0, "t-num": 3 },
            { "k-num": 1, "t-num": 6 },
            { "w-num": 0, "t-num": 0 }
        ]

list_2W_3T_wrongkey_tnum = [
            { "w-num": 0, "t-num": 3 },
            { "w-num": 1, "e-num": 6 },
            { "w-num": 0, "t-num": 0 }
        ]

list_2W_3T_wrongkey_nb = [
            { "w-num": 0, "t-num": 3, "nb_tiles": 1 },
            { "w-num": 1, "t-num": 6, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 0, "nb_tles": 1 }
        ]

list_2W_3T_negative_wnum = [
            { "w-num": 0, "t-num": 3 },
            { "w-num": -1, "t-num": 6 },
            { "w-num": 0, "t-num": 0 }
        ]

list_2W_3T_negative_tnum = [
            { "w-num": 0, "t-num": 0},
            { "w-num": 0, "t-num": 4},
            { "w-num": 1, "t-num": -7}

        ]

list_2W_3T_negative_nb = [
            { "w-num": 1, "t-num": 3, "nb_tiles": 2 },
            { "w-num": 0, "t-num": 2, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 4, "nb_tiles": -1 }
        ]

list_2W_3T_zero_nb = [
            { "w-num": 1, "t-num": 5, "nb_tiles": 2 },
            { "w-num": 0, "t-num": 2, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 1, "nb_tiles": 0 }
        ]

list_5T_AllLetters = [
            { "w-num": "b", "t-num": "g", "nb_tiles": 1 },
            { "w-num": "a", "t-num": "d", "nb_tiles": 1 },
            { "w-num": "c", "t-num": "f", "nb_tiles": 1 },
            { "w-num": "b", "t-num": "h", "nb_tiles": 1 },
            { "w-num": "a", "t-num": "e", "nb_tiles": 1 }
        ]

list_2W_3T_letter_wnum = [
            { "w-num": 0, "t-num": 3 },
            { "w-num": "a", "t-num": 6 },
            { "w-num": 0, "t-num": 0 }
        ]

list_2W_3T_letter_tnum = [
            { "w-num": 0, "t-num": 0 },
            { "w-num": 0, "t-num": 4 },
            { "w-num": 1, "t-num": "h"}

        ]

list_2W_3T_letter_nb = [
            { "w-num": 1, "t-num": 3, "nb_tiles": 2 },
            { "w-num": 0, "t-num": 2, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 4, "nb_tiles": "b" }
        ]

list_3T_AllNone = [
            { "w-num": None, "t-num": None, "nb_tiles": None },
            { "w-num": None, "t-num": None, "nb_tiles": None },
            { "w-num": None, "t-num": None, "nb_tiles": None }
        ]

list_2W_3T_none_wnum = [
            { "w-num": 0, "t-num": 3},
            { "w-num": None, "t-num": 6 },
            { "w-num": 0, "t-num": 0 }
        ]

list_2W_3T_none_tnum = [
            { "w-num": 0, "t-num": 0 },
            { "w-num": 0, "t-num": 4 },
            { "w-num": 1, "t-num": None }

        ]

list_2W_3T_none_nb = [
            { "w-num": 1, "t-num": 3, "nb_tiles": 2 },
            { "w-num": 0, "t-num": 2, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 4, "nb_tiles": None }
        ]

list_3W_5T_repeated = [
            { "w-num": 2, "t-num": 5, "nb_tiles": 1 },
            { "w-num": 1, "t-num": 6, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 3, "nb_tiles": 1 },
            { "w-num": 2, "t-num": 5, "nb_tiles": 1 },
            { "w-num": 1, "t-num": 7, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 4, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 3, "nb_tiles": 1 }
        ]

list_1W_9T = [
            { "w-num": 0, "t-num": 9},
            { "w-num": 0, "t-num": 4},
            { "w-num": 0, "t-num": 5},
            { "w-num": 0, "t-num": 7},
            { "w-num": 0, "t-num": 1},
            { "w-num": 0, "t-num": 3},
            { "w-num": 0, "t-num": 0},
            { "w-num": 0, "t-num": 15},
            { "w-num": 0, "t-num": 12}
        ]


#-------------------Tests--Function--get_mic----------------------------------------------------
def test_get_mic_3Windows_5Tiles() -> None:
    """Test that make bit list returns the correct list."""
    tile_list = list_3W_5T
    expected_bit_list = {
            0: [0, 0, 1, 1, 0, 0, 0],
            1: [1, 0, 0, 0, 1, 0, 0],
            2: [0, 1]
            #2: [0, 1, 0, 0, 0, 0, 0]
        }
    assert make_bit_list(tile_list,3,7) == expected_bit_list
    
def test_get_mic_1Windows_9Tiles() -> None:
    """Test that make bit list returns the correct list."""
    tile_list = list_1W_9T
    expected_bit_list = {
            #0: [1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1]
            0: [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1]
        }
    print(make_bit_list(tile_list,4,15))
    print(make_bit_list(tile_list,4,16))
    print(make_bit_list(tile_list,5,17))
    assert make_bit_list(tile_list,5,17) == expected_bit_list
#-------------------Tests--Function--get_mic_size----------------------------------------------------
def test_get_mic_size_3Windows_5Tiles() -> None:
    """Test that make bit list returns the correct list."""
    tile_list = list_3W_5T
    expected_bit_list = {
            0: [0, 0, 1, 1, 0, 0, 0],
            1: [1, 0, 0, 0, 1, 0, 0],
            2: [0, 1]
            #2: [0, 1, 0, 0, 0, 0, 0]
        }
    assert make_bit_list(tile_list,3,7) == expected_bit_list
    
def test_get_mic_size_1Windows_9Tiles() -> None:
    """Test that make bit list returns the correct list."""
    tile_list = list_1W_9T
    expected_bit_list = {
            #0: [1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1]
            0: [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1]
        }
    print(make_bit_list(tile_list,4,15))
    print(make_bit_list(tile_list,4,16))
    print(make_bit_list(tile_list,5,17))
    assert make_bit_list(tile_list,5,17) == expected_bit_list