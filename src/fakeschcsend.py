
from base_import import *  # used for now for differing modules in py/upy

import schc

# https://raw.githubusercontent.com/wiki/openschc/doc/draft-ietf-lpwan-ipv6-static-context-hc-17-ref.txt

# 1434 8.3.1.1.  Regular SCHC Fragment
# 1435
# 1436    The Regular SCHC Fragment format is shown in Figure 11.  Regular SCHC
# 1437    Fragments are generally used to carry tiles that are not the last one
# 1438    of a SCHC Packet.  The DTag field and the W field are optional.
# 1439
# 1440  |--- SCHC Fragment Header ----|
# 1441            |-- T --|-M-|-- N --|
# 1442  +-- ... --+- ... -+---+- ... -+--------...-------+~~~~~~~~~~~~~~~~~~~~~
# 1443  | Rule ID | DTag  | W |  FCN  | Fragment Payload | padding (as needed)
# 1444  +-- ... --+- ... -+---+- ... -+--------...-------+~~~~~~~~~~~~~~~~~~~~~

# 1517   |---- SCHC ACK Header ----|
# 1518               |-- T --|-M-|1|
# 1519   +---- ... --+- ... -+---+-+~~~~~~~~~~~~~~~~~~
# 1520   |  Rule ID  |  DTag | W |1| padding as needed                (success)
# 1521   +---- ... --+- ... -+---+-+~~~~~~~~~~~~~~~~~~

sys.path.append("schctest")
#import
import schc_fragment_holder

#schc_fragment_holder.XXX


RULE_ID_SIZE = 6
DTAG_SIZE = 2
WINDOW_SIZE = 5
FCN_SIZE = 3

# the above parameters allow having a header aligned on byte boundaries
MAX_WIND_FCN = 6
TILE_SIZE = 30

RULE_ID = 9
DTAG = 1

# XXX:
FCN_ALL_0 = 0

class Struct:
    pass

RULE = Struct()
RULE.rid = RULE_ID
RULE.C = Struct()
RULE.C.rid_size =  RULE_ID_SIZE
RULE.dtag_size = DTAG_SIZE
RULE.win_size = WINDOW_SIZE
RULE.fcn_size = FCN_SIZE
PAYLOAD_SIZE = 30

class FakeSCHCProtocolSender(schc.SCHCProtocol):

    def start_sending(self):
        #packet = b""
        fragment = schc_fragment_holder.frag_sender_tx(
            R=RULE,
            dtag=DTAG, win=0, fcn=6, mic=None, bitmap=None,
            cbit=None, payload=None)
        #fragment.set_param(rid=, dtag=, win=, fcn=, mic=None, bitmap=None,
        #                   cbit=None, payload=b"")
        #fragment.init_param()
        print("->", fragment.dump())
        #print(fragment)
        #self.layer2.send_packet(fragment)


def fake_schc_packet(config, rule, payload):
    fragment = schc_fragment_holder.frag_sender_tx(
        R=RULE,
        dtag=DTAG, win=0, fcn=6, mic=None, bitmap=None,
        cbit=None, payload=payload)
    return fragment


fake_packet = fake_schc_packet(None, None, "0"*30)
print(fake_packet.dump())
print(fake_packet.full_dump())

