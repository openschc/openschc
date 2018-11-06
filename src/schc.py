# C.A. 2018
# ---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import warnings

class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)"""
    #def __init__(self, config, scheduler, schc_layer2, role="sender"):
    def __init__(self, config, scheduler, schc_layer2):
        warnings.warn("XXX: use NewSCHCProtocol")
        self.config = config
        self.scheduler = scheduler
        self.layer2 = schc_layer2
        self.layer2.set_receive_callback(self.event_receive_packet)
        '''
        if role == "sender":
            self.layer2.set_receive_callback(self.event_sender_receive_packet)
        elif role == "receiver":
            self.layer2.set_receive_callback(self.event_receiver_receive_packet)
        else:
            raise ValueError("role must be sender or receiver.")
        '''
        self.default_frag_rule = None # XXX: to be in  rule_manager

    def set_frag_rule(self, rule):
        self.rule = rule

# ---------------------------------------------------------------------------

from schcrecv import ReassemblerAckOnError
from schcsend import FragmentAckOnError

class NewSCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)"""
    #def __init__(self, config, scheduler, schc_layer2, role="sender"):
    def __init__(self, config, scheduler, layer2, layer3):
        self.config = config
        self.scheduler = scheduler
        self.layer2 = layer2
        self.layer3 = layer3
        print(self.layer2)
        self.layer2._set_protocol(self)
        self.layer3._set_protocol(self)
        self.default_frag_rule = None # XXX: to be in  rule_manager
        self.reassembly_session = ReassemblerAckOnError(self, None) # XXX
        self.fragmentation_session = FragmentAckOnError(self, None) # XXX

    #def find_session(self, device_id):
    #    # XXX: to do
    #    return self.session

    def set_frag_rule(self, rule):
        self.rule = rule
        self.reassembly_session.rule = rule
        self.fragmentation_session.rule = rule

    def event_receive_from_L3(self, packet):
        print("[schc] recv [L3:%s] -> %s"
              % (self.layer2.mac_id, packet))

        # [the diagram that was drawn]
        # Compress/etc.

        # XXX: copied from SCHCProtocolSender.send_packet()

        #session = FragmentAckOnError(self, None) # XXX:hack
        session = self.fragmentation_session
        session.set_packet(packet)
        frag = session.get_frags()
        dev_id = self.layer2.mac_id
        print(frag)
        print(dev_id, frag.packet.get_content())
        def callback(*args):
            print("packet sent!", self.sim.get_time())
        args = (frag.packet.get_content(), dev_id)
        self.scheduler.add_event(0, self.layer2.send_packet, args)
        session.update_frags_sent_flag()


    def event_receive_from_L2(self, device_id, raw_packet):
        print("[schc] recv [L2:%s] -> SCHC[mac:%s] %s"
              % (device_id, self.layer2.mac_id, raw_packet))

        #session = self.find_session(device_id)
        session = self.reassembly_session
        session.process_packet(raw_packet)

# ---------------------------------------------------------------------------
