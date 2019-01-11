# C.A. 2018
# ---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy
from frag_man import fragment_manager

class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)"""
    def __init__(self, config, scheduler, schc_layer2, role="sender"):
        self.config = config
        self.scheduler = scheduler
        self.layer2 = schc_layer2
        if role == "sender":
            self.layer2.set_receive_callback(self.event_sender_receive_packet)
        else:
            self.layer2.set_receive_callback(self.event_receiver_receive_packet)
        self.default_frag_rule = None # XXX: to be in  rule_manager
        self.frag_manager = fragment_manager(config, scheduler, schc_layer2)
        #self.frag_manager = None

    def send_packet(self, packet, peer_iid=None):
        # Should do:
        # - compression
        # - fragmentation
        # (and sending packets)
        #compression_rule = XXX
        #self.compression_manager.compress(compression_rule)
        packet = packet[:]  # Null compression

        # XXX:TODO select the rule
        if self.frag_manager is not None:
            self.frag_manager.send_packet(self.rule, packet, peer_iid=peer_iid)
        else:
            self.layer2.send_packet(packet)

    def frag_manager(self):
        pass

    def set_frag_rule(self, rule):
        self.rule = rule

    def event_sender_receive_packet(self, other_mac_id, packet):
        print("S: [mac%s] -> SCHC[mac:%s] %s"
              % (other_mac_id, self.layer2.mac_id, packet))
        if(len(packet) < 10):
            if self.frag_manager is not None:
                self.frag_manager.recv_ack(packet, peer_iid=self.layer2.mac_id)
            else:
                self.send_packet(packet+self.layer2.mac_id.to_bytes(6,byteorder="big"))

    def event_receiver_receive_packet(self, other_mac_id, packet):
        print("R: [mac%s] -> SCHC[mac:%s] %s"
              % (other_mac_id, self.layer2.mac_id, packet))
        if(len(packet) < 10):
            if self.frag_manager is not None:
                self.frag_manager.recv_ack(packet, peer_iid=self.layer2.mac_id)
            else:
                self.send_packet(packet+self.layer2.mac_id.to_bytes(6,byteorder="big"))

# ---------------------------------------------------------------------------
