



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



class FakeSCHCProtocolReceiver(schc.SCHCProtocol):

    def event_receive_packet(self, other_mac_id, packet):
        print("[mac%s] -> SCHC[mac:%s] %s"
              % (other_mac_id, self.layer2.mac_id, packet))
        #if(len(packet) < 10):
        #    self.send_packet(packet+b"%s"%self.layer2.mac_id)
        #
        # 1)
        # parse_packet
        # print parsed

        # 2)
        # if FCN==all-0? (or "end of window")
        #  self.send_packet(ACK-success)

        # 3)
        # if FCN==all-1?
        #  see draft, ask c. l. d. s.
        # compute MIC?

