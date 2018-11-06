# C.A. 2018
# ---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)"""
    #def __init__(self, config, scheduler, schc_layer2, role="sender"):
    def __init__(self, config, scheduler, schc_layer2):
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
