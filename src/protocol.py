"""
.. module:: schc
   :platform: Python, Micropython
"""
# ---------------------------------------------------------------------------

from gen_base_import import *  # used for now for differing modules in py/upy
from gen_utils import dprint, dpprint, set_debug_output

# ---------------------------------------------------------------------------

from frag_recv import ReassemblerAckOnError
from frag_recv import ReassemblerNoAck
from frag_send import FragmentAckOnError
from frag_send import FragmentNoAck
import frag_msg
from compr_parser import *
from compr_core import Compressor, Decompressor

from gen_utils import dtrace
import binascii

# ---------------------------------------------------------------------------

class SessionManager:
    """
    Manage a table of sessions:

    Internals:
       session_table[(l2_address, rule_id, rule_id_size, dtag)]
              -> session
       session_type is "reassembly" or "fragmentation"
    """
    def __init__(self, protocol, unique_peer):
        self.protocol = protocol
        self.unique_peer = unique_peer
        self.session_table = {}

    def find_session(self, session_id):
        session = self.session_table.get(session_id, None)
        return session

    def _add_session(self, session_id, session):
        assert session_id not in self.session_table
        self.session_table[session_id] = session
        
    def create_reassembly_session(self, context, rule, session_id):
        l2_address, rule_id, unused, dtag = session_id
        if self.unique_peer:
            l2_address = None
        mode = rule[T_FRAG][T_FRAG_MODE]
        if mode == "noAck":
            session = ReassemblerNoAck(
                self.protocol, context, rule, dtag, l2_address)
        elif mode == "ackAlways":
            raise NotImplementedError("FRMode:", mode)
        elif mode == "ackOnError":
            session = ReassemblerAckOnError(
                self.protocol, context, rule, dtag, l2_address)
        else:
            raise ValueError("FRMode:", mode)
        self._add_session(session_id, session)
        return session

    def create_fragmentation_session(self, l2_address, context, rule):
        if self.unique_peer:
            l2_address = None

        rule_id = rule[T_RULEID]
        rule_id_length = rule[T_RULEIDLENGTH]
        dtag_length = rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG]
        dtag_limit = 2**dtag_length

        for dtag in range(0, dtag_limit):
            session_id = (l2_address, rule_id, rule_id_length, dtag)
            if session_id not in self.session_table:
                break

        if dtag == dtag_limit:
            self.protocol.log("session", "cannot create session, no dtag available")
            return None

        mode = rule[T_FRAG][T_FRAG_MODE]
        if mode == "noAck":
            session = FragmentNoAck(self.protocol, context, rule)
        elif mode == "ackAlways":
            raise NotImplementedError(
                "{} is not implemented yet.".format(mode))
        elif mode == "ackOnError":
            session = FragmentAckOnError(self.protocol, context, rule)
        else:
            raise ValueError("invalid FRMode: {}".format(mode))
        self._add_session(session_id, session)        
        return session

    def get_state(self, **kw):
        return []

# ---------------------------------------------------------------------------

class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)

    """

    def __init__(self, config, system, layer2, layer3, role, unique_peer):
        assert role in ["device", "core"]
        self.config = config
        self.unique_peer = unique_peer
        self.role = role
        self.system = system
        self.scheduler = system.get_scheduler()
        self.layer2 = layer2
        self.layer3 = layer3
        self.layer2._set_protocol(self)
        self.layer3._set_protocol(self)
        self.compressor = Compressor(self)
        self.decompressor = Decompressor(self)
        self.session_manager = SessionManager(self, unique_peer)
        if hasattr(config, "debug_level"):
            set_debug_output(True)

    def _log(self, message):
        self.log("schc", message)

    def log(self, name, message):
        self.system.log(name, message)

    def set_rulemanager(self, rule_manager):
        self.rule_manager = rule_manager

    def get_system(self):
        return self.system

    def schc_send(self, dst_l2_address, dst_l3_address, raw_packet):
        self._log("recv-from-L3 -> {} {}".format(dst_l3_address, raw_packet))
        context = self.rule_manager.find_context_bydstiid(dst_l3_address)
        dprint("raw_packet in schc_send", raw_packet)
        if self.role == "device":
            t_dir = T_DIR_UP
        else:
            assert self.role == "core"
            t_dir = T_DIR_DW

        P = Parser(self)
        parsed_packet = P.parse(raw_packet, t_dir)
        dpprint(parsed_packet)

        try:
            parsed_packet = P.parse(raw_packet, T_DIR_UP) # XXX: redundant!
            dpprint("parsed_packet[0]", parsed_packet[0])
        except:
            dprint("no parsing, try fragmentation")
            parsed_packet = None
            schc_packet = None

        if parsed_packet is not None:
            # pass        # to be done
            rule = self.rule_manager.FindRuleFromPacket(parsed_packet[0], direction=t_dir)
            if rule is None:
                schc_packet = None
                # reject it.
                # self._log("Rejected. Not for SCHC packet, L4addr={}".format(
                #    dst_L3addr))
                # return
            else:
                if rule["Compression"] != []:
                    dprint(
                        "-------------------------------------- Compression Proccess -------------------------------------------")
                    dprint("selected rule is ", rule)
                    schc_packet = self.compressor.compress(rule, parsed_packet[0], parsed_packet[1], t_dir)
                    dprint(schc_packet)
                    schc_packet.display("bin")
                else:
                    schc_packet = None

        if schc_packet == None:
            packet_bbuf = BitBuffer(raw_packet) # XXX: not putting any SCHC compression header
        else:
            packet_bbuf = schc_packet

        # check if fragmentation is needed.
        if packet_bbuf.count_added_bits() < self.layer2.get_mtu_size():
            self._log("SCHC fragmentation is not needed. size={}".format(
                packet_bbuf.count_added_bits()))
            args = (packet_bbuf.get_content(), dst_l2_address)
            self.scheduler.add_event(0, self.layer2.send_packet, args)
            return

        # fragmentation is required.
        lower_addr = self.layer2.get_address() #XXX: don't find rule based on my address???
        frag_rule = self.rule_manager.FindFragmentationRule(lower_addr)
        if frag_rule is None:
            self._log("Rejected the packet due to no fragmenation rule.")
            return
        # Do fragmenation
        dprint(
            "-------------------------------------- Fragmentation Proccess -------------------------------------------")
        rule = frag_rule
        context = None  # LT: don't know why context is needed, should be self.rule_manager which handle the context
        self._log("fragmentation rule_id={}".format(rule[T_RULEID]))


        session = self.session_manager.create_fragmentation_session(
            dst_l2_address, context, rule)
        # XXX: session can be None
        session.set_packet(packet_bbuf)
        session.start_sending()



    def schc_recv(self, sender_l2_address, raw_packet):
        #self._log("recv-from-L2 {} {}".format(sender_l2_addr, raw_packet))
        frag_rule = self.rule_manager.FindFragmentationRule(sender_l2_address)

        packet_bbuf = BitBuffer(raw_packet)

        dtrace('>', binascii.hexlify(packet_bbuf.get_content()), ' ')
        dtrace ('\t\t\t-----------{:3}--------->|'.format(len(packet_bbuf._content)))

        dtag_length = frag_rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG]
        if dtag_length > 0:
            dtag = packet_bbuf.get_bits(dtag_length, position=frag_rule[T_RULEIDLENGTH])
        else:
            dtag = None # XXX: get_bits(0) should work?

        rule_id = frag_rule[T_RULEID]
        rule_id_length = frag_rule[T_RULEIDLENGTH]
        session_id = (sender_l2_address, rule_id, rule_id_length, dtag)
        session = self.session_manager.find_session(session_id)

        if session is not None:
            dprint("{} session found".format(
                session.get_session_type().capitalize()),
                session.__class__.__name__)
        else:
            context = None
            session = self.session_manager.create_reassembly_session(
                context, frag_rule, session_id)
            dprint("New reassembly session created", session.__class__.__name__)

        session.receive_frag(packet_bbuf, dtag)


    def process_decompress(self, packet_bbuf, dev_L2addr, direction):
        rule = self.rule_manager.FindRuleFromSCHCpacket(packet_bbuf, dev_L2addr)
        if rule is None:
            # reject it.
            self._log("Rejected. Not rule compression for SCHC packet, sender L2addr={}".format(
                dev_L2addr))
            return

        if "Compression" not in rule:
            # reject it.
            self._log("Not compression parameters for SCHC packet, sender L2addr={}".format(
                dev_L2addr))
            return

        if rule["Compression"]:
            dprint("---------------------- Decompression ----------------------")
            dprint("---------------------- Decompression Rule-------------------------")
            self._log("compression rule_id={}".format(rule[T_RULEID]))
            dprint("receiver frag received:", packet_bbuf)
            dprint('rule {}'.format(rule))
            dprint("------------------------ Decompression ---------------------------")
            raw_packet = self.decompressor.decompress(packet_bbuf, rule, direction)
            dprint("---- Decompression result ----")
            dprint(raw_packet)
            args = (dev_L2addr, raw_packet)
            self.scheduler.add_event(0, self.layer3.recv_packet, args)

    # def process_decompress(self, context, dev_L2addr, schc_packet):
    #    self._log("compression rule_id={}".format(context["comp"]["ruleID"]))
    #    raw_packet = self.decompressor.decompress(context, schc_packet)
    #    args = (dev_L2addr, raw_packet)
    #    self.scheduler.add_event(0, self.layer3.recv_packet, args)

    def get_state_info(self, **kw):
        result =  {}
        return result

    def get_init_info(self, **kw):
        result =  {
            "role": self.role,
            "unique-peer": self.unique_peer
        }
        result["rule-manager"] = self.rule_manager.get_init_info(**kw)
        return result
