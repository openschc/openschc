from src.frag_bitmap import sort_tile_list
import pytest

list_3W_5T = [
            { "w-num": 1, "t-num": 6, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 3, "nb_tiles": 1 },
            { "w-num": 2, "t-num": 5, "nb_tiles": 1 },
            { "w-num": 1, "t-num": 7, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 4, "nb_tiles": 1 }
        ]

list_3W_5T_negative = [
            { "w-num": -1, "t-num": -6, "nb_tiles": -1 },
            { "w-num": 0, "t-num": -3, "nb_tiles": -1 },
            { "w-num": -2, "t-num": -5, "nb_tiles": -1 },
            { "w-num": -1, "t-num": -7, "nb_tiles": -1 },
            { "w-num": 0, "t-num": -4, "nb_tiles": -1 }
        ]

list_3W_5T_letters = [
            { "w-num": "b", "t-num": "g", "nb_tiles": 1 },
            { "w-num": "a", "t-num": "d", "nb_tiles": 1 },
            { "w-num": "c", "t-num": "f", "nb_tiles": 1 },
            { "w-num": "b", "t-num": "h", "nb_tiles": 1 },
            { "w-num": "a", "t-num": "e", "nb_tiles": 1 }
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

list_3W_5T_nb2 = [
            { "w-num": 1, "t-num": 4, "nb_tiles": 2 },
            { "w-num": 0, "t-num": 3, "nb_tiles": 2 },
            { "w-num": 2, "t-num": 5, "nb_tiles": 2 },
            { "w-num": 1, "t-num": 7, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 0, "nb_tiles": 2 }
        ]

list_3W_5T_nb1to3 = [
            { "w-num": 1, "t-num": 4, "nb_tiles": 3 },
            { "w-num": 0, "t-num": 3, "nb_tiles": 2 },
            { "w-num": 2, "t-num": 5, "nb_tiles": 2 },
            { "w-num": 1, "t-num": 7, "nb_tiles": 1 },
            { "w-num": 0, "t-num": 0, "nb_tiles": 3 }
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

def test_sort_3Windows_5Tiles() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_3W_5T
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 4, 'nb_tiles': 1}, 
                                 {'w-num': 0, 't-num': 3, 'nb_tiles': 1}, 
                                 {'w-num': 1, 't-num': 6, 'nb_tiles': 1}, 
                                 {'w-num': 1, 't-num': 7, 'nb_tiles': 1}, 
                                 {'w-num': 2, 't-num': 5, 'nb_tiles': 1}]
    assert sort_tile_list(tile_list,3) == expected_sorted_tile_list

def test_sort_3Windows_5Tiles_Negative() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_3W_5T_negative
    expected_sorted_tile_list = [{'w-num': -2, 't-num': -5, 'nb_tiles': -1}, 
                                 {'w-num': -1, 't-num': -6, 'nb_tiles': -1}, 
                                 {'w-num': -1, 't-num': -7, 'nb_tiles': -1},
                                 {'w-num': 0, 't-num': -3, 'nb_tiles': -1}, 
                                 {'w-num': 0, 't-num': -4, 'nb_tiles': -1}]
    assert sort_tile_list(tile_list,3) == expected_sorted_tile_list

def test_sort_3Windows_5Tiles_Letters() -> None:
    """Test that sort tile list sorts positive numbers returns the correct result."""
    tile_list = list_3W_5T_letters
    
    expected_sorted_tile_list = [{'w-num': 'a', 't-num': 'e', 'nb_tiles': 1}, 
                                 {'w-num': 'a', 't-num': 'd', 'nb_tiles': 1}, 
                                 {'w-num': 'b', 't-num': 'g', 'nb_tiles': 1}, 
                                 {'w-num': 'b', 't-num': 'h', 'nb_tiles': 1}, 
                                 {'w-num': 'c', 't-num': 'f', 'nb_tiles': 1}]
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
    expected_sorted_tile_list = [{'w-num': 0, 't-num': 15}, 
                                 {'w-num': 0, 't-num': 12}, 
                                 {'w-num': 0, 't-num': 9}, 
                                 {'w-num': 0, 't-num': 5}, 
                                 {'w-num': 0, 't-num': 4}, 
                                 {'w-num': 0, 't-num': 3}, 
                                 {'w-num': 0, 't-num': 1}, 
                                 {'w-num': 0, 't-num': 0}, 
                                 {'w-num': 0, 't-num': 7}]
    assert sort_tile_list(tile_list,3) == expected_sorted_tile_list
    
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