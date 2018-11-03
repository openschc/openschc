
from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg

rule_as_dict = {
    # Header format
    "rule-id-size": 6,
    "dtag-size": 2,
    "window-size": 5,
    "fcn-size": 3,
    "mode": "ack-on-error",

    "tile-size": 30,
    "mic-algorithm": "crc32"
}

#---------------------------------------------------------------------------
# XXX: put rule_manager

Rule = namedtuple("Rule", "rule_id_size dtag_size window_size"
                  + " fcn_size mode tile_size mic_algorithm")

def rule_from_dict(rule_as_dict):
    rule_as_dict = { k.replace("-","_"): v for k,v in rule_as_dict.items() }
    return Rule(**rule_as_dict)

#---------------------------------------------------------------------------

class FakeSCHCProtocolSender(schc.SCHCProtocol):

    def start_sending(self):
        return
        fragment = schcmsg.frag_sender_tx(
            R=rule, dtag=DTAG, win=0, fcn=6, mic=None, bitmap=None,
            cbit=None, payload=None)
        print("->", fragment.dump())

def make_test_fragment_list(rule):
    rule_id = 9
    dtag = 1
    W = 0
    one_tile = 30 * b"\0"
    message = schcmsg.frag_sender_tx(rule, rule_id, dtag, W, one_tile)

rule = rule_from_dict(rule_as_dict)
print(rule)
print(make_test_fragment_list(rule))

