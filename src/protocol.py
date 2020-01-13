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


class Session:
    """ fragmentation/reassembly session manager
    session = [
        { "ruleID": n, "ruleLength", "dtag": n, "session": session }, ...
        ]
    """

    def __init__(self, protocol):
        self.protocol = protocol
        self.session_list = []

    def add(self, rule_id, rule_id_size, dtag, session):
        if self.get(rule_id, rule_id_size, dtag) is not None:
            dprint("ERROR: the session rid={}/{} dtag={} exists already".format(
                rule_id, rule_id_size, dtag))
            return False
        self.session_list.append({"rule_id": rule_id,
                                  "rule_id_size": rule_id_size, "dtag": dtag,
                                  "session": session})
        return True

    def get(self, rule_id, rule_id_size, dtag):
        for i in self.session_list:
            if (rule_id == i["rule_id"] and
                    rule_id_size == i["rule_id_size"] and dtag == i["dtag"]):
                return i["session"]
        return None


    def get_state(self, **kw):
        result = []
        for session in self.session_list:
            session_state = session.copy()
            session_state["session"] = session["session"].get_state(**kw)
            result.append(session_state)
        return result


class debug_protocol:
    def _log(*arg):
        dprint(*arg)


class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)

    """

    def __init__(self, config, system, layer2, layer3, role):
        assert role in ["device", "core"]
        self.config = config
        self.system = system
        self.role = role
        self.scheduler = system.get_scheduler()
        self.layer2 = layer2
        self.layer3 = layer3
        self.layer2._set_protocol(self)
        self.layer3._set_protocol(self)
        self.compressor = Compressor(self)
        self.decompressor = Decompressor(self)
        self.fragment_session = Session(self)
        self.reassemble_session = Session(self)
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

    def schc_send(self, dst_L3addr, raw_packet, direction="UP"):
        self._log("recv-from-L3 -> {} {}".format(dst_L3addr, raw_packet))
        context = self.rule_manager.find_context_bydstiid(dst_L3addr)
        dprint("raw_packet in schc_send", raw_packet)
        if direction in ["UP", "up"]:
            t_dir = T_DIR_UP
        elif direction in ["DOWN", "down", "DW", "dw"]:
            t_dir = T_DIR_DW
        else:
            raise ValueError("direction must be UP or DOWN, but {}"
                             .format(direction))

        P = Parser(debug_protocol)
        parsed_packet = P.parse(raw_packet, t_dir)
        dpprint(parsed_packet)

        try:
            parsed_packet = P.parse(raw_packet, T_DIR_UP)
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
            packet_bbuf = BitBuffer(raw_packet)
        else:
            packet_bbuf = schc_packet

        # check if fragmentation is needed.
        if packet_bbuf.count_added_bits() < self.layer2.get_mtu_size():
            self._log("SCHC fragmentation is not needed. size={}".format(
                packet_bbuf.count_added_bits()))
            """ Changement à corriger
            args = (packet_bbuf.get_content(), context["devL2Addr"])
            """
            args = (packet_bbuf.get_content(), "*")
            self.scheduler.add_event(0, self.layer2.send_packet, args)
            return

        # fragmentation is required.
        lower_addr = self.layer2.get_address()
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
        session = self.new_fragment_session(context, rule)
        session.set_packet(packet_bbuf)
        self.fragment_session.add(rule[T_RULEID], rule[T_RULEIDLENGTH],
                                  session.dtag, session)
        session.start_sending()

    def new_fragment_session(self, context, rule):
        mode = rule[T_FRAG][T_FRAG_MODE]
        if mode == "noAck":
            session = FragmentNoAck(self, context, rule)  # XXX
        elif mode == "ackAlways": #XXX
            raise NotImplementedError(
                "{} is not implemented yet.".format(mode))
        elif mode == "ackOnError":
            session = FragmentAckOnError(self, context, rule)  # XXX
        else:
            raise ValueError("invalid FRMode: {}".format(mode))
        return session

    def new_reassemble_session(self, context, rule, dtag, dev_L2addr):
        mode = rule[T_FRAG][T_FRAG_MODE]
        if mode == "noAck":
            session = ReassemblerNoAck(self, context, rule, dtag, dev_L2addr)
        elif mode == "ackAlways":
            raise NotImplementedError("FRMode:", mode)
        elif mode == "ackOnError":
            session = ReassemblerAckOnError(self, context, rule, dtag,
                                            dev_L2addr)
        else:
            raise ValueError("FRMode:", mode)
        return session

    def schc_recv(self, dev_L2addr, raw_packet):
        # self._log("recv-from-L2 {} {}".format(dev_L2addr, raw_packet))
        frag_rule = self.rule_manager.FindFragmentationRule(dev_L2addr)

        # dprint(dev_L2addr)
        packet_bbuf = BitBuffer(raw_packet)
        # dprint("raw_packet", raw_packet)
        # dprint("schc packet", packet_bbuf)
        # dprint("frag_rule", frag_rule)

        # !IMPORTANT: This condition has to be changed by a context condition like in the last version

        dtrace('>', binascii.hexlify(packet_bbuf.get_content()), ' ')
        dtrace ('\t\t\t-----------{:3}--------->|'.format(len(packet_bbuf._content)))

        if dev_L2addr == b"\xaa\xbb\xcc\xee":

            if frag_rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG] > 0:
                dtag = packet_bbuf.get_bits(frag_rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG],
                                            position=frag_rule[T_RULEIDLENGTH])
            else:
                dtag = None

            # find existing session for fragment or reassembly.
            session = self.reassemble_session.get(frag_rule[T_RULEID], frag_rule[T_RULEIDLENGTH], dtag)
            if session is not None:
                dprint("Reassembly session found", session.__class__.__name__)
            else:
                # no session is found.  create a new reassemble session.
                context = None
                session = self.new_reassemble_session(context, frag_rule, dtag,
                                                      dev_L2addr)
                self.reassemble_session.add(frag_rule[T_RULEID], frag_rule[T_RULEIDLENGTH],
                                            dtag, session)
                dprint("New reassembly session created", session.__class__.__name__)
            session.receive_frag(packet_bbuf, dtag)
            return

            self.process_decompress(packet_bbuf, dev_L2addr, direction=T_DIR_UP)

        elif dev_L2addr == b"\xaa\xbb\xcc\xdd":
            if frag_rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG] > 0:
                dtag = packet_bbuf.get_bits(frag_rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG],
                                            position=frag_rule[T_RULEIDLENGTH])
            else:
                dtag = None
            # find existing session for fragment or reassembly.
            session = self.fragment_session.get(frag_rule[T_RULEID], frag_rule[T_RULEIDLENGTH], dtag)
            dprint("rule.ruleID -> {},rule.ruleLength-> {}, dtag -> {}".format(frag_rule[T_RULEID],
                                                                              frag_rule[T_RULEIDLENGTH], dtag))
            if session is not None:
                dprint("Fragmentation session found", session)
                session.receive_frag(packet_bbuf, dtag)
            else:
                dprint("context exists, but no {} session for this packet {}".
                      format(dev_L2addr))
            return

        else:
            raise RuntimeError("Not implemented properly", dev_L2addr)

    # def schc_recv(self, dev_L2addr, raw_packet):
    #     self._log("recv-from-L2 {} {}".format(dev_L2addr, raw_packet))
    #     # find context for the SCHC processing.
    #     # XXX
    #     # the receiver never knows if the packet from the device having the L2
    #     # addrss is encoded in SCHC.  Therefore, it has to search the db with
    #     # the field value of the packet.
    #     context = self.rule_manager.find_context_bydevL2addr(dev_L2addr)
    #     if context is None:
    #         # reject it.
    #         self._log("Rejected. Not for SCHC packet, sender L2addr={}".format(
    #                 dev_L2addr))
    #         return
    #     # find a rule in the context for this packet.
    #     packet_bbuf = BitBuffer(raw_packet)
    #     key, rule = self.rule_manager.find_rule_bypacket(context, packet_bbuf)
    #     if key == "fragSender":
    #         if rule["dtagSize"] > 0:
    #             dtag = packet_bbuf.get_bits(rule.get("dtagSize"),
    #                                 position=rule.get("ruleLength"))
    #         else:
    #             dtag = None
    #         # find existing session for fragment or reassembly.
    #         session = self.fragment_session.get(rule.ruleID,
    #                                             rule.ruleLength, dtag)
    #         if session is not None:
    #             dprint("Fragmentation session found", session)
    #             session.receive_frag(packet_bbuf, dtag)
    #         else:
    #             dprint("context exists, but no {} session for this packet {}".
    #                     format(key, dev_L2addr))
    #     elif key == "fragReceiver":
    #         if rule["dtagSize"] > 0:
    #             dtag = packet_bbuf.get_bits(rule.get("dtagSize"),
    #                                 position=rule.get("ruleLength"))
    #         else:
    #             dtag = None
    #         # find existing session for fragment or reassembly.
    #         session = self.reassemble_session.get(rule.ruleID,
    #                                             rule.ruleLength, dtag)
    #         if session is not None:
    #             dprint("Reassembly session found", session)
    #         else:
    #             # no session is found.  create a new reassemble session.
    #             session = self.new_reassemble_session(context, rule, dtag,
    #                                                   dev_L2addr)
    #             self.reassemble_session.add(rule.ruleID, rule.ruleLength,
    #                                         dtag, session)
    #             dprint("New reassembly session created", session)
    #         session.receive_frag(packet_bbuf, dtag)
    #     elif key == "comp":
    #         # if there is no reassemble rule, process_decompress() is directly
    #         # called from here.  Otherwise, it will be called from a reassemble
    #         # function().
    #         self.process_decompress(context, dev_L2addr, packet_bbuf)
    #     elif key is None:
    #         raise ValueError(
    #                 "context exists, but no rule found for L2Addr {}".
    #                 format(dev_L2addr))
    #     else:
    #         raise SystemError("should not come here.")

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
            "role": self.role
        }
        result["rule-manager"] = self.rule_manager.get_init_info(**kw)
        return result
