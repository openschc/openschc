"""
.. module:: frag_send
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------
import math

from gen_base_import import *  # used for now for differing modules in py/upy
from gen_utils import dprint, dtrace

import protocol
import frag_msg
from frag_tile import TileList
from frag_bitmap import make_bit_list

try:
    import utime as time
except ImportError:
    import time

enable_statsct = True
if enable_statsct:
    from stats.statsct import Statsct

from compr_core import *
#---------------------------------------------------------------------------

max_ack_requests = 8

class FragmentBase():
    def __init__(self, rule, mtu_in_bytes, protocol=None, context=None, dtag=None, fecrule = None):
        self.protocol = protocol
        self.context = context
        self.rule = rule
        self.mtu = 60
        self.l2word = 8 # self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE]
        self.dtag = dtag

        if fecrule:
            self.fecrule = fecrule[0]
            self.fec_enabled = True
            self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN] = math.ceil(math.log2(self.fecrule[T_FRAG_FEC][T_FRAG_FEC_XORFRAGS] + 1)) # black magic here but it works
            self.fecrule["Fragmentation"] = rule["Fragmentation"]           #recopie dans fecrule des parametres de la regle rule
            self.xorFrags = self.fecrule[T_FRAG_FEC][T_FRAG_FEC_XORFRAGS]
            self.circular_buffer = []
            self.fragment_counter = 0 
            self.fcn_counter = (2**self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])-2
            self.xor_buffer = 0
            self.fcn_for_fec = self.fcn_counter
            self.save_nxt_fcn = False

            #print(self.fecrule)
        else:
            self.fec_enabled = False

        # self.mic is used to check whether All-1 has been sent or not.
        self.mic_sent = None
        self.event_id_ack_wait_timer = None
        self.ack_wait_timer = 150
        self.ack_requests_counter = 0
        self.resend = False
        self.all1_send = False
        self.number_tiles_send = 0
        self.all_tiles = None
        self.state = "START"
        self.ACK_SUCCESS = "ACK_SUCCESS"
        self.ACK_FAILURE = "ACK_FAILURE"
        self.RECEIVER_ABORT = "RECEIVER_ABORT"
        self.SEND_ALL_1 = "SEND_ALL_1"
        self.WAITING_FOR_ACK = "WAITING_FOR_ACK"
        self.ACK_TIMEOUT = "ACK_TIMEOUT"
        self.schc_all_1 = None
        self.last_window_tiles = None
        self.num_of_windows = 0
        self.number_of_ack_waits = 0
        self.sender_abort_sent = False
        self.last_send_time = None
        self.verbose = None

    def set_packet(self, packet_bbuf):
        """ store the packet of bitbuffer for later use,
        return dtag for the packet """
        #packet_bbuf.display()
        self.packet_bbuf = packet_bbuf.copy()
        self.mic_base = packet_bbuf.copy()
        # XXX:remove - dtag management is in protocol.py:
        ## update dtag for next
        #self.dtag += 1
        #if self.dtag > frag_msg.get_max_dtag(self.rule):
        #    self.dtag = 0

    def get_mic(self, mic_base, last_frag_base_size,
                penultimate_size=0):
        assert isinstance(mic_base, BitBuffer)

        # calculate the significant padding bits.
        # 1. get the extra bits.
        #
        #   |<------------ last SCHC frag ------------->|
        #   |<- header ->|<- payload ->|<--- padding -->|
        #   |<---- frag base size ---->|<- extra bits-->|
        #                                      L2Word ->|

        extra_bits = (frag_msg.roundup(last_frag_base_size, self.l2word) -
                        last_frag_base_size)

        # 2. round up the payload of all SCHC fragments
        #    to the MIC word size.
        #
        #   |<----------------- input data  ----------------->|
        #   |<- a SCHC packet ->|<- extra bits->|<- padding ->|
        #            MIC Word ->|                  MIC Word ->|
        mic_base.add_bits(0, extra_bits)
        # XXX
        if penultimate_size != 0:
            extra_bits = (frag_msg.roundup(penultimate_size, self.l2word) -
                            penultimate_size)
            mic_base.add_bits(0, frag_msg.roundup(extra_bits,
                                                self.rule[T_FRAG][T_FRAG_PROF ][T_FRAG_MIC]))
        #
        mic = get_mic(mic_base.get_content()).to_bytes(4, "big")
        dprint("Send MIC {}, base = {}, lenght = {}".format(mic.hex(), mic_base.get_content(), len(mic_base.get_content())))
        return mic

    def start_sending(self):
        self.send_frag()

    def send_frag(self):
        raise NotImplementedError("it is implemented at the subclass.")

    def get_session_type(self):
        return "fragmentation"

    def get_state_info(self, **kw):
        return "<fragmentation session>"

    def send_sender_abort(self):
        """ Starting to send SCHC Sender-Abort after called by Application."""

        """ This function can also be used to send Sender-Abort messages from upper layer
        """
        #, core_id=None, device_id=None, direction=T_DIR_UP
        # First we look for the ongoing fragmentation sessions, then we create the 
        # schc abort

        if self.sender_abort_sent == False:
            schc_frag = frag_msg.frag_sender_tx_abort(self.rule, self.dtag)  
            # Send a SCHC Sender Abort
            if self.protocol.position == T_POSITION_DEVICE:
                dest = self._session_id[0] # core address
            else:
                dest = self._session_id[1] # device address
            args = (schc_frag.packet.get_content(), dest) 
            dprint("MESSSAGE TYPE ----> Sent Sender-Abort.", schc_frag.__dict__)
            if enable_statsct:
                Statsct.set_msg_type("SCHC_SENDER_ABORT")
                Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))
            self.protocol.scheduler.cancel_session(self._session_id) # Cancel previous events of this session
            self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet, args, session_id = self._session_id)
            self.sender_abort_sent = True
            self.protocol.session_manager.delete_session(self._session_id)

        return self.sender_abort_sent

#-------------------------------------- FEC UTILITIES

    def pad_bytearrays_to_max_length(self, data: list[bytearray]) -> list[bytearray]:
        max_len = max(len(b) for b in data)
        return [bytearray([0x00] * (max_len - len(b)) + list(b)) for b in data] # on pad (0 a gauche), si necessaire, tous les fragments < au plus long fragment

    def get_xor_bytearray(self, arr):
        if not arr:
            return bytearray()

        length = len(arr[0])            #deja paddé donc forcement taille max
        result = bytearray(length)

        for barr in arr:
            for i in range(length):
                result[i] ^= barr[i]
                
        return result

#-------------------------------------- 

class FragmentNoAck(FragmentBase):

# 8.4.1.  No-ACK mode
#
#    fragmentation and the entity performing reassembly.  This mode
#    supports LPWAN technologies that have a variable MTU.
#
#    In No-ACK mode, only the All-1 SCHC Fragment is padded as needed.
#    The other SCHC Fragments are intrinsically aligned to L2 Words.
#
# 8.4.1.1.  Sender behavior
#
#    Each SCHC Fragment MUST contain exactly one tile in its Payload.  The
#    tile MUST be at least the size of an L2 Word.  The sender MUST
#    transmit the SCHC Fragments messages in the order that the tiles
#    appear in the SCHC Packet.  Except for the last tile of a SCHC
#    Packet, each tile MUST be of a size that complements the SCHC
#    Fragment Header so that the SCHC Fragment is a multiple of L2 Words
#    without the need for padding bits.  Except for the last one, the SCHC
#    Fragments MUST use the Regular SCHC Fragment format specified in
#    Section 8.3.1.1.  The last SCHC Fragment MUST use the All-1 format
#    specified in Section 8.3.1.2.
    
            
    def set_packet(self, packet_bbuf):
        super().set_packet(packet_bbuf)
        # because draft-18 requires that in No-ACK mode, each fragment must
        # contain exactly one tile and the tile size must be at least the size
        # of an L2 Word.
        #print(self.rule)
        min_size = (frag_msg.get_sender_header_size(self.rule) +
                        frag_msg.get_mic_size(self.rule) + self.l2word)   
        #print ('MTU = ', self.protocol.connectivity_manager.get_mtu("toto"), min_size)

        if self.mtu < min_size:
           print("toto")
           raise ValueError("the MTU={} is not enough to carry the SCHC fragment of No-ACK mode={}".format(self.mtu, min_size))

    def send_frag(self):
        # XXX
        # because No-ACK mode supports variable MTU,
        # sender can't know the fact that it can't send all fragments
        # before it reachs to send the last fragment (All-1).
        #
        #     The All-1 fragment MUST be formed like below.
        #
        #     | header | MIC |    last tile     |
        #                    |<- L2 word size ->|
        #                                       |<- L2 Word
        #
        #     if the size of header+MIC+tile doesn't fit the L2 Word,
        #
        #     | header | MIC |     last tile    |    padding    |
        #                    |<- L2 word size ->|<- less than ->|
        #                                         L2 word size
        #                                                       |<- L2 Word
        mtu = self.protocol.connectivity_manager.get_mtu("toto")
        mtu = self.protocol.layer2.get_mtu_size()
        fcn_size = self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN]
        flag_fec = False

        payload_size = (mtu - frag_msg.get_sender_header_size(self.rule))
        remaining_data_size = self.packet_bbuf.count_remaining_bits()
        if remaining_data_size >= payload_size:
            #dprint("----------------------- Fragmentation process -----------------------")
            # put remaining_size of bits of packet into the tile.
            tile = self.packet_bbuf.get_bits_as_buffer(payload_size)

            transmit_callback = None
            self.protocol.scheduler.add_event(0, self.event_sent_frag, ())
            if fcn_size == 1:           #ALL-0
                fcn = 0
            else:                       #pour FCNSize > 1
                fcn = self.fcn_counter
                if(self.fcn_counter==0):        # valeur pour le prochain fragment
                    self.fcn_counter=(2**self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])-2
                else:
                    self.fcn_counter-=1

            self.mic_sent = None

            if enable_statsct:
                Statsct.set_msg_type("SCHC_FRAG")
                Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))
        elif remaining_data_size < payload_size:
            #dprint("----------------------- Fragmentation process -----------------------")
            if remaining_data_size <= (
                    payload_size - frag_msg.get_mic_size(self.rule)):
                tile = None
                if remaining_data_size > 0:
                    tile = self.packet_bbuf.get_bits_as_buffer()
                # make All-1 frag.
                assert self.mic_sent is None
                last_frag_base_size = 0
                if tile is not None:
                    last_frag_base_size += (
                            frag_msg.get_sender_header_size(self.rule) +
                            frag_msg.get_mic_size(self.rule) +
                            remaining_data_size)
                self.mic_sent = self.get_mic(self.mic_base, last_frag_base_size)
                self.protocol.session_manager.delete_session(self._session_id)
                #print('MIC Size = ', frag_msg.get_mic_size(self.rule))
                fcn = frag_msg.get_fcn_all_1(self.rule)
                if enable_statsct:
                    Statsct.set_msg_type("SCHC_ALL_1 ")
                    Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule) +
                                            frag_msg.get_mic_size(self.rule))
            else:
                # put the size of the complements of the header to L2 Word.
                tile_size = (remaining_data_size -
                             (frag_msg.get_sender_header_size(self.rule) +
                              remaining_data_size) % self.l2word)
                tile = self.packet_bbuf.get_bits_as_buffer(tile_size)
                self.protocol.scheduler.add_event(0, self.event_sent_frag, ())

                if fcn_size == 1:           #ALL-0
                    fcn = 0
                else:
                    fcn = self.fcn_counter
                    if(self.fcn_counter==0):
                        self.fcn_counter=(2**self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])-2
                    else:
                        self.fcn_counter-=1

                self.mic_sent = None
                if enable_statsct:
                    Statsct.set_msg_type("SCHC_FRAG")
                    Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))

        schc_frag = frag_msg.frag_sender_tx(
            self.rule, dtag=self.dtag,
            win=None,
            fcn=fcn,
            mic=self.mic_sent,
            payload=tile)
        
        if self.fec_enabled and self.save_nxt_fcn:      # on garde en mémoire le fcn du premier fragment de la "window", qui sera plus tard le fcn du frag FEC
            self.fcn_for_fec = schc_frag.fcn
            self.save_nxt_fcn = False

        if self.fec_enabled:
            if tile is not None and (0 <= self.fragment_counter <= self.xorFrags):      #sauvegarde de la payload
                self.circular_buffer.append(tile.get_content())         # get content pour ne pas avoir le /xxx, pour le calcul du xor

            self.fragment_counter += 1      #on pourrait directement verifier le nb d'element dans le buffer plutot que davoir un compteur

            if(self.fragment_counter >= self.xorFrags):
                padded_fecbuffer = self.pad_bytearrays_to_max_length(self.circular_buffer)  # on pad tous les elem par rapport a la taille de l'elem max(len())
                self.circular_buffer.clear()                                                # reset le circular pour le prochain cycle xorfrag
                self.xor_buffer = BitBuffer(self.get_xor_bytearray(padded_fecbuffer))       # Xor de tous les frag paddés, attention au suffixe /xxx (selon alex cest bon)
                flag_fec = True
                self.fragment_counter = 0
                self.save_nxt_fcn = True

        # send a SCHC fragment
        if self.protocol.position == T_POSITION_DEVICE:
            dest = self._session_id[0] # core address
        else:
            dest = self._session_id[1] # device address

        args = (schc_frag.packet.get_content(), dest)
        #dprint ("dbug: frag_send.py: Fragment args", args)
        #dprint("frag sent:", schc_frag.__dict__)
    
        if self.verbose:
            if self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] == 0:
                w_dtag = '-'
            else:
                w_dtag = schc_frag.dtag

            if self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] == 0:
                w_w = '-'
            else:
                w_w = schc_frag.win

            all1 = 2**self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN]-1
            if schc_frag.fcn == all1:
                w_fcn = "All-1"
            elif schc_frag.fcn == 0:
                w_fcn = "All-0"
            else:
                w_fcn = schc_frag.fcn

            if self.protocol.position == T_POSITION_CORE:
                print ("<--{:3}--| r:{}/{} (noA) DTAG={} W={} FCN={}  ".format(
                    len(schc_frag.packet._content),
                    self.rule[T_RULEID],
                    self.rule[T_RULEIDLENGTH],
                    w_dtag,
                    w_w,
                    w_fcn
                    ))
            elif self.protocol.position == T_POSITION_DEVICE:
                print ("r:{}/{} (noA) DTAG={} W={} FCN={}  |--{:3}-->".format(
                    self.rule[T_RULEID],
                    self.rule[T_RULEIDLENGTH],
                    w_dtag,
                    w_w,
                    w_fcn,
                    len(schc_frag.packet._content)
                    ))
            else:
                print("Unknown position to display frag")

        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args, session_id = self._session_id) # Add session_id

        if self.fec_enabled and flag_fec:           #envoi du fragment FEC sur le canal
            
            fec_frag = frag_msg.frag_sender_tx(
                self.fecrule, dtag=self.dtag,
                win=None,
                fcn=self.fcn_for_fec,
                mic=self.mic_sent,
                payload=self.xor_buffer)
                
            if self.protocol.position == T_POSITION_DEVICE:
                dest = self._session_id[0] # core address
            else:
                dest = self._session_id[1] # device address

            args = (fec_frag.packet.get_content(), dest)

            if self.verbose:
                if self.fecrule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] == 0:
                    w_dtag = '-'
                else:
                    w_dtag = fec_frag.dtag

                if self.fecrule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] == 0:
                    w_w = '-'
                else:
                    w_w = fec_frag.win

                all1 = 2**self.fecrule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN]-1
                if fec_frag.fcn == all1:
                    w_fcn = "All-1"
                elif fec_frag.fcn == 0:
                    w_fcn = "All-0"
                else:
                    w_fcn = fec_frag.fcn

                if self.protocol.position == T_POSITION_CORE:
                    print ("<--{:3}--| r:{}/{} (noA) DTAG={} W={} FCN={}  ".format(
                        len(fec_frag.packet._content),
                        self.fecrule[T_RULEID],
                        self.fecrule[T_RULEIDLENGTH],
                        w_dtag,
                        w_w,
                        w_fcn
                        ))
                elif self.protocol.position == T_POSITION_DEVICE:
                    print ("r:{}/{} (noA) DTAG={} W={} FCN={}  |--{:3}--> FEC FRAG".format(
                        self.fecrule[T_RULEID],
                        self.fecrule[T_RULEIDLENGTH],
                        w_dtag,
                        w_w,
                        w_fcn,
                        len(fec_frag.packet._content)
                        ))
                else:
                    print("Unknown position to display frag")

            self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                    args, session_id = self._session_id) # Add session_id
            
            flag_fec = False

    def event_sent_frag(self, status=0): # status == nb actually sent (for now)
        #print("event_sent_frag")
        # delay = 10 #self.protocol.config.get("tx_interval", 0)
        delay = self.protocol.config.get("tx_interval", 0)
        self.protocol.scheduler.add_event(delay, self.send_frag, {})

    def receive_frag(self, bbuf, dtag, protocol, core_id=None, device_id=None):

        schc_frag = frag_msg.frag_sender_rx(self.rule, bbuf)     
        # in No-Ack mode, only Receiver Abort message can be acceptable.
        print("sender frag received:", schc_frag.__dict__)
        if ((self.rule[T_FRAG][T_FRAG_PROF ][T_FRAG_W_SIZE] == 0 or
             schc_frag.win == frag_msg.get_win_all_1(self.rule)) and
            schc_frag.cbit == 1 and schc_frag.remaining.allones() == True):
            dprint("Receiver Abort rid={} dtag={}".format(
                    self.rule.ruleID, self.dtag))
            return
        else:
            dprint("XXX Unacceptable message has been received.")

    def get_state(self, **kw):
        result = {
            "type": "no-ack",
            "state": "XXX - need to be added"
        }
        return result


#---------------------------------------------------------------------------

class FragmentAckOnError(FragmentBase):

    def set_packet(self, packet_bbuf):
        super().set_packet(packet_bbuf)
        self.all_tiles = TileList(self.rule, packet_bbuf, self.l2word)
        # XXX
        # check whether the size of the last tile is less than L2 word
        # AND the tile number is zero
        # because draft-17 doesn't specify how to handle it.
        a = self.all_tiles.get_all_tiles()

        if (a[-1]["t-num"] == 0 and
            a[-1]["tile"].count_added_bits() < self.l2word):
            raise ValueError("The size {} of the last tile with the tile number 0 must be equal to or greater than L2 word size {}.".format(a[-1]["tile"].count_added_bits(), self.l2word))
        # make the bitmap
        #self.bit_list = make_bit_list(self.all_tiles.get_all_tiles(),
        #                              self.rule["FCNSize"],
        #                              frag_msg.get_fcn_all_1(self.rule))
        print("----------------------- Fragmentation process -----------------------")
        self.bit_list = make_bit_list(self.all_tiles.get_all_tiles(),
                                      self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                                      self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE])
        #dprint("bit_list:", self.bit_list)
        #for tile in self.all_tiles.get_all_tiles():
            #dprint("w: {}, t: {}, sent: {}".format(tile['w-num'],tile['t-num'],tile['sent']))
        self.all1_send = False
        self.num_of_windows = 0
        for pos in self.bit_list:
            #dprint("bitmap: {}, length:{}".format(self.bit_list[pos], len(self.bit_list[pos])))
            if len(self.bit_list[pos]) != 0:
                self.num_of_windows += 1
        dprint("frag_send.py, Number of windows = {}".format(self.num_of_windows))
        #input("")


    def send_frag(self):
        if self.state == self.ACK_SUCCESS:
            dprint("-----------------------------------------------------------------------")
            return
        dprint("----------------------- Preparing to send a message -----------------------")
        scheduler = self.protocol.system.get_scheduler()
        #dprint("{} send_frag!!!!!!!!!!!!!!!!!".format(scheduler.get_clock()))  # utime.time()
        dprint("all1_send-> {}, resend -> {}, state -> {}".format(self.all1_send, self.resend, self.state))
        #dprint("all tiles unsend -> {}".format(self.all_tiles.get_all_tiles()))
        #for tile in self.all_tiles.get_all_tiles():
            #dprint("w: {}, t: {}, sent: {}".format(tile['w-num'], tile['t-num'], tile['sent']))
        #dprint("")
        # if self.state == self.ACK_FAILURE and self.num_of_windows != 1 and self.number_of_ack_waits <= self.num_of_windows:
        #     #waiting for the acks of the others windows
        #     self.number_of_ack_waits += 1 #wait depends on the number of windows
        #     #set ack_time_out_timer
        #     dprint("waiting for more acks: {}".format(self.number_of_ack_waits))
        #     return

        # get contiguous tiles as many as possible fit in MTU.
        # mtu_size = self.protocol.layer2.get_mtu_size()
        mtu_size = self.protocol.connectivity_manager.get_mtu("toto")
        print ("MTU at frag_send.py = ", mtu_size) 
        window_tiles, nb_remaining_tiles, remaining_size = self.all_tiles.get_tiles(mtu_size)
        #dprint("----window tiles to send: {}, nb_remaining_tiles: {}, remaining_size: {}".format(window_tiles, nb_remaining_tiles, remaining_size))

        if window_tiles is None and self.resend:
            dprint("no more tiles to resend")
            # how to identify that all tiles are resend and that the ack timeout should be set
            # to wait for tha last ok. It should be set after retransmission of the last fragment
            if self.state == self.ACK_FAILURE and self.event_id_ack_wait_timer is None:
                win = self.last_window_tiles[0]["w-num"] if self.last_window_tiles[0]["w-num"] is not None else 0
                if self.last_window_tiles[0]["t-num"] == 0:
                    win += 1
                schc_frag = frag_msg.frag_sender_tx(
                    self.rule, dtag=self.dtag, win=win,
                    fcn=frag_msg.get_fcn_all_1(self.rule),
                    mic=self.mic_sent)
                # set ack waiting timer
                args = (schc_frag, win,)
                self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                    self.ack_wait_timer, self.ack_timeout, args, session_id = self._session_id)
                dprint("*******event id {}".format(self.event_id_ack_wait_timer))
                # if self.all1_send and self.state == self.ACK_FAILURE:
            #     #case when with the bitmap is not possible to identify the missing tile,
            #     #resend ALL-1 messages
            #     # send a SCHC fragment
            #     args = (self.schc_all_1.packet.get_content(), self._session_id[0],
            #     self.event_sent_frag)
            #     dprint("frag sent:", self.schc_all_1.__dict__)
            #     if enable_statsct:
            #         Statsct.set_msg_type("SCHC_ALL_1")
            #         Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule) +
            #             frag_msg.get_mic_size(self.rule))
            #     self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
            #                                     args)
            #     dprint("Sending all-1 beacuse there is an ACK FaILURE but cannot find the missing tiles")
            #     input("")

            # win = self.last_window_tiles[0]["w-num"] if self.last_window_tiles[0]["w-num"] is not None else 0
            # if self.last_window_tiles[0]["t-num"] == 0:
            #     win += 1
            # schc_frag = frag_msg.frag_sender_tx(
            #         self.rule, dtag=self.dtag, win=win,
            #         fcn=frag_msg.get_fcn_all_1(self.rule),
            #         mic=self.mic_sent)
            # set ack waiting timer
            # args = (schc_frag, win,)
            # self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
            #        self.ack_wait_timer, self.ack_timeout, args)
            # dprint("*******event id {}".format(self.event_id_ack_wait_timer))

        # if window_tiles is not None and not self.all1_send and not self.resend:

        if window_tiles is not None:

            dprint("window_tiles is not None -> {}, resend -> {}".format(self.all1_send, self.resend))
            dprint("")
            # even when mic is sent, it comes here in the retransmission.
            if self.all1_send and self.state != self.ACK_FAILURE:
                # when there is a retransmission, the all-1 is send again and is send before
                # the ACK-OK is received. One option is not set the timer after the last
                # retransmission, but i don´t know how to idenfy that all missing fragments
                # have been send. Also the ALL-1 is not retransmisted (dont know if this should
                # be like this. For example, if the ALL-1s is lost, the receiver timer expires
                # and a receiver abort is send. If it arrives, there is not need to retransmit
                # the message after the retransmission of the missing fragments)
                # FIX, all-1 is resend
                dprint('All-1 ones already send')
                # cancel timer when there is success
                # if self.event_id_ack_wait_timer and self.state == self.ACK_SUCCESS:
                #     self.cancel_ack_wait_timer()
                # else:
                #    dprint("how to add a timer without sending a message")
                # fcn = frag_msg.get_fcn_all_1(self.rule)
                # args = (schc_frag, window_tiles[0]["w-num"],)
                # elf.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                # self.ack_wait_timer, self.ack_timeout, args)
                # fcn = frag_msg.get_fcn_all_1(self.rule)
                return
            elif (nb_remaining_tiles == 0 and
                  len(window_tiles) == 1 and
                  remaining_size >= frag_msg.get_mic_size(self.rule)):
                dprint("MESSSAGE TYPE ----> ALL-1 prepared")

                # make the All-1 frag with this tile.
                # the All-1 fragment can carry only one tile of which the size
                # is less than L2 word size.
                fcn = frag_msg.get_fcn_all_1(self.rule)
                last_frag_base_size = (
                        frag_msg.get_sender_header_size(self.rule) +
                        frag_msg.get_mic_size(self.rule) +
                        TileList.get_tile_size(window_tiles))
                # check if mic exists, no need no created again
                if self.mic_sent is None:
                    mic = self.get_mic(self.mic_base, last_frag_base_size)
                    # store the mic in order to know all-1 has been sent.
                    self.mic_sent = mic
                else:
                    mic = self.mic_sent
                dprint("mic_sent -> {}".format(self.mic_sent))
                if enable_statsct:
                    Statsct.set_msg_type("SCHC_ALL_1")
                    Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule) +
                                            frag_msg.get_mic_size(self.rule))
                self.all1_send = True
                self.state = self.SEND_ALL_1
            else:
                dprint("MESSSAGE TYPE ----> regular SCHC frag")
                dprint("")
                # regular fragment.
                fcn = window_tiles[0]["t-num"]
                mic = None

                if enable_statsct:
                    Statsct.set_msg_type("SCHC_FRAG")
                    Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))

            schc_frag = frag_msg.frag_sender_tx(
                self.rule, dtag=self.dtag,
                win=window_tiles[0]["w-num"],
                fcn=fcn,
                mic=mic,
                payload=TileList.concat(window_tiles))

            if mic is not None:
                dprint("mic is not None")
                # set ack waiting timer
                if enable_statsct:
                   Statsct.set_msg_type("SCHC_FRAG")
                   Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))
                args = (schc_frag, window_tiles[0]["w-num"],)
                dprint("all ones")
                self.schc_all_1 = schc_frag
                self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                    self.ack_wait_timer, self.ack_timeout, args, session_id = self._session_id)
                dprint("*******event id {}".format(self.event_id_ack_wait_timer))
            # save the last window tiles.
            self.last_window_tiles = window_tiles
            #dprint("self.last_window_tiles -> {}".format(self.last_window_tiles))
        elif self.mic_sent is not None or self.all1_send:
            dprint("self.mic_sent is not None state -> {}".format(self.state))
            # it looks that all fragments have been sent.
            dprint("----------------------- all tiles have been sent -----------------------",
                  window_tiles, nb_remaining_tiles, remaining_size)
            schc_frag = None
            self.all1_send = True
            if self.event_id_ack_wait_timer and self.state == self.ACK_SUCCESS:
                self.cancel_ack_wait_timer()
            return
        else:
            dprint("only mic all tiles send")
            # Here, only MIC will be sent since all tiles has been sent.
            assert self.last_window_tiles is not None
            # As the MTU would be changed anytime AND the size of the
            # significant padding bits would be changed, therefore the MIC
            # calculation may be needed again.
            # XXX maybe it's better to check whether the size of MTU is change
            # or not when the previous MIC was calculated..
            last_frag_base_size = (frag_msg.get_sender_header_size(self.rule) +
                                   TileList.get_tile_size(self.last_window_tiles))
            self.mic_sent = self.get_mic(self.mic_base, last_frag_base_size)
            # check the win number.
            # XXX if the last tile number is zero, here window number has to be
            # incremented.
            win = self.last_window_tiles[0]["w-num"]
            if self.last_window_tiles[0]["t-num"] == 0:
                win += 1
            schc_frag = frag_msg.frag_sender_tx(
                self.rule, dtag=self.dtag, win=win,
                fcn=frag_msg.get_fcn_all_1(self.rule),
                mic=self.mic_sent)
            # set ack waiting timer
            args = (schc_frag, win,)
            if enable_statsct:
                Statsct.set_msg_type("SCHC_ALL_1")
                Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule) +
                                        frag_msg.get_mic_size(self.rule))
            self.schc_all_1 = schc_frag
            self.state = self.SEND_ALL_1
            self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                self.ack_wait_timer, self.ack_timeout, args, session_id = self._session_id)
            dprint("*******event id {}".format(self.event_id_ack_wait_timer))

        # send a SCHC fragment
        if self.protocol.position == T_POSITION_DEVICE:
            dest = self._session_id[0] # core address
        else:
            dest = self._session_id[1] # device address

        args = (schc_frag.packet.get_content(), dest, self.event_sent_frag)
        dprint ("dbug: frag_send.py: Sending Fragment, args: ", args)
        dprint("frag sent:", schc_frag.__dict__)
        self.last_send_time = time.time()
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet, args, session_id = self._session_id)

    def cancel_ack_wait_timer(self):
        # don't assert here because the receiver sends ACK back anytime.
        #assert self.event_id_ack_wait_timer is not None
        dprint('----------------------- cancel_ack_wait_timer -----------------------')
        self.protocol.scheduler.cancel_event(self.event_id_ack_wait_timer)
        self.event_id_ack_wait_timer = None

    def ack_timeout(self, *args):
        self.cancel_ack_wait_timer()
        dprint("----------------------- ACK timeout -----------------------  ")
        self.state = self.ACK_TIMEOUT
        assert len(args) == 2
        assert isinstance(args[0], frag_msg.frag_sender_tx)
        assert isinstance(args[1], int)
        schc_frag = args[0]
        win = args[1]
        self.ack_requests_counter += 1
        dprint("ack_requests_counter -> {}".format(self.ack_requests_counter))
        if self.ack_requests_counter > max_ack_requests:
            # sending sender abort.
            schc_frag = frag_msg.frag_sender_tx_abort(self.rule, self.dtag)
            if self.protocol.position == T_POSITION_DEVICE:
                dest = self._session_id[0] # core address
            else:
                dest = self._session_id[1] # device address
            args = (schc_frag.packet.get_content(), self.dest) 
            dprint("MESSSAGE TYPE ----> Sent Sender-Abort.", schc_frag.__dict__)
            if enable_statsct:
                Statsct.set_msg_type("SCHC_SENDER_ABORT")
                Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))

            self.protocol.scheduler.add_event(0,
                                        self.protocol.layer2.send_packet, args, session_id = self._session_id)
            return
        # set ack waiting timer
        self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                self.ack_wait_timer, self.ack_timeout, args, session_id = self._session_id)
        dprint("*******event id {}".format(self.event_id_ack_wait_timer))
        schc_frag = frag_msg.frag_sender_ack_req(self.rule, self.dtag, win)
        if enable_statsct:
                Statsct.set_msg_type("SCHC_ACK_REQ")
        # # retransmit MIC.
        args = (schc_frag.packet.get_content(), self._session_id[0],
                self.event_sent_frag)

        dprint("MESSSAGE TYPE ----> SCHC ACK REQ frag:", schc_frag.__dict__)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                        args, session_id = self._session_id)
        """ waits for all the acks before sending the ack request

        self.number_of_ack_waits += 1
        dprint("number_of_ack_waits -> {}".format(self.number_of_ack_waits))
        if self.number_of_ack_waits > self.num_of_windows:
            schc_frag = frag_msg.frag_sender_ack_req(self.rule, self.dtag, win)
            if enable_statsct:
                    Statsct.set_msg_type("SCHC_ACK_REQ")
            # # retransmit MIC.
            args = (schc_frag.packet.get_content(), self._session_id[0],
                    self.event_sent_frag)
            dprint("SCHC ACK REQ frag:", schc_frag.__dict__)
            # if enable_statsct:
            #     Statsct.set_msg_type("SCHC_FRAG")
            #     Statsct.set_header_size(frag_msg.get_sender_header_size(self.rule))
            self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                            args)
            self.number_of_ack_waits = 0

        else:
            dprint("Do no send ACK REQ, waiting for more ACKS")        #the idea is that if the ack did not arrive, to send a SCHC ACK REQ
        """

    def event_sent_frag(self, status): # status == nb actually sent (for now)
        dprint("EVENT SEND FRAG")
        self.send_frag()

    def receive_frag(self, bbuf, dtag, protocol, core_id=None, device_id=None, iface=None, verbose=False):
        #receive_frag(self, bbuf, dtag):
        # the ack timer can be cancelled here, because it's been done whether
        # both rule_id and dtag in the fragment are matched to this session
        # at process_received_packet().
        self.cancel_ack_wait_timer() # the timeout is canceled but has to be set
        # when an ack should be received
        self.resend = False
        #
        schc_frag = frag_msg.frag_sender_rx(self.rule, bbuf)
        dprint("-----------------------  Sender Frag Received -----------------------")
        dprint("fragment received -> {}".format(schc_frag.__dict__))
        if ((self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] is None or
            schc_frag.win == frag_msg.get_win_all_1(self.rule)) and
            schc_frag.cbit == 1 and schc_frag.remaining.allones() == True):
            dprint("-----------------------  Receiver Abort rid={} dtag={} -----------------------".format(
                    self.rule[T_RULEID], self.dtag))
            #self.resend = False
            self.state = self.RECEIVER_ABORT

            return
        if schc_frag.cbit == 1:
            dprint("----------------------- ACK Success rid={} dtag={} -----------------------".format(
                    self.rule[T_RULEID], self.dtag))
            #self.resend = False
            self.state = self.ACK_SUCCESS

            # XXX needs to be reviewed.  at least, no one need this log.
            # try:
            #     f = open("client_server_simulation.txt", "r+")
            # except IOError:
            #     f = open("client_server_simulation.txt", "w+")
            #     f = open("client_server_simulation.txt", "r+")
            # content = f.read()
            # seconds = time. time()
            # f.seek(0, 0)
            # f.write(str(int(seconds)) + '\n' + content)
            # f.close()

            return
        if schc_frag.cbit == 0:
            dprint("----------------------- ACK Failure rid={} dtag={} -----------------------".format(
                    self.rule[T_RULEID], self.dtag))
            #self.resend = False
            #self.all1_send = False
            self.state = self.ACK_FAILURE
            self.resend_frag(schc_frag)
            return

    def resend_frag(self, schc_frag):
        self.resend = True
        dprint("recv bitmap:", (schc_frag.win, schc_frag.bitmap.to_bit_list()))
        dprint("sent bitmap:", (schc_frag.win, self.bit_list[schc_frag.win]))
        self.all_tiles.unset_sent_flag(schc_frag.win,
                                       schc_frag.bitmap.to_bit_list())
        self.send_frag()

    def tiles_send(self):
        for tile in self.all_tiles.get_all_tiles():
            if not tile['sent']:
                self.number_tiles_send += 1
        self.number_tiles_send = math.ceil(self.number_tiles_send / (self.protocol.layer2.get_mtu_size() // self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_TILE]))
        dprint("----------- ", self.number_tiles_send, "tiles to send")

    def current_number_tiles_sent(self):
        if self.number_tiles_send > 0:
            self.number_tiles_send -= 1
        dprint("----------- ", self.number_tiles_send, "tiles to send")
        return self.number_tiles_send

    def get_state(self, **kw):
        result = {
            "type": "ack-on-error",
            "state": self.state,
            "mic-sent": self.mic_sent,
            "resend": self.resend,
            "all1-send": self.all1_send,
            "sent-tiles": self.number_tiles_send,
            "ack-req-counter": self.ack_requests_counter,
            "tiles": self.all_tiles.get_state(**kw),
            "state": "XXX - need to be added"
        }
        return result
