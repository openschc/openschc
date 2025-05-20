from frag_tile import TileList
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


#-------------------Tests--Function--sort_tile_list----------------------------------------------------
def test_sort_3Windows_5Tiles() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_3W_5T
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 4}, 
                                 {'w-num': 0, 't-num': 3}, 
                                 {'w-num': 1, 't-num': 6}, 
                                 {'w-num': 1, 't-num': 2}, 
                                 {'w-num': 2, 't-num': 5}]
    assert sort_tile_list(tile_list,3) == expected_sorted_tile_list

def test_sort_3Windows_5Tiles_1to3_nbtile() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_3W_5T_nb1to3
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 6, 'nb_tiles': 2}, 
                                 {'w-num': 0, 't-num': 3, 'nb_tiles': 3}, 
                                 {'w-num': 1, 't-num': 4, 'nb_tiles': 3}, 
                                 {'w-num': 1, 't-num': 7, 'nb_tiles': 1}, 
                                 {'w-num': 2, 't-num': 5, 'nb_tiles': 2}]
    assert sort_tile_list(tile_list,3) == expected_sorted_tile_list
    
def test_sort_2Windows_3Tiles_single_nbtile() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_2W_3T_single_nb
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 3}, 
                                 {'w-num': 0, 't-num': 0}, 
                                 {'w-num': 1, 't-num': 6, 'nb_tiles': 1}]
    assert sort_tile_list(tile_list,3) == expected_sorted_tile_list


def test_sort_2Windows_3Tiles_wrongkey_wnum() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_2W_3T_wrongkey_wnum
    with pytest.raises(KeyError, match="w-num"):
        sort_tile_list(tile_list,3) 

def test_sort_2Windows_3Tiles_wrongkey_tnum() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_2W_3T_wrongkey_tnum
    with pytest.raises(KeyError, match="t-num"):
        sort_tile_list(tile_list,3) 

def test_sort_2Windows_3Tiles_wrongkey_nbtiles() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_2W_3T_wrongkey_nb
    with pytest.raises(KeyError, match="nb_tiles"):
        sort_tile_list(tile_list,3) 


def test_sort_2Windows_3Tiles_Negative_wnum() -> None:
    """Test that sort tile list raises a ValueError when a w-num is a negative number."""
    tile_list = list_2W_3T_negative_wnum
    with pytest.raises(ValueError, match="All w-num need to be bigger than 0"):
        sort_tile_list(tile_list,3)

def test_sort_2Windows_3Tiles_Negative_tnum() -> None:
    """Test that sort tile list raises a ValueError when a t-num is a negative number."""
    tile_list = list_2W_3T_negative_tnum
    with pytest.raises(ValueError, match="All t-num need to be bigger than 0"):
        sort_tile_list(tile_list,3) 

def test_sort_2Windows_3Tiles_Zero_nbtiles() -> None:
    """Test that sort tile list raises a ValueError when a nb_tiles is zero."""
    tile_list = list_2W_3T_zero_nb
    with pytest.raises(ValueError, match="All nb_tiles need to be bigger than 1"):
        sort_tile_list(tile_list,3)

def test_sort_2Windows_3Tiles_Negative_nbtiles() -> None:
    """Test that sort tile list raises a ValueError when a nb_tiles is a negative number."""
    tile_list = list_2W_3T_negative_nb
    with pytest.raises(ValueError, match="All nb_tiles need to be bigger than 1"):
        sort_tile_list(tile_list,3)


def test_sort_5Tiles_AllLetters() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_5T_AllLetters
    with pytest.raises(TypeError, match="bad operand type for unary -: 'str'"):
        sort_tile_list(tile_list,3) 

def test_sort_2Windows_3Tiles_letter_wnum() -> None:
    """Test that sort tile list raises a ValueError when a w-num is a letter."""
    tile_list = list_2W_3T_letter_wnum
    with pytest.raises(TypeError, match="'<' not supported between instances of 'str' and 'int'"):
        sort_tile_list(tile_list,3)

def test_sort_2Windows_3Tiles_letter_tnum() -> None:
    """Test that sort tile list raises a ValueError when a t-num is a letter."""
    tile_list = list_2W_3T_letter_tnum
    with pytest.raises(TypeError, match="bad operand type for unary -: 'str'"):
        sort_tile_list(tile_list,3) 

def test_sort_2Windows_3Tiles_letter_nbtiles() -> None:
    """Test that sort tile list raises a ValueError when a nb_tiles is a letter."""
    tile_list = list_2W_3T_letter_nb
    with pytest.raises(TypeError, match="bad operand type for unary -: 'str'"):
        sort_tile_list(tile_list,3)


def test_sort_3Tiles_AllNone() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_3T_AllNone
    with pytest.raises(TypeError, match="bad operand type for unary -: 'NoneType'"):
        sort_tile_list(tile_list,3) 

def test_sort_2Windows_3Tiles_none_wnum() -> None:
    """Test that sort tile list raises a ValueError when a w-num is a letter."""
    tile_list = list_2W_3T_none_wnum
    with pytest.raises(TypeError, match="'<' not supported between instances of 'NoneType' and 'int'"):
        sort_tile_list(tile_list,3)

def test_sort_2Windows_3Tiles_none_tnum() -> None:
    """Test that sort tile list raises a ValueError when a t-num is a letter."""
    tile_list = list_2W_3T_none_tnum
    with pytest.raises(TypeError, match="bad operand type for unary -: 'NoneType'"):
        sort_tile_list(tile_list,3) 

def test_sort_2Windows_3Tiles_none_nbtiles() -> None:
    """Test that sort tile list raises a ValueError when a nb_tiles is a letter."""
    tile_list = list_2W_3T_none_nb
    with pytest.raises(TypeError, match="bad operand type for unary -: 'str'"):
        sort_tile_list(tile_list,3)


def test_sort_3Windows_5Tiles_Repeated() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_3W_5T_repeated
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 4, 'nb_tiles': 1}, 
                                 {'w-num': 0, 't-num': 3, 'nb_tiles': 1}, 
                                 {'w-num': 0, 't-num': 3, 'nb_tiles': 1}, 
                                 {'w-num': 1, 't-num': 6, 'nb_tiles': 1}, 
                                 {'w-num': 1, 't-num': 7, 'nb_tiles': 1}, 
                                 {'w-num': 2, 't-num': 5, 'nb_tiles': 1}, 
                                 {'w-num': 2, 't-num': 5, 'nb_tiles': 1}]
    assert sort_tile_list(tile_list,3) == expected_sorted_tile_list

def test_sort_1Window_9Tiles_N3() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_1W_9T
    #expected_sorted_tile_list = [{'w-num': 0, 't-num': 15}, 
    #                             {'w-num': 0, 't-num': 12}, 
    #                             {'w-num': 0, 't-num': 9}, 
    #                             {'w-num': 0, 't-num': 5}, 
    #                             {'w-num': 0, 't-num': 4}, 
    #                             {'w-num': 0, 't-num': 3}, 
    #                             {'w-num': 0, 't-num': 1}, 
    #                             {'w-num': 0, 't-num': 0}, 
    #                             {'w-num': 0, 't-num': 7}]
    with pytest.raises(ValueError, match="There are t-nums bigger than All-1"):
        sort_tile_list(tile_list,3)
    
def test_sort_1Window_9Tiles_N4() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_1W_9T
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 12}, 
                                 {'w-num': 0, 't-num': 9}, 
                                 {'w-num': 0, 't-num': 7}, 
                                 {'w-num': 0, 't-num': 5}, 
                                 {'w-num': 0, 't-num': 4}, 
                                 {'w-num': 0, 't-num': 3}, 
                                 {'w-num': 0, 't-num': 1}, 
                                 {'w-num': 0, 't-num': 0}, 
                                 {'w-num': 0, 't-num': 15}]
    assert sort_tile_list(tile_list,4) == expected_sorted_tile_list
    
def test_sort_1Window_9Tiles_N5() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_1W_9T
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 15}, 
                                 {'w-num': 0, 't-num': 12}, 
                                 {'w-num': 0, 't-num': 9}, 
                                 {'w-num': 0, 't-num': 7}, 
                                 {'w-num': 0, 't-num': 5}, 
                                 {'w-num': 0, 't-num': 4}, 
                                 {'w-num': 0, 't-num': 3}, 
                                 {'w-num': 0, 't-num': 1}, 
                                 {'w-num': 0, 't-num': 0}]
    assert sort_tile_list(tile_list,5) == expected_sorted_tile_list

#-------------------Tests--Function--make_bit_list----------------------------------------------------
def test_make_bit_list_3Windows_5Tiles() -> None:
    """Test that make bit list returns the correct list."""
    tile_list = list_3W_5T
    expected_bit_list = {
            0: [0, 0, 1, 1, 0, 0, 0],
            1: [1, 0, 0, 0, 1, 0, 0],
            2: [0, 1]
            #2: [0, 1, 0, 0, 0, 0, 0]
        }
    assert make_bit_list(tile_list,3,7) == expected_bit_list
    
def test_make_bit_list_1Windows_9Tiles() -> None:
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