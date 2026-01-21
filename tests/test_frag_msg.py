from frag_msg import get_fcn_all_0
from frag_msg import get_fcn_all_1
from frag_msg import get_win_all_1
from frag_msg import get_max_dtag
from frag_msg import get_max_fcn
from frag_msg import get_sender_header_size
from frag_msg import get_receiver_header_size
from frag_msg import get_mic_size
from frag_msg import roundup
from frag_msg import frag_base
from frag_msg import frag_tx
from frag_msg import frag_receiver_tx
from frag_msg import frag_sender_tx_abort
from frag_msg import frag_sender_tx
from frag_msg import frag_sender_ack_req
from frag_msg import frag_receiver_tx_all0_ack
from frag_msg import frag_receiver_tx_all1_ack
from frag_msg import frag_receiver_tx_abort
from frag_msg import frag_rx
from frag_msg import frag_sender_rx_all0_ack
from frag_msg import frag_sender_rx
from frag_msg import frag_receiver_rx
import pytest

#-------------------Test-Rules----------------------------------------------------
example_rule = {
    "RuleID": 1,
    "RuleIDLength": 3,
    "Fragmentation" : {
        "FRMode": "ackOnError",
        "FRDirection": "UP",
        "FRModeProfile": {
            "dtagSize": 2,
            "WSize": 5,
            "FCNSize": 3,
            "ackBehavior": "afterAll1",
            "tileSize": 9,
            "MICAlgorithm": "crc32",
            "MICWordSize": 8,
            "maxRetry": 4,
            "timeout": 600,
            "lastTileInAll1": False,
            "windowSize": 7
        }
    }
}

#-------------------Tests--Function--get_fcn_all_1----------------------------------------------------
def test_get_fcn_all_1() -> None:
    """Test that validates get_fcn_all_1."""
    assert get_fcn_all_1(example_rule) == 7

#-------------------Tests--Function--get_fcn_all_0----------------------------------------------------
def test_get_fcn_all_0() -> None:
    """Test that validates get_fcn_all_0."""
    assert get_fcn_all_0(example_rule) == -4

#-------------------Tests--Function--get_win_all_1----------------------------------------------------
def test_get_win_all_1() -> None:
    """Test that validates get_win_all_1."""
    assert get_win_all_1(example_rule) == 31

#-------------------Tests--Function--get_max_dtag----------------------------------------------------
def test_get_max_dtag() -> None:
    """Test that validates get_max_dtag."""
    assert get_max_dtag(example_rule) == 3

#-------------------Tests--Function--get_max_fcn----------------------------------------------------
def test_get_max_fcn() -> None:
    """Test that validates get_max_fcn."""
    assert get_max_fcn(example_rule) == 6

#-------------------Tests--Function--get_sender_header_size----------------------------------------------------
def test_get_sender_header_size() -> None:
    """Test that validates get_sender_header_size."""
    assert get_sender_header_size(example_rule) == 13

#-------------------Tests--Function--get_receiver_header_size----------------------------------------------------
def test_get_receiver_header_size() -> None:
    """Test that validates get_receiver_header_size."""
    assert get_receiver_header_size(example_rule) == 11
    
#-------------------Tests--Function--roundup----------------------------------------------------
def test_roundup() -> None:
    """Test that validates get_receiver_header_size."""
    assert roundup(17,8) == 24

#-------------------Tests--Function--frag_base----------------------------------------------------
def test_frag_base__max_Dtag_bad() -> None:
    """Test that validates get_receiver_header_size."""
    test = frag_base()
    test.init_param()
    with pytest.raises(ValueError, match="All w-num need to be bigger than 0"):
        test.set_param(example_rule)