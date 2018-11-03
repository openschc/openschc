

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


class FakeSCHCProtocolSender(schc.SCHCProtocol):
    pass
