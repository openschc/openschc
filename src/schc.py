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
        self.default_frag_rule = None # XXX: to be in  rule_manager
        self.frag_manager = None

    def send_packet(self, packet):
        # Should do:
        # - compression
        # - fragmentation
        # (and sending packets)
        #compression_rule = XXX
        #self.compression_manager.compress(compression_rule)
        packet = packet[:]  # Null compression

        # XXX:TODO select the rule
        rule = self.rule
        if self.frag_manager is not None:
            self.frag_manager.send_packet(rule, packet)
        else:
            self.layer2.send_packet(packet)

    def set_frag_rule(self, rule):
        self.rule = rule

    def event_receive_packet(self, other_mac_id, packet):
        print("[mac%s] -> SCHC[mac:%s] %s"
              % (other_mac_id, self.layer2.mac_id, packet))
        if(len(packet) < 10):
            self.send_packet(packet+b"%s"%self.layer2.mac_id)

# ---------------------------------------------------------------------------
