# ---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

#import rulemanager
from fakerulemgr import FakeRuleManager as RuleManager
import compress

# ---------------------------------------------------------------------------

from schcrecv import ReassemblerAckOnError
from schcsend import FragmentAckOnError
from compress import Compression

class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)"""
    #def __init__(self, config, scheduler, schc_layer2, role="sender"):
    def __init__(self, config, system, layer2, layer3):
        self.config = config
        self.system = system
        self.scheduler = system.get_scheduler()
        self.layer2 = layer2
        self.layer3 = layer3
        self.layer2._set_protocol(self)
        self.layer3._set_protocol(self)
        self.default_frag_rule = None # XXX: to be in  rule_manager
        self.reassembly_session = ReassemblerAckOnError(self, None) # XXX
        self.fragmentation_session = FragmentAckOnError(self, None) # XXX
        self.compression = compress.Compression(self)
        self.rule_manager = RuleManager()

    def _log(self, message):
        self.log("schc", message)

    def log(self, name, message):
        self.system.log(name, message)

    #def find_session(self, device_id):
    #    # XXX: to do
    #    return self.session

    def set_frag_rule(self, rule):
        self.rule_manager.set_frag_rule(rule)
        self.reassembly_session.rule = rule
        self.fragmentation_session.rule = rule

    def event_receive_from_L3(self, packet):
        self._log("recv-from-L3 {}".format(packet))

        # hc-17,509-529

        # [the diagram that was drawn]
        # Compress/etc.

        # @@538-550
        schc_packet_bitbuffer, meta_info = self.compression.compress(packet)
        rule_id, rule, frag_meta_info = self.rule_manager.find_frag_rule(
            schc_packet_bitbuffer, meta_info)

        self._log("fragmentation rule_id={}".format(rule_id))
        #self.start_frag_session(schc_packet_bitbuffer, frag_meta_info)

        #assert "mode" in self.meta_info2
        #if "mode" == "fragmentation":
        #
        #elif "mode" == "reassembly":
        #    print("XXX")

        # XXX: copied from SCHCProtocolSender.send_packet()

        #def start_frag_session(self, schc_packet_bitbuffer, meta_info):

        #session = FragmentAckOnError(self, None) # XXX:hack
        session = self.fragmentation_session
        session.set_packet(packet)
        session.start_sending()

    def event_receive_from_L2(self, device_id, raw_packet):
        self._log("recv-from-L2 {}->{} {}".format(
            device_id, self.layer2.mac_id, raw_packet))

        #session = self.find_session(device_id)
        session = self.reassembly_session
        session.process_packet(raw_packet)

# ---------------------------------------------------------------------------
