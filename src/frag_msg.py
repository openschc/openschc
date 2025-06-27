"""
.. module:: frag_msg
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------
from gen_base_import import *  # used for now for differing modules in py/upy
from compr_core import *
import gen_bitarray
from compr_core import *
from gen_utils import dprint

#---------------------------------------------------------------------------

def get_fcn_all_1(rule):
    rule = rule[T_FRAG][T_FRAG_PROF] #ajoute
    return (1<<rule[T_FRAG_FCN])-1

def get_fcn_all_0(rule):
    rule = rule[T_FRAG][T_FRAG_PROF] #ajoute
    dprint((0<<rule[T_FRAG_FCN]))
    return (0<<rule[T_FRAG_FCN])-4

def get_win_all_1(rule):
    rule = rule[T_FRAG][T_FRAG_PROF] #ajoute
    return (1<<rule[T_FRAG_W_SIZE])-1

def get_max_fcn(rule):
    rule = rule[T_FRAG][T_FRAG_PROF] #ajoute
    return rule[T_FRAG_WINDOW_SIZE]-1

def get_max_dtag(rule):
    rule = rule[T_FRAG][T_FRAG_PROF] #ajoute
    return (1<<rule[T_FRAG_DTAG_SIZE])-1

def get_sender_header_size(rule):
    """Changement à corriger
    return rule[T_RULEIDLENGTH] + rule[T_FRAG_DTAG_SIZE] + rule.get(T_FRAG_W_SIZE , 0) + rule[T_FRAG_FCN]
    """
    return rule[T_RULEIDLENGTH] + rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] + rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] + rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN]

def get_receiver_header_size(rule):
    """Changement à corriger
    return rule[T_RULEIDLENGTH] + rule[T_FRAG_DTAG_SIZE] + rule.get(T_FRAG_W_SIZE , 0) + 1
    """
    return rule[T_RULEIDLENGTH] + rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] + rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] + 1

def get_mic_size(rule):
    rule = rule[T_FRAG][T_FRAG_PROF] #ajoute
    assert rule[T_FRAG_MIC] ==  T_FRAG_RFC8724
    return 32


def roundup(v, w=8):
    """ return the size of bits align to the w boundary. """
    a, b = (v//w, v%w)
    return a*w+(w if b else 0)

#---------------------------------------------------------------------------

class frag_base():
    '''
    base class for operation of message.
    packet: a bytearray transmitted or a bytearray received.
    '''
    def init_param(self):
        self.rule_id = None
        self.dtag = None
        self.win = None
        self.fcn = None
        self.mic = None
        self.bitmap = None
        self.cbit = None
        self.payload = None
        self.packet = None
        self.abort = False
        self.ack_request = False
        self.ack = False

    def set_param(self, rule_id, dtag=None, win=None, fcn=None, mic=None,
                  bitmap=None, cbit=None, payload=None):
        self.rule_id = rule_id
        self.dtag = dtag
        self.win = win
        self.fcn = fcn
        self.mic = mic
        self.bitmap = bitmap
        self.cbit = cbit
        self.payload = payload
        # check the field size.
        if dtag > get_max_dtag(self.rule):
            raise ValueError("dtag is bigger than the field size.")

    def display(self):
        print ("rule id", self.rule_id)
        print ("dtag", self.dtag)
        print ("win", self.win)
        print ("fcn", self.fcn)
        print ("mic", self.mic)
        print ("bitmap", self.bitmap)
        print ("cbit", self.cbit)
        print ("payload", self.payload)
        print ("packet", self.packet)
        print ("abort", self.abort)
        print ("ack_request", self.ack_request)
        print ("ack", self.ack)

class frag_tx(frag_base):

    '''
    parent class for sending message.
    '''
    def make_frag(self, dtag, win=None, fcn=None, mic=None, bitmap=None,
                  cbit=None, payload=None, abort=False , req = False):
        assert payload is None or isinstance(payload, BitBuffer)
        buffer = BitBuffer()
        #dprint(T_RULEID)
        #dprint("Make_frag Rule", self.rule)
        if self.rule[T_RULEID] is not None and self.rule[T_RULEIDLENGTH] is not None:
            buffer.add_bits(self.rule[T_RULEID], self.rule[T_RULEIDLENGTH])
        if dtag is not None and self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] is not None:
            assert self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] != None # CA: sanity check
            buffer.add_bits(dtag, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE])
        if win is not None and self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE ] is not None:
            buffer.add_bits(win, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE ])
        #dprint("buffer before {},{},{}".format(buffer.count_added_bits(), 
        #buffer.count_padding_bits(),buffer.count_padding_bits()))
        if abort == True:
            # XXX for receiver abort, needs to be fixed
            buffer.add_bits(get_fcn_all_1(self.rule), self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])
        elif req == True:
            #dprint(buffer)
            buffer.add_bits(0, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])
            #dprint("buffer before {},{},{}".format(buffer.count_added_bits(), 
            #        buffer.count_padding_bits(),buffer.count_padding_bits()))
 
            #for zero in range(0, self.rule[T_FRAG_FCN]):
            #    dprint("{},{}".format(self.rule[T_FRAG_FCN],zero))
            #    buffer.set_bit(0)
            #dprint("buffer after")
            #dprint(buffer)        
        else:
            if fcn is not None and self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN] is not None:
                buffer.add_bits(fcn, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])
            if mic is not None and self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_MIC] is not None:
                mic_size = get_mic_size(self.rule)
                assert mic_size % gen_bitarray.BITS_PER_BYTE == 0
                assert len(mic) == mic_size // 8
                buffer.add_bytes(mic)
            if cbit is not None:
                buffer.set_bit(cbit)
            if bitmap is not None:
                buffer += bitmap
            #
            if payload is not None:
                # assumed that bit_set() has extended to a byte boundary
                buffer += payload
        #
        self.set_param(self.rule_id, dtag, win, fcn, mic, bitmap, cbit, payload)
        self.packet = buffer

class frag_receiver_tx(frag_base):
    """ make SCHC fragment receiver TX message. """
    def make_frag(self, dtag, win=None, cbit=None, bitmap=None, abort=False):
        buffer = BitBuffer()
        if (self.rule[T_RULEID] is not None and
            self.rule[T_RULEIDLENGTH] is not None):
            buffer.add_bits(self.rule[T_RULEID], self.rule[T_RULEIDLENGTH])
        if dtag is not None and self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] is not None:
            assert self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] != None # CA: sanity check
            buffer.add_bits(dtag, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE])
        if abort == True:
            if self.rule.get(T_FRAG_W_SIZE ) is not None:
                win = get_win_all_1(self.rule)
                buffer.add_bits(win, self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE ])
            # c-bit
            buffer.set_bit(1)
            padding_size = (self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE] -
                            buffer.count_added_bits()%self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE])
            padding_size += self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE]
            # padding bits
            for _ in range(padding_size):
                buffer.set_bit(1)
        else:
            if cbit is not None:
                buffer.set_bit(cbit)
            if bitmap is not None:
                buffer += bitmap
        #
        self.set_param(self.rule_id, dtag=dtag, win=win, cbit=cbit,
                       bitmap=bitmap)
        self.packet = buffer

class frag_sender_tx_abort(frag_tx):
    """ make a message for the SCHC fragment sender. """
    def __init__(self, rule, dtag=None):
        self.init_param()
        self.rule = rule
        self.rule_id = rule[T_RULEID]
        # Must set w to proper value:
        # 1815 If the W field is present,
        # 1817 o the fragment sender MUST set it to all ones.  Other values are
        # 1818   RESERVED.
        w_size = self.rule["Fragmentation"]["FRModeProfile"]["WSize"]
        win = (1<<w_size)-1
        self.make_frag(dtag, win=win, abort=True)

class frag_sender_tx(frag_tx):
    """ make a message for the SCHC fragment sender. """
    def __init__(self, rule, dtag, win=None, fcn=None, mic=None,
                 cbit=None, payload=None, abort=False):
        self.init_param()
        self.rule = rule
        self.rule_id = rule[T_RULEID]
        self.make_frag(dtag, win=win, fcn=fcn, mic=mic, payload=payload)

class frag_sender_ack_req(frag_tx):
    """ make ACK Request message.
    ACK REQ : [ Rule ID | Dtag | W | (P-1) ]
    """
    def __init__(self, rule, dtag, win):
        self.init_param()
        self.rule = rule
        self.rule_id = rule[T_RULEID]
        self.make_frag(dtag, win=win,req=True)


class frag_receiver_tx_all0_ack(frag_tx):

    '''
    for the fragment receiver, to make an all0 ack.
        Format: [ Rule ID | DTag |W|  Bitmap  |P1]
    '''
    def __init__(self, R, dtag, win=None, bitmap=None):
        self.init_param()
        self.rule = R
        self.make_frag(dtag, win=win, bitmap=bitmap)

class frag_receiver_tx_all1_ack(frag_tx):
    """ make ACK message.
    for the fragment receiver, to make an all1 ack.
        Format: [ Rule ID | DTag |W|C|P1]
        Format: [ Rule ID | DTag |W|C|  Bitmap  |P1]
    """
    def __init__(self, rule, dtag, win=None, cbit=None, bitmap=None):
        self.init_param()
        self.rule = rule
        self.rule_id = rule[T_RULEID]
        self.make_frag(dtag, win=win, cbit=cbit, bitmap=bitmap)

class frag_receiver_tx_abort(frag_receiver_tx):
    """ make Receiver Abort message.
    Recv Abort : [ Rule ID | Dtag | W-1 | C-1 | (P-1) ]
    """
    def __init__(self, rule, dtag=None):
        self.init_param()
        self.rule = rule
        self.rule_id = rule[T_RULEID]
        self.make_frag(dtag, abort=True)

class frag_rx(frag_base):

    '''
    parent class for receiving message.
    recvbuf: str, bytes, bytearray.
    '''
    def set_recvbuf(self, recvbuf):
        dprint("set_recvbuf -> {}".format(recvbuf))
        assert isinstance(recvbuf, BitBuffer)
        self.packet_bbuf = recvbuf

    def parse_dtag(self):
        """ get the value of the dtag field and set it into self.dtag.
        if dtagSize in the rule is zero, default dtag is adopted.
        XXX need to be considered.
        """
        dtag_size = self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE]
        if dtag_size != 0:
            dtag = self.packet_bbuf.get_bits(dtag_size)
        else:
            # XXX need a default dtag, or None handling.
            dtag = 1
        #
        self.dtag = dtag
        return dtag_size

    def parse_win(self):
        """ get the value of the window field and set it into self.win.
        if WSize in the rule is zero, self.win is not set (None).
        """
        win_size = self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE ]
        if win_size != 0:
            self.win = self.packet_bbuf.get_bits(win_size)
        return win_size

    def parse_fcn(self):
        '''
        parse fcn in the frame.
        assuming that fcn_size is not zero.
        '''
        self.fcn = self.packet_bbuf.get_bits(self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])
        return self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN]

    def parse_bitmap(self):
        """ parse bitmap in the frame. """
        bitmap_size = min(self.packet_bbuf.count_remaining_bits(),
                          get_fcn_all_1(self.rule))
        self.bitmap = self.packet_bbuf.get_bits_as_buffer(bitmap_size)
        return bitmap_size

    def parse_cbit(self):
        '''
        parse cbit in the frame.
        '''
        self.cbit = self.packet_bbuf.get_bits(1)
        return self.cbit

    def parse_mic(self):
        '''
        parse mic in the frame.
        assuming that mic_size is not zero.
        '''
        mic_size = get_mic_size(self.rule)
        self.mic = self.packet_bbuf.get_bits_as_buffer(mic_size).get_content()
        return mic_size

class frag_sender_rx_all0_ack(frag_rx):

    '''
    for the fragment sender to receive the all0 ack.
        Format: [ Rule ID | DTag |W|  Bitmap  |P1]
        Format: [ Rule ID | DTag |W| All-1 |  FF  |P1]

    XXX How can you differenciate the All-1 abort message ?
    e.g. FCN      bitmap All1+FF
         size(=N) size   size
         3        7      11
         4        15     12
         5        31     13
    '''
    def __init__(self, recvbuf, rule, dtag, exp_win=None):
        '''
        recvbuf: buffer received in bytearray().
        R: rule instance.
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.rule = rule
        pos = rule["RuleIDLength"]
        pos += self.parse_dtag()
        pos += self.parse_win()
        # XXX the abort is not supported yet.
        pos += self.parse_bitmap(pos)

#class frag_sender_rx_all1_ack(frag_rx):
#
#    '''
#    for the fragment sender to receive the all1 ack.
#        Format: [ Rule ID | DTag |W|C|P1]
#        Format: [ Rule ID | DTag |W|C|  Bitmap  |P1]
#        Format: [ Rule ID | DTag |W| All-1 |  FF  |P1]
#    '''
#    def __init__(self, recvbuf, rule, dtag, win):
#        '''
#        recvbuf: buffer received in bytearray().
#        R: rule instance.
#        '''
#        self.init_param()
#        self.set_recvbuf(recvbuf)
#        self.rule = rule
#        pos = rule["RuleIDLength"]
#        pos += self.parse_dtag()
#        pos += self.parse_win()
#        # XXX the abort is not supported yet.
#        pos += self.parse_cbit()
#        if self.cbit == 0:
#            pos += self.parse_bitmap(pos)

class frag_sender_rx(frag_rx):
    """ SCHC fragment sender's class to parse the message from the receiver.
    ACK Success: [ Rule ID | Dtag |  W  | C-1 | (P-0) ]
    ACK Failure: [ Rule ID | Dtag |  W  | C-0 | Bitmap | (P-0) ]
    Recv Abort : [ Rule ID | Dtag | W-1 | C-1 | (P-1) ]
    """
    def __init__(self, rule, packet_bbuf):
        """ packet_bbuf: BitBuffer containing the SCHC fragment. """
        dprint("frag_sender_rx")
        dprint(packet_bbuf)
        #input("")        
        self.init_param()
        self.set_recvbuf(packet_bbuf)
        self.rule = rule
        self.rule_id = self.packet_bbuf.get_bits(rule[T_RULEIDLENGTH])
        pos = self.rule[T_RULEIDLENGTH]
        pos += self.parse_dtag()
        pos += self.parse_win()
        pos += self.parse_cbit()
        if self.cbit == 0:
            pos += self.parse_bitmap()
            self.ack = True
        else: # is a Abort if next bits are equal to 1
            self.packet_bbuf.display(format="bin")
            l2_word=rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE]
            l2_remain = (l2_word-(pos%l2_word))%l2_word
            for i in range(0, l2_remain+l2_word):
                b = self.packet_bbuf.get_bits(1)
                if b == 0:
                    self.ack = True
                    return
            self.abort = True
        self.remaining = self.packet_bbuf.get_bits_as_buffer()

class frag_receiver_rx(frag_rx):
    """ SCHC fragment receiver's class to parse the message from the sender.
    Regular    : [ Rule ID | Dtag | W | FCN        | payload | (P-0) ]
    All-0      : [ Rule ID | Dtag | W | FCN(All-0) | payload | (P-0) ]
    All-1      : [ Rule ID | Dtag | W | FCN(All-1) | MIC | (payload) | (P-0) ]
    ACK REQ    : [ Rule ID | Dtag | W | FCN(All-0) | (P-0) ]
    Send. Abort: [ Rule ID | Dtag | W | FCN(All-1) | (P-0) ]
    """
    def __init__(self, rule, packet_bbuf):
        """ packet_bbuf: BitBuffer containing the SCHC fragment. """
        dprint("frag_receiver_rx")
        dprint(packet_bbuf)
        
        self.init_param()
        self.set_recvbuf(packet_bbuf)
        self.rule = rule
        self.rule_id = self.packet_bbuf.get_bits(self.rule[T_RULEIDLENGTH])
        pos = self.rule[T_RULEIDLENGTH]
        pos += self.parse_dtag()
        pos += self.parse_win()
        pos += self.parse_fcn()
        if self.fcn == get_fcn_all_1(self.rule):
            """ Changement à corriger
            if self.packet_bbuf.count_remaining_bits() < self.rule[T_FRAG_L2WORDSIZE]:
            """
            if self.packet_bbuf.count_remaining_bits() < self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE]:
                # this is a Sender Abort message.
                self.abort = True
                return
            # this is a All-1 message.
            pos += self.parse_mic()
        elif self.fcn == 0:
            dprint('FCN ALL-0 found!')
            """ Changement à corriger
            if self.packet_bbuf.count_remaining_bits() < self.rule[T_FRAG_L2WORDSIZE]:
            """
            if self.packet_bbuf.count_remaining_bits() < self.rule[T_FRAG][T_FRAG_PROF][T_FRAG_L2WORDSIZE]:
                # this is a ACK REQ message
                self.ack_request = True
                return
        self.payload = self.packet_bbuf.get_bits_as_buffer()
        #TODO: Parse ACK REQ
