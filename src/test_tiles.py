# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")
from gen_rulemanager import *
from frag_tile import TileList
import io
from gen_utils import dprint, dpprint, set_debug_output
import pytest

def frag_generic(rule, packet):
    # General configuration
    l2_mtu = 72  # bits
    data_size = 14  # bytes
    SF = 12

    simul_config = {
        "log": True,
    }
    devaddr = b"\xaa\xbb\xcc\xdd"

    set_debug_output(True)
    rm0 = RuleManager()
    rm0.Add(devaddr, dev_info=rule)

    # Message
    packet_bbuf = BitBuffer(packet)
    tiles = TileList(rm0.FindFragmentationRule(devaddr), packet_bbuf)

    for t in tiles.get_all_tiles():
        print(t)

    set_debug_output(False)
    return True


def test_make_tiles():
    rule = {
            "RuleID": 12,
            "RuleIDLength": 6,
            "Fragmentation": {
                    "FRMode": "AckOnError",
                    "FRDirection": "DW",
                    "FRModeProfile": {
                            "dtagSize": 2,
                            "ackBehavior": "afterAll1",
                            "MICAlgorithm": "RCS_RFC8724",
                            "MICWordSize": 8,
                            "lastTileInAll1": False
                            }
                    }
            }
    packet_size = 7 # 56 bits
    packet = bytearray(b"".join([b"\x55" for _ in range(packet_size)]))
    wsize = 3
    fcn_size = 3
    rule["Fragmentation"]["FRModeProfile"].update(
                {"WSize": wsize})
    rule["Fragmentation"]["FRModeProfile"].update(
                {"FCNSize": fcn_size})
    for tile_size in range(9, 32):
        rule["Fragmentation"]["FRModeProfile"].update(
                {"tileSize": tile_size})
        print("---- packet_size={} WSize={} FCNSize={} tile_size={} ----"
              .format(packet_size, wsize, fcn_size, tile_size))
        stdout = frag_generic(rule, packet)

test_make_tiles()
