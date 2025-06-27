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

class ConnectivityManager:
    """
    This class is aware of the connectivity condition for a device:
    - current MTU
    - error rate
    - duty cycle
    """

    def __init__(self):
        self.mtu = 30

    def get_mtu (self, device):
        """
        Return the MTU is bits for a specific device, currently returns always 500
        """
        return self.mtu

    def set_mtu (self, mtu, device = None):
        """
        Return the MTU is bits for a specific device, currently returns always 500
        """
        self.mtu = mtu
        


# ---------------------------------------------------------------------------

class SessionManager:
    """Maintain the table of active fragmentation/reassembly sessions.

    Internals:
       session_table[(l2_address, rule_id, rule_id_size, dtag)]
              -> session

    When 'unique_peer' is true, the l2_address for another peer is 'None'.
    """
    def __init__(self, protocol, unique_peer):
        self.protocol = protocol
        self.unique_peer = unique_peer
        self.session_table = {}

    def _filter_session_id(self, session_id):
        if self.unique_peer:
            session_id = (None,) + session_id[1:]
        return session_id

    def find_session(self, session_id):
        session_id = self._filter_session_id(session_id)
        session = self.session_table.get(session_id, None)
        dprint("protocol.py, session table: ", self.session_table)
        return session

    def _add_session(self, session_id, session):
        session_id = self._filter_session_id(session_id)        
        assert session_id not in self.session_table
        self.session_table[session_id] = session

    def delete_session(self, session_id):
        self.session_table.pop(session_id)
        #print("SessionManager: deleted", session_id)

    def create_reassembly_session(self, context, rule, session_id): #TODO
        session_id = self._filter_session_id(session_id)  

        core_id, device_id, rule_id, unused, dtag = session_id
        if self.unique_peer:
            l2_address = None #TODO
        mode = rule[T_FRAG][T_FRAG_MODE]
        if mode == T_FRAG_NO_ACK:
            session = ReassemblerNoAck(
                self.protocol, context, rule, dtag, core_id, device_id)
        elif mode == T_FRAG_ACK_ALWAYS:
            raise NotImplementedError("FRMode:", mode)
        elif mode == T_FRAG_ACK_ON_ERROR:
            session = ReassemblerAckOnError(
                self.protocol, context, rule, dtag, core_id, device_id)
        else:
            raise ValueError("FRMode:", mode)
        self._add_session(session_id, session)
        setattr(session, "_session_id", session_id)
        print("protocol.py, create_reassembly_session, session :", session_id)
        print("protocol.py : create_reassembly_session, core_id, device_id", core_id, device_id)
        return session

    def create_fragmentation_session(self, core_id, device_id, context, rule,verbose=None, fecrule = None):
        #print("create frag session: core_id, device_id", core_id, device_id )
        if self.unique_peer:
            l2_address = None #TODO

        rule_id = rule[T_RULEID]
        rule_id_length = rule[T_RULEIDLENGTH]
        dtag_length = rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE]
        dtag_limit = 2**dtag_length

        for dtag in range(0, dtag_limit):
            session_id = (core_id, device_id, rule_id, rule_id_length, dtag)
            session_id = self._filter_session_id(session_id)         
            if session_id not in self.session_table:
                break

        if dtag == dtag_limit:
            self.protocol.log("cannot create session, no dtag available")
            return None
        
        #dprint("protocol.py: creating frag_session with session_id: ", session_id)

        mode = rule[T_FRAG][T_FRAG_MODE]
        #print ('fragmentation mode:' , mode)
        if mode == T_FRAG_NO_ACK:
            if not fecrule:
                session = FragmentNoAck(rule, 12, self.protocol, context, dtag) #TODO : refactor MTU
            else:
                session = FragmentNoAck(rule, 12, self.protocol, context, dtag, fecrule)
        elif mode == T_FRAG_ACK_ALWAYS:
            raise NotImplementedError(
                "{} is not implemented yet.".format(mode))

        elif mode == T_FRAG_ACK_ON_ERROR:
            session = FragmentAckOnError(rule, 12, self.protocol, context, dtag) #TODO : refactor MTU
            # see above for param order
        else:
            raise ValueError("invalid FRMode: {}".format(mode))
        
        session.verbose = verbose

        self._add_session(session_id, session)        
        setattr(session, "_session_id", session_id)
        return session

    def get_state_info(self, **kw):
        return [(session_id, session.get_state_info(**kw))
                for (session_id, session) in self.session_table.items() ]

# ---------------------------------------------------------------------------

class SCHCProtocol:
    """This class is the entry point for the openschc
    (in this current form, object composition is used)

    """


    def __init__(self, layer2=None, system=None, role=None, config={}, tunnel=None, layer3=None,  unique_peer=False, verbose=True):
        assert role in [T_POSITION_CORE, T_POSITION_DEVICE]
        self.config = config
        self.unique_peer = unique_peer
        self.role = role # should be remove for position
        self.position = self.role #position gives if the SCHC is for device or core to define UP and DOWN

        if system:
            self.system = system

        if layer2:
            self.layer2 = layer2 # old stuff to be removed
        else: # use a L2 connectio by default
            import basic_connection
            import socket 

            if tunnel is None:
                self.tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.tunnel.bind(("0.0.0.0", 0x5C4C))
            else:
                self.tunnel = tunnel

            self.layer2 = basic_connection.ScapyLowerLayer(position=role, socket=self.tunnel, other_end=None)
            self.system = basic_connection.ScapySystem()

        self.scheduler = self.system.get_scheduler()


        self.layer2._set_protocol(self)
        self.compressor = Compressor(self)
        self.decompressor = Decompressor(self)
        self.session_manager = SessionManager(self, unique_peer)
        self.verbose = verbose
        self.sender_delay = 0

        self.connectivity_manager = ConnectivityManager()

        if ((isinstance(config, object) and hasattr(config, "debug_level")) or
            (isinstance(config, dict) and config.get("debug_level", 0))):
            set_debug_output(True)

    def _log(self, message):
        if self.verbose:
            print("Protocol", message)

    def log(self, name, message):
        if self.verbose:
            print(name, message)

    def set_rulemanager(self, rule_manager):
        self.rule_manager = rule_manager

    def set_position(self, position):
        assert position in [T_POSITION_DEVICE, T_POSITION_CORE]
        self.position = position

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler

    def set_l2_send_fct(self, fct):
        self.send_layer2 = fct

    def get_system(self):
        return self.system
    
    def get_tunnel(self):
        return self.tunnel

    #CLEANUP remove dst_l3_address
    def _apply_compression(self, device_id, raw_packet, parsing=None, reverse_direction=False, verbose=False):
        """Apply matching compression rule if one exists.
        
        In any case return a SCHC packet (compressed or not) as a BitBuffer
        """
        # Parse packet as IP packet and apply compression rule
        P = Parser(self)
        if self.position == T_POSITION_CORE:
            t_dir = T_DIR_DW
        elif self.position == T_POSITION_DEVICE:
            t_dir = T_DIR_UP
        else:
            raise ValueError ("Unknown position")


        if reverse_direction:
            if t_dir == T_DIR_DW:
                t_dir = T_DIR_UP
            else:
                t_dir = T_DIR_DW 


        if parsing != None:
             parsed_packet, residue, parsing_error = P.parse(raw_packet, t_dir, layers=parsing)
        else: 
             parsed_packet, residue, parsing_error = P.parse(raw_packet, t_dir)
        #self._log("parser {} {} {}".format(parsed_packet, residue, parsing_error))

        if parsed_packet is None:
            print ("schc_send:", parsing_error)
            return BitBuffer(raw_packet), None

        # Apply compression rule


        rule = self.rule_manager.FindRuleFromPacket(parsed_packet, direction=t_dir, failed_field=verbose)
        if rule is None:
            rule = self.rule_manager.FindNoCompressionRule(device_id) # /!\ SHOULD NOT WORK SINCE device_ID is not none

            if rule is None:
                # XXX: not putting any SCHC compression header? - need fix
                if verbose:
                    print("rule for compression/no-compression not found, abort sending.")
                return None, device_id

            if verbose:
                print ("use a no-compression rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))                
            schc_packet = self.compressor.no_compress(rule, raw_packet)
            return schc_packet, device_id

        device_id = rule[T_META][T_DEVICEID]

        if verbose:
            print ("Use compression rule {}/{}".format(rule[T_RULEID], rule[T_RULEIDLENGTH]))
        
        schc_packet = self.compressor.compress(rule, parsed_packet, residue, t_dir, device_id)

        return schc_packet, device_id

    def _make_frag_session(self, core_id, device_id, direction, verbose=None):
        print("make_frag_session, device_id: ", device_id, "core_id", core_id, "direction", direction)
        """Search a fragmentation rule, create a session for it, return None if not found"""
        frag_rule = self.rule_manager.FindFragmentationRule(
                deviceID=device_id, direction=direction)
        
        if frag_rule is None:
            self._log("fragmentation rule not found")
            return None

        fec_rule = []                                   #only if it exists
        for dev in self.rule_manager._ctxt:
            for f in dev["SoR"]:
                    if "ForwardErrorCorrection" in f:
                        fec_rule.append(f)

                    
        if verbose:       
            print("rule_id found :", frag_rule[T_RULEID])
        # Perform fragmentation
        rule = frag_rule
        context = None  # LT: don't know why context is needed, should be self.rule_manager which handle the context
        #self._log("fragmentation rule_id={}".format(rule[T_RULEID]))
        if not fec_rule:
            session = self.session_manager.create_fragmentation_session(
                core_id, device_id, context, rule, verbose=verbose)
        else:
            session = self.session_manager.create_fragmentation_session(
                core_id, device_id, context, rule, verbose=verbose, fecrule= fec_rule)
        if session is None:
            self._log("fragmentation session could not be created") # XXX warning
            return None

        return session

    # CLEANUP: dst_l2 and l3 should be removed
    def schc_send(self, raw_packet, core_id=None, device_id=None, sender_delay=0, parsing=None, verbose=False):
        """Starting to send SCHC packet after called by Application.       
        If self.position is T_POSITION_DEVICE and 
        this function is for sending from device to core.
        TODO: If only compress retun True If Compres and Frag, return context
        """
        #self._log("schc_send {} {}".format(core_id, device_id))

	#, raw_packet))

        #To perform fragmentation, we get the device_id from the rule:
        #Ex: "DeviceID" : "udp:54.37.158.10:8888",

        #Add sender delay if specified by upper layer

        self.sender_delay = sender_delay

        packet_bbuf, device_id = self._apply_compression(device_id, raw_packet, parsing, verbose=verbose)

        if packet_bbuf is None: # No compression rule found
            return

        if self.position == T_POSITION_DEVICE:
            direction = T_DIR_UP
            destination = core_id
        else:
            direction = T_DIR_DW
            destination = device_id

        if verbose:
            print("protocol.py, schc_send, core_id: ", core_id, "device_id: ", device_id, "length in bits", packet_bbuf.count_added_bits() )

        if packet_bbuf == None: # No compression rule found
            return 

        # Start a fragmentation session from rule database
        # Check if fragmentation is needed.
        if packet_bbuf.count_added_bits() < self.connectivity_manager.get_mtu(device_id):
            if verbose:
                print("fragmentation not needed")
            args = (packet_bbuf.get_content(), destination)

            self.scheduler.add_event(0, self.layer2.send_packet, args) # XXX: what about directly send?            
            return 

        frag_session = self._make_frag_session(core_id=core_id, device_id=device_id, direction=direction, verbose=verbose)
        if frag_session is not None:
            frag_session.set_packet(packet_bbuf)
            frag_session.start_sending() 
        
        return frag_session

    def schc_recv(self, schc_packet, core_id=None,  device_id=None, iface=None, verbose=False):
        #dprint ("schc_recv, core_id: " , core_id, "device_id: " , device_id, "position:", self.position)
        """Receiving a SCHC packet from a lower layer."""

        packet_bbuf = BitBuffer(schc_packet)

        rule = self.rule_manager.FindRuleFromSCHCpacket(packet_bbuf, device=device_id)

        if rule == None:
            print ("No rule found")
            return (None, None)

        if T_COMP in rule:
            if self.position == T_POSITION_DEVICE:
                direction = T_DIR_DW
            else:
                direction = T_DIR_UP

            decomp = Decompressor()
            unparser = Unparser()
            header_d = decomp.decompress(schc=packet_bbuf, rule=rule, direction=direction)
            pkt_data = bytearray()
            while (packet_bbuf._wpos - packet_bbuf._rpos) >= 8:
                octet = packet_bbuf.get_bits(nb_bits=8)
                pkt_data.append(octet)

            #print("The HEADER D:", header_d, pkt_data)
            pkt = unparser.unparse(header_d, pkt_data,  direction, rule, iface, verbose)
            return device_id, pkt
        elif T_NO_COMP in rule:
            #remove ruleID
            ruleID = packet_bbuf.get_bits(nb_bits=rule[T_RULEIDLENGTH])
            pkt_data = bytearray()
            while (packet_bbuf._wpos - packet_bbuf._rpos) >= 8:
                octet = packet_bbuf.get_bits(nb_bits=8)
                pkt_data.append(octet)

            return device_id, pkt_data
    

        # fragmentation rule

        frag_rule = rule


        dtag_length = frag_rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE]
        if dtag_length > 0:
            dtag = packet_bbuf.get_bits(dtag_length, position=frag_rule[T_RULEIDLENGTH])
        else:
            dtag = None # XXX: get_bits(0) should work?

        rule_id = frag_rule[T_RULEID]
        rule_id_length = frag_rule[T_RULEIDLENGTH]
        session_id = (core_id, device_id, rule_id, rule_id_length, dtag) 
        #print ("protocol.py: session_id ", session_id)
        session = self.session_manager.find_session(session_id)

        if session is not None:
            #print("{} session found".format(
            #    session.get_session_type().capitalize()),
            #    session.__class__.__name__)
            pass
        else:
            context = None
            session = self.session_manager.create_reassembly_session(
                context, frag_rule, session_id)
            print("New reassembly session created", session.__class__.__name__)

        dprint("core_id, device_id:", core_id , device_id)
        dprint("device or core?", self.role) 

        return session.receive_frag(bbuf=packet_bbuf, 
                                    dtag=dtag, 
                                    protocol=self, 
                                    core_id=core_id, 
                                    device_id=device_id,
                                    iface = iface,
                                    verbose = verbose)

    def decompress_only (self, packet_bbuf, rule, device_id=None, iface=None): # called after reassembly      

        dprint ("debug: protocol.py, decompress_only : ", packet_bbuf, rule, device_id)
        if rule == None:
            print ("No rule found")
            return None
        
        if T_COMP in rule:
            if self.position == T_POSITION_DEVICE:
                direction = T_DIR_DW
                dprint("direction: ", direction)
            else:
                direction = T_DIR_UP
                dprint("direction: ", direction)

            decomp = Decompressor()
            unparser = Unparser()
            header_d = decomp.decompress(schc=packet_bbuf, rule=rule, direction=direction)
            #dprint("header_d:", header_d)
            pkt_data = bytearray()
            while (packet_bbuf._wpos - packet_bbuf._rpos) >= 8:
                octet = packet_bbuf.get_bits(nb_bits=8)
                pkt_data.append(octet)
            pkt = unparser.unparse(header_d, pkt_data,  direction, rule, iface=iface)
            return device_id, pkt


    def process_decompress(self, packet_bbuf, dev_l2_addr, direction):
        rule = self.rule_manager.FindRuleFromSCHCpacket(packet_bbuf, dev_l2_addr)
        if rule is None:
            # reject it.
            self._log("No compression rule for SCHC packet, sender L2addr={}"
                      .format(dev_l2_addr))
            #self.scheduler.add_event(0, self.layer3.recv_packet,
            #                         (dev_l2_addr, packet_bbuf.get_content()))
            return (dev_l2_addr, packet_bbuf.get_content())

        if "Compression" not in rule:
            # reject it.
            self._log("Not compression parameters for SCHC packet, sender L2addr={}".format(
                dev_l2_addr))
            return False

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
            args = (dev_l2_addr, raw_packet)
            # self.scheduler.add_event(0, self.layer3.recv_packet, args)
            return args

    # def process_decompress(self, context, dev_l2_addr, schc_packet):
    #    self._log("compression rule_id={}".format(context["comp"]["ruleID"]))
    #    raw_packet = self.decompressor.decompress(context, schc_packet)
    #    args = (dev_l2_addr, raw_packet)
    #    self.scheduler.add_event(0, self.layer3.recv_packet, args)

    def get_state_info(self, **kw):
        result =  {
            "sessions": self.session_manager.get_state_info(**kw)
        }
        return result

    def get_init_info(self, **kw):
        result =  {
            "role": self.role,
            "unique-peer": self.unique_peer
        }
        result["rule-manager"] = self.rule_manager.get_init_info(**kw)
        return result
