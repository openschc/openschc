# C.A. 2018
# ---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)"""
    def __init__(self, config, scheduler, schc_layer2):
        self.config = config
        self.scheduler = scheduler
        self.layer2 = schc_layer2
        self.layer2.set_receive_callback(self.event_receive_packet)

    def send_packet(self, packet):
        # Should do:
        # - compression
        # - fragmentation
        # (and sending packets)
        self.layer2.send_packet(packet)

    def event_receive_packet(self, other_mac_id, packet):
        print("[mac%s] -> SCHC[mac:%s] %s"
              % (other_mac_id, self.layer2.mac_id, packet))
        if(len(packet) < 10):
            self.send_packet(packet+b"%s"%self.layer2.mac_id)

# ---------------------------------------------------------------------------
