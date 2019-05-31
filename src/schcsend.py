"""
.. module:: schcsend
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg
from schctile import TileList
from schcbitmap import make_bit_list
import utime
enable_statsct = True
if enable_statsct:
    from stats.statsct import Statsct

#---------------------------------------------------------------------------

max_ack_requests = 8

class FragmentBase():
    def __init__(self, protocol, context, rule):
        self.protocol = protocol
        self.context = context
        self.rule = rule
        self.dtag = 0
        # self.mic is used to check whether All-1 has been sent or not.
        self.mic_sent = None
        self.event_id_ack_wait_timer = None
        self.ack_wait_timer = 150   
        self.ack_requests_counter = 0
        self.resend = False
        self.all1_send = False
        self.state = "START"
        self.ACK_SUCCESS = "ACK_SUCCESS"
        self.ACK_FAILURE = "ACK_FAILURE"
        self.RECEIVER_ABORT = "RECEIVER_ABORT"
        self.SEND_ALL_1 = "SEND_ALL_1"
        self.WAITING_FOR_ACK = "WAITING_FOR_ACK"
        self.schc_all_1 = None
        self.last_window_tiles = None
        self.num_of_windows = 0
        self.number_of_ack_waits = 0

    def set_packet(self, packet_bbuf):
        """ store the packet of bitbuffer for later use,
        return dtag for the packet """
        self.packet_bbuf = packet_bbuf.copy()
        self.mic_base = packet_bbuf.copy()
        # update dtag for next
        self.dtag += 1
        if self.dtag > schcmsg.get_max_dtag(self.rule):
            self.dtag = 0

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
        extra_bits = (schcmsg.roundup(last_frag_base_size,
                                      self.rule["L2WordSize"]) -
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
            extra_bits = (schcmsg.roundup(penultimate_size,
                                        self.rule["L2WordSize"]) -
                            penultimate_size)
            mic_base.add_bits(0, schcmsg.roundup(extra_bits,
                                                self.rule["MICWordSize"]))
        #

        mic = get_mic(mic_base.get_content())
        print("Send MIC {}, base = {}, lenght = {}".format(mic, mic_base.get_content(), len(mic_base.get_content())))
        return mic.to_bytes(4, "big")

    def start_sending(self):
        self.send_frag()

    def send_frag(self):
        raise NotImplementedError("it is implemented at the subclass.")

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
        min_size = (schcmsg.get_sender_header_size(self.rule) +
                        schcmsg.get_mic_size(self.rule) +
                        self.rule["L2WordSize"])
        if self.protocol.layer2.get_mtu_size() < min_size:
            raise ValueError("the MTU={} is not enough to carry the SCHC fragment of No-ACK mode={}".format(self.protocol.layer2.get_mtu_size(), min_size))

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
        payload_size = (self.protocol.layer2.get_mtu_size() -
                        schcmsg.get_sender_header_size(self.rule))
        remaining_data_size = self.packet_bbuf.count_remaining_bits()
        if remaining_data_size >= payload_size:
            # put remaining_size of bits of packet into the tile.
            tile = self.packet_bbuf.get_bits_as_buffer(payload_size)
            transmit_callback = self.event_sent_frag
            fcn=0
            self.mic_sent=None
            if enable_statsct:
                Statsct.set_msg_type("SCHC_FRAG")
                Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
        elif remaining_data_size < payload_size:
            if remaining_data_size <= (
                    payload_size - schcmsg.get_mic_size(self.rule)):
                tile = None
                if remaining_data_size > 0:
                    tile = self.packet_bbuf.get_bits_as_buffer()
                # make All-1 frag.
                assert self.mic_sent is None
                last_frag_base_size = 0
                if tile is not None:
                    last_frag_base_size += (
                        schcmsg.get_sender_header_size(self.rule) +
                        schcmsg.get_mic_size(self.rule) +
                        remaining_data_size)
                self.mic_sent = self.get_mic(self.mic_base, last_frag_base_size)
                # callback doesn't need in No-ACK mode.
                transmit_callback = None
                fcn=schcmsg.get_fcn_all_1(self.rule)
                if enable_statsct:
                    Statsct.set_msg_type("SCHC_ALL_1")
                    Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule) +
                        schcmsg.get_mic_size(self.rule))
            else:
                # put the size of the complements of the header to L2 Word.
                tile_size = (remaining_data_size -
                                (schcmsg.get_sender_header_size(self.rule) +
                                remaining_data_size)%self.rule["L2WordSize"])
                tile = self.packet_bbuf.get_bits_as_buffer(tile_size)
                transmit_callback = self.event_sent_frag
                fcn=0
                self.mic_sent=None
                if enable_statsct:
                    Statsct.set_msg_type("SCHC_FRAG")
                    Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
        schc_frag = schcmsg.frag_sender_tx(
                self.rule, dtag=self.dtag,
                win=None,
                fcn=fcn,
                mic=self.mic_sent,
                payload=tile)
                
        # send a SCHC fragment
        args = (schc_frag.packet.get_content(), self.context["devL2Addr"],
                transmit_callback)
        print("frag sent:", schc_frag.__dict__)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args)

    def event_sent_frag(self, status): # status == nb actually sent (for now)
        print("event_sent_frag")
        self.send_frag()
        #input("")
    def receive_frag(self, bbuf, dtag):
        # in No-Ack mode, only Receiver Abort message can be acceptable.
        schc_frag = schcmsg.frag_sender_rx(self.rule, bbuf)
        print("sender frag received:", schc_frag.__dict__)
        if ((self.rule["WSize"] is 0 or
             schc_frag.win == schcmsg.get_win_all_1(self.rule)) and
            schc_frag.cbit == 1 and schc_frag.remaining.allones() == True):
            print("Receiver Abort rid={} dtag={}".format(
                    self.rule.ruleID, self.dtag))
            return
        else:
            print("XXX Unacceptable message has been received.")


#---------------------------------------------------------------------------

class FragmentAckOnError(FragmentBase):

    def set_packet(self, packet_bbuf):
        super().set_packet(packet_bbuf)
        self.all_tiles = TileList(self.rule, packet_bbuf)
        # XXX
        # check whether the size of the last tile is less than L2 word
        # AND the tile number is zero
        # because draft-17 doesn't specify how to handle it.
        a = self.all_tiles.get_all_tiles()
        if (a[-1]["t-num"] == 0 and
            a[-1]["tile"].count_added_bits() < self.rule["L2WordSize"]):
            raise ValueError("The size of the last tile with the tile number 0 must be equal to or greater than L2 word size.")
        # make the bitmap
        #self.bit_list = make_bit_list(self.all_tiles.get_all_tiles(),
        #                              self.rule["FCNSize"],
        #                              schcmsg.get_fcn_all_1(self.rule))
        self.bit_list = make_bit_list(self.all_tiles.get_all_tiles(),
                                      self.rule["FCNSize"],
                                      self.rule["WSize"])
        print("bit_list:", self.bit_list)
        for tile in self.all_tiles.get_all_tiles():
            print("w: {}, t: {}, sent: {}".format(tile['w-num'],tile['t-num'],tile['sent']))
        self.all1_send = False
        self.num_of_windows = 0
        for pos in self.bit_list:
            print("bitmap: {}, length:{}".format(self.bit_list[pos], len(self.bit_list[pos])))
            if len(self.bit_list[pos]) is not 0:
                self.num_of_windows += 1
        print("number of windows = {}".format(self.num_of_windows))
        #input("")
    def send_frag(self):
        print("{} send_frag!!!!!!!!!!!!!!!!!".format(utime.time()))
        print("all1_send-> {}, resend -> {}, state -> {}".format(self.all1_send, self.resend,self.state))
        print("all tiles unsend -> {}".format(self.all_tiles))
        for tile in self.all_tiles.get_all_tiles():
            print("w: {}, t: {}, sent: {}".format(tile['w-num'],tile['t-num'],tile['sent']))
        if self.state == self.ACK_SUCCESS:
            return
        
        # if self.state == self.ACK_FAILURE and self.num_of_windows != 1 and self.number_of_ack_waits <= self.num_of_windows:
        #     #waiting for the acks of the others windows
        #     self.number_of_ack_waits += 1 #wait depends on the number of windows
        #     #set ack_time_out_timer
        #     print("waiting for more acks: {}".format(self.number_of_ack_waits))
        #     return


        # get contiguous tiles as many as possible fit in MTU.
        mtu_size = self.protocol.layer2.get_mtu_size()
        window_tiles, nb_remaining_tiles, remaining_size = self.all_tiles.get_tiles(mtu_size)
        print("window tiles: {}, nb_remaining_tiles: {}, remaining_size: {}".format(window_tiles, nb_remaining_tiles, remaining_size))
        if window_tiles is None and self.resend:
            print("no more tiles to resend")
            #how to identify that all tiles are resend and that the ack timeout should be set
            #to wait for tha last ok. It should be set after retransmission of the last fragment
            if self.state == self.ACK_FAILURE and self.event_id_ack_wait_timer is None:
                win = self.last_window_tiles[0]["w-num"] if self.last_window_tiles[0]["w-num"] is not None else 0 
                if self.last_window_tiles[0]["t-num"] == 0:
                    win += 1
                schc_frag = schcmsg.frag_sender_tx(
                        self.rule, dtag=self.dtag, win=win,
                        fcn=schcmsg.get_fcn_all_1(self.rule),
                        mic=self.mic_sent)
                #set ack waiting timer
                args = (schc_frag, win,)
                self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                    self.ack_wait_timer, self.ack_timeout, args)
                print("*******event id {}".format(self.event_id_ack_wait_timer))    
            # if self.all1_send and self.state == self.ACK_FAILURE:
            #     #case when with the bitmap is not possible to identify the missing tile,
            #     #resend ALL-1 messages
            #     # send a SCHC fragment
            #     args = (self.schc_all_1.packet.get_content(), self.context["devL2Addr"],
            #     self.event_sent_frag)
            #     print("frag sent:", self.schc_all_1.__dict__)
            #     if enable_statsct:
            #         Statsct.set_msg_type("SCHC_ALL_1")
            #         Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule) +
            #             schcmsg.get_mic_size(self.rule))
            #     self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
            #                                     args)
            #     print("Sending all-1 beacuse there is an ACK FaILURE but cannot find the missing tiles")
            #     input("")


            # win = self.last_window_tiles[0]["w-num"] if self.last_window_tiles[0]["w-num"] is not None else 0 
            # if self.last_window_tiles[0]["t-num"] == 0:
            #     win += 1
            # schc_frag = schcmsg.frag_sender_tx(
            #         self.rule, dtag=self.dtag, win=win,
            #         fcn=schcmsg.get_fcn_all_1(self.rule),
            #         mic=self.mic_sent)
            # set ack waiting timer
            #args = (schc_frag, win,)
            #self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
            #        self.ack_wait_timer, self.ack_timeout, args)
            #print("*******event id {}".format(self.event_id_ack_wait_timer))

        #if window_tiles is not None and not self.all1_send and not self.resend:
        if window_tiles is not None:
        
            print("window_tiles is not None -> {}, resend -> {}".format(self.all1_send, self.resend))
            # even when mic is sent, it comes here in the retransmission.
            if self.all1_send and self.state != self.ACK_FAILURE:
                #when there is a retransmission, the all-1 is send again and is send before
                #the ACK-OK is received. One option is not set the timer after the last
                #retransmission, but i don´t know how to idenfy that all missing fragments
                #have been send. Also the ALL-1 is not retransmisted (dont know if this should
                # be like this. For example, if the ALL-1s is lost, the receiver timer expires
                # and a receiver abort is send. If it arrives, there is not need to retransmit 
                # the message after the retransmission of the missing fragments)
                #FIX, all-1 is resend
                print('All-1 ones already send')
                #cancel timer when there is success
                # if self.event_id_ack_wait_timer and self.state == self.ACK_SUCCESS:
                #     self.cancel_ack_wait_timer() 
                #else:
                #    print("how to add a timer without sending a message")
                # fcn = schcmsg.get_fcn_all_1(self.rule)
                # args = (schc_frag, window_tiles[0]["w-num"],)
                # elf.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                # self.ack_wait_timer, self.ack_timeout, args)
                #fcn = schcmsg.get_fcn_all_1(self.rule)
                return
            elif (nb_remaining_tiles == 0 and
                len(window_tiles) == 1 and
                remaining_size >= schcmsg.get_mic_size(self.rule)):
                print("ALL-1 prepared")
                
                    
                # make the All-1 frag with this tile.
                # the All-1 fragment can carry only one tile of which the size
                # is less than L2 word size.
                fcn = schcmsg.get_fcn_all_1(self.rule)
                last_frag_base_size = (
                        schcmsg.get_sender_header_size(self.rule) +
                        schcmsg.get_mic_size(self.rule) +
                        TileList.get_tile_size(window_tiles))
                #check if mic exists, no need no created again
                if self.mic_sent is None:        
                    mic = self.get_mic(self.mic_base, last_frag_base_size)
                    # store the mic in order to know all-1 has been sent.
                    self.mic_sent = mic
                else:
                    mic = self.mic_sent
                print("mic_sent -> {}".format(self.mic_sent))
                if enable_statsct:
                    Statsct.set_msg_type("SCHC_ALL_1")
                    Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule) +
                        schcmsg.get_mic_size(self.rule))
                self.all1_send = True
                self.state = self.SEND_ALL_1
            else:
                print("regular SCHC frag")
                # regular fragment.
                fcn = window_tiles[0]["t-num"]
                mic = None
                
                if enable_statsct:
                    Statsct.set_msg_type("SCHC_FRAG")
                    Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, dtag=self.dtag,
                    win=window_tiles[0]["w-num"],
                    fcn=fcn,
                    mic=mic,
                    payload=TileList.concat(window_tiles))
            
            if mic is not None:

                print("mic is not None")
                # set ack waiting timer
                #if enable_statsct:
                #    Statsct.set_msg_type("SCHC_FRAG")
                #    Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
                args = (schc_frag, window_tiles[0]["w-num"],)
                print("all ones")
                self.schc_all_1 = schc_frag          
                self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                        self.ack_wait_timer, self.ack_timeout, args)
                print("*******event id {}".format(self.event_id_ack_wait_timer))
            # save the last window tiles.
            self.last_window_tiles = window_tiles
            print("self.last_window_tiles -> {}".format(self.last_window_tiles))
        elif self.mic_sent is not None or self.all1_send:
            print("self.mic_sent is not None state -> {}".format(self.state))
            # it looks that all fragments have been sent.
            print("----------------------- all tiles have been sent -----------------------",
                  window_tiles, nb_remaining_tiles, remaining_size)
            schc_frag = None
            self.all1_send = True
            if self.event_id_ack_wait_timer and self.state == self.ACK_SUCCESS:
                self.cancel_ack_wait_timer() 
            return
        else:
            print("only mic all tiles send")
            # Here, only MIC will be sent since all tiles has been sent.
            assert self.last_window_tiles is not None
            # As the MTU would be changed anytime AND the size of the
            # significant padding bits would be changed, therefore the MIC
            # calculation may be needed again.
            # XXX maybe it's better to check whether the size of MTU is change
            # or not when the previous MIC was calculated..
            last_frag_base_size = (schcmsg.get_sender_header_size(self.rule) +
                                TileList.get_tile_size(self.last_window_tiles))
            self.mic_sent = self.get_mic(self.mic_base, last_frag_base_size)
            # check the win number.
            # XXX if the last tile number is zero, here window number has to be
            # incremented.
            win = self.last_window_tiles[0]["w-num"]
            if self.last_window_tiles[0]["t-num"] == 0:
                win += 1
            schc_frag = schcmsg.frag_sender_tx(
                    self.rule, dtag=self.dtag, win=win,
                    fcn=schcmsg.get_fcn_all_1(self.rule),
                    mic=self.mic_sent)
            # set ack waiting timer
            args = (schc_frag, win,)
            if enable_statsct:
                Statsct.set_msg_type("SCHC_ALL_1")
                Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule) +
                        schcmsg.get_mic_size(self.rule))
            self.schc_all_1 = schc_frag
            self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                    self.ack_wait_timer, self.ack_timeout, args)
            print("*******event id {}".format(self.event_id_ack_wait_timer))


        # send a SCHC fragment
        args = (schc_frag.packet.get_content(), self.context["devL2Addr"],
                self.event_sent_frag)
        print("frag sent:", schc_frag.__dict__)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args)

    def cancel_ack_wait_timer(self):
        # don't assert here because the receiver sends ACK back anytime.
        #assert self.event_id_ack_wait_timer is not None
        print('----------------------- cancel_ack_wait_timer -----------------------')
        self.protocol.scheduler.cancel_event(self.event_id_ack_wait_timer)
        self.event_id_ack_wait_timer = None

    def ack_timeout(self, *args):
        self.cancel_ack_wait_timer()
        print("----------------------- ACK timeout -----------------------  ")
        assert len(args) == 2
        assert isinstance(args[0], schcmsg.frag_sender_tx)
        assert isinstance(args[1], int)
        schc_frag = args[0]
        win = args[1]
        self.ack_requests_counter += 1
        print("ack_requests_counter -> {}".format(self.ack_requests_counter))
        if self.ack_requests_counter > max_ack_requests:
            # sending sender abort.
            schc_frag = schcmsg.frag_sender_tx_abort(self.rule, self.dtag, win)
            args = (schc_frag.packet.get_content(), self.context["devL2Addr"])
            print("Sent Sender-Abort.", schc_frag.__dict__)
            if enable_statsct:
                Statsct.set_msg_type("SCHC_SENDER_ABORT")
                #Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))

            self.protocol.scheduler.add_event(0,
                                        self.protocol.layer2.send_packet, args)
            return
        # set ack waiting timer
        self.event_id_ack_wait_timer = self.protocol.scheduler.add_event(
                self.ack_wait_timer, self.ack_timeout, args)
        print("*******event id {}".format(self.event_id_ack_wait_timer))
        schc_frag = schcmsg.frag_sender_ack_req(self.rule, self.dtag, win)
        if enable_statsct:
                Statsct.set_msg_type("SCHC_ACK_REQ")
        # # retransmit MIC.
        args = (schc_frag.packet.get_content(), self.context["devL2Addr"],
                self.event_sent_frag)
        print("SCHC ACK REQ frag:", schc_frag.__dict__)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                        args)
        """ waits for all the acks before sending the ack request
        
        self.number_of_ack_waits += 1
        print("number_of_ack_waits -> {}".format(self.number_of_ack_waits))
        if self.number_of_ack_waits > self.num_of_windows:
            schc_frag = schcmsg.frag_sender_ack_req(self.rule, self.dtag, win)
            if enable_statsct:
                    Statsct.set_msg_type("SCHC_ACK_REQ")
            # # retransmit MIC.
            args = (schc_frag.packet.get_content(), self.context["devL2Addr"],
                    self.event_sent_frag)
            print("SCHC ACK REQ frag:", schc_frag.__dict__)
            # if enable_statsct:
            #     Statsct.set_msg_type("SCHC_FRAG")
            #     Statsct.set_header_size(schcmsg.get_sender_header_size(self.rule))
            self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                            args)
            self.number_of_ack_waits = 0
            
        else:
            print("Do no send ACK REQ, waiting for more ACKS")        #the idea is that if the ack did not arrive, to send a SCHC ACK REQ
        """

    def event_sent_frag(self, status): # status == nb actually sent (for now)
        print("EVENT SEND FRAG")
        self.send_frag()

    def receive_frag(self, bbuf, dtag):
        # the ack timer can be cancelled here, because it's been done whether
        # both rule_id and dtag in the fragment are matched to this session
        # at process_received_packet().
        self.cancel_ack_wait_timer() # the timeout is canceled but has to be set 
        # when an ack should be received
        self.resend = False
        #
        schc_frag = schcmsg.frag_sender_rx(self.rule, bbuf)
        print("-----------------------  sender frag received -----------------------") 
        print("fragment received -> {}".format(schc_frag.__dict__))
        if ((self.rule["WSize"] is None or
             schc_frag.win == schcmsg.get_win_all_1(self.rule)) and
            schc_frag.cbit == 1 and schc_frag.remaining.allones() == True):
            print("-----------------------  Receiver Abort rid={} dtag={} -----------------------".format(
                    self.rule.ruleID, self.dtag))
            #self.resend = False
            self.state = self.RECEIVER_ABORT
            
            return
        if schc_frag.cbit == 1:
            print("----------------------- ACK Success rid={} dtag={} -----------------------".format(
                    self.rule.ruleID, self.dtag))
            #self.resend = False
            self.state = self.ACK_SUCCESS
            return
        if schc_frag.cbit == 0:
            print("----------------------- ACK Failure rid={} dtag={} -----------------------".format(
                    self.rule.ruleID, self.dtag))
            #self.resend = False
            #self.all1_send = False
            self.state = self.ACK_FAILURE
            self.resend_frag(schc_frag)
            return
        

    def resend_frag(self, schc_frag):
        self.resend = True
        print("recv bitmap:", (schc_frag.win, schc_frag.bitmap.to_bit_list()))
        print("sent bitmap:", (schc_frag.win, self.bit_list[schc_frag.win]))
        self.all_tiles.unset_sent_flag(schc_frag.win,
                                       schc_frag.bitmap.to_bit_list())
        self.send_frag()

