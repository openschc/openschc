# ---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

from fakerulemgr import FakeRuleManager as RuleManager
import compress

# ---------------------------------------------------------------------------

from schcrecv import ReassemblerAckOnError
from schcrecv import ReassemblerNoAck
from schcsend import FragmentAckOnError
from schcsend import FragmentNoAck
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
        self.compression = compress.Compression(self)
        self.fragment_session_list = {}

    def _log(self, message):
        self.log("schc", message)

    def log(self, name, message):
        self.system.log(name, message)

    def set_rulemanager(self, rule_manager):
        self.rule_manager = rule_manager

    def event_receive_from_L3(self, remote_id, raw_packet):
        self._log("recv-from-L3 -> {} {}".format(remote_id, raw_packet))
        packet_bbuf = BitBuffer(raw_packet)

        # hc-17,509-529

        rule = self.rule_manager.findRuleByRemoteID(remote_id)
        if rule is None:
            self._log("no SCHC processing for the packet.")
            args = (raw_packet, self.layer2.mac_id, None, None)
            self.scheduler.add_event(0, self.layer2.send_packet, args)
            return

        # [the diagram that was drawn]
        if "compression" in rule:
            # Compress/etc.
            # @@538-550
            self._log("compression rule_id={}".format(rule.ruleID))
            packet_bbuf, meta_info = self.compression.compress(packet_bbuf)
        else:
            self._log("no SCHC compression for the packet.")

        if "fragmentation" in rule:
            self._log("fragmentation rule_id={}".format(rule.ruleID))
            mode = rule.get("FRMode")
            if mode == "noAck":
                session = FragmentNoAck(self, rule) # XXX
            elif mode == "ackAlwayw":
                raise NotImplementedError(
                        "{} is not implemented yet.".format(mode))
            elif mode == "ackOnError":
                session = FragmentAckOnError(self, rule) # XXX
            else:
                raise ValueError("invalid FRMode: {}".format(mode))
            session.set_packet(packet_bbuf)
            session.start_sending()
            # self.layer2.send_packet() will be called in the session.
        else:
            self._log("no SCHC fragmentation for the packet.")
            args = (packet_bbuf.get_content(), self.layer2.mac_id, None,
                    None)
            self.scheduler.add_event(0, self.layer2.send_packet, args)
            return

    def new_reassemble_session(self, bbuf, rule, remote_id, context=None):
        #self.rule_manager.set_frag_rule(rule)
        mode = rule.get("FRMode")
        if mode == "noAck":
            session = ReassemblerNoAck(self, rule, remote_id) # XXX
        elif mode == "ackAlways":
            raise NotImplementedError("FRMode:", mode)
        elif mode == "ackOnError":
            session = ReassemblerAckOnError(self, rule, remote_id) # XXX
        else:
            raise ValueError("FRMode:", mode)
        session.rule = rule
        return session

    def event_receive_from_L2(self, device_id, raw_packet):
        self._log("recv-from-L2 {}->{} {}".format(
            device_id, self.layer2.mac_id, raw_packet))
        self.process_received_packet(device_id, BitBuffer(raw_packet))

    def process_received_packet(self, remote_id, packet_bbuf):
        # remote_id needs to bind into a single context in order to map
        # the packet into a procedure for SCHC fragment, SCHC packet.
        # or raw IP packet.
# XXX
# For now, a context and rules are merged.  It needs to be separated.
# XXX
        rule = self.rule_manager.findRuleByPacket(remote_id, packet_bbuf)
        if rule is None:
            self._log("no rule found for {}".format(remote_id))
            args = (remote_id, self.layer2.mac_id, packet_bbuf.get_content())
            self.scheduler.add_event(0, self.layer3.receive_packet, args)
            return
        # if it is a SCHC fragment or a SCHC packet,
        # the context must exist, which indicates a size of the rule id.

        if "fragmentation" in rule:
            # SCHC R.
            # find the session for the dtag.
            if rule["dtagSize"] > 0:
                dtag = packet_bbuf.get_bits(rule.get("dtagSize"),
                                    position=rule.get("ruleLength"))
            else:
                dtag = None
            session = self.fragment_session_list.get(dtag)
            # if not exist, new session will be created.
            if session is None:
                session = self.new_reassemble_session(packet_bbuf,
                                                      rule, remote_id)
                self.fragment_session_list[dtag] = session
            # call resembling process according to the mode.
            # once resembling is finished, self.proccess_packet() will be
            # called again for decompression.
            session.process_packet(packet_bbuf, dtag)
            return

        if "compression" in rule:
            # SCHC D.
            packet_bbuf = self.compression.decompress(packet_bbuf)
            args = (remote_id, self.layer2.mac_id, raw_packet)
            self.scheduler.add_event(0, self.layer3.receive_packet, args)
            return

        raise RuntimeError("must not come here.")

# ---------------------------------------------------------------------------
