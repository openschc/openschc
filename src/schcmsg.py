"""
.. module:: schcmsg
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------
from base_import import *  # used for now for differing modules in py/upy

import bitarray

#---------------------------------------------------------------------------

def get_fcn_all_1(rule):
    return (1<<rule["FCNSize"])-1

def get_fcn_all_0(rule):
    print((0<<rule["FCNSize"]))
    return (0<<rule["FCNSize"])-4

def get_win_all_1(rule):
    return (1<<rule["WSize"])-1

def get_max_fcn(rule):
    return rule["windowSize"]-1

def get_max_dtag(rule):
    return (1<<rule["dtagSize"])-1

def get_sender_header_size(rule):
    return rule["ruleLength"] + rule["dtagSize"] + rule.get("WSize", 0) + rule["FCNSize"]

def get_receiver_header_size(rule):
    return rule["ruleLength"] + rule["dtagSize"] + rule.get("WSize", 0) + 1

def get_mic_size(rule):
    assert rule["MICAlgorithm"] == "crc32"
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
            raise ValueError("dtag is too big than the field size.")

class frag_tx(frag_base):

    '''
    parent class for sending message.
    '''
    def make_frag(self, dtag, win=None, fcn=None, mic=None, bitmap=None,
                  cbit=None, payload=None, abort=False, req = False):
        assert payload is None or isinstance(payload, BitBuffer)
        buffer = BitBuffer()
        #print("ruleID")
        #print(self.rule["ruleID"])
        if self.rule["ruleID"] is not None and self.rule["ruleLength"] is not None:
            buffer.add_bits(self.rule["ruleID"], self.rule["ruleLength"])
        if dtag is not None and self.rule["dtagSize"] is not None:
            assert self.rule["dtagSize"] != None # CA: sanity check
            buffer.add_bits(dtag, self.rule["dtagSize"])
        if win is not None and self.rule.get("WSize") is not None:
            buffer.add_bits(win, self.rule["WSize"])
        #print("buffer before {},{},{}".format(buffer.count_added_bits(), 
        #           buffer.count_padding_bits(),buffer.count_padding_bits()))
        if abort == True:
            # XXX for receiver abort, needs to be fixed
            buffer.add_bits(get_fcn_all_1(self.rule), self.rule["FCNSize"])
        elif req == True:
            #print(buffer)
            buffer.add_bits(0, self.rule["FCNSize"])
            #print("buffer before {},{},{}".format(buffer.count_added_bits(), 
            #        buffer.count_padding_bits(),buffer.count_padding_bits()))

            #for zero in range(0, self.rule["FCNSize"]):
            #    print("{},{}".format(self.rule["FCNSize"],zero))
            #    buffer.set_bit(0)
            #print("buffer after")
            #print(buffer)
        else:
            if fcn is not None and self.rule.get("FCNSize") is not None:
                buffer.add_bits(fcn, self.rule["FCNSize"])
            if mic is not None and self.rule.get("MICAlgorithm") is not None:
                mic_size = get_mic_size(self.rule)
                assert mic_size % bitarray.BITS_PER_BYTE == 0
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
        if (self.rule["ruleID"] is not None and
            self.rule["ruleLength"] is not None):
            buffer.add_bits(self.rule["ruleID"], self.rule["ruleLength"])
        if dtag is not None and self.rule["dtagSize"] is not None:
            assert self.rule["dtagSize"] != None # CA: sanity check
            buffer.add_bits(dtag, self.rule["dtagSize"])
        if abort == True:
            if self.rule.get("WSize") is not None:
                win = get_win_all_1(self.rule)
                buffer.add_bits(win, self.rule["WSize"])
            # c-bit
            buffer.set_bit(1)
            padding_size = (self.rule["L2WordSize"] -
                            buffer.count_added_bits()%self.rule["L2WordSize"])
            padding_size += self.rule["L2WordSize"]
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
    def __init__(self, rule, dtag=None, win=None):
        self.init_param()
        self.rule = rule
        self.rule_id = rule["ruleID"]
        self.make_frag(dtag, win=win, abort=True)

class frag_sender_tx(frag_tx):
    """ make a message for the SCHC fragment sender. """
    def __init__(self, rule, dtag, win=None, fcn=None, mic=None,
                 cbit=None, payload=None, abort=False):
        self.init_param()
        self.rule = rule
        self.rule_id = rule["ruleID"]
        self.make_frag(dtag, win=win, fcn=fcn, mic=mic, payload=payload)

class frag_sender_ack_req(frag_tx):
    """ make ACK Request message.
    ACK REQ : [ Rule ID | Dtag | W | (P-1) ]
    """
    def __init__(self, rule, dtag, win):
        self.init_param()
        self.rule = rule
        self.rule_id = rule["ruleID"]
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
        self.rule_id = rule["ruleID"]
        self.make_frag(dtag, win=win, cbit=cbit, bitmap=bitmap)

class frag_receiver_tx_abort(frag_receiver_tx):
    """ make Receiver Abort message.
    Recv Abort : [ Rule ID | Dtag | W-1 | C-1 | (P-1) ]
    """
    def __init__(self, rule, dtag=None):
        self.init_param()
        self.rule = rule
        self.rule_id = rule["ruleID"]
        self.make_frag(dtag, abort=True)



class frag_rx(frag_base):

    '''
    parent class for receiving message.
    recvbuf: str, bytes, bytearray.
    '''
    def set_recvbuf(self, recvbuf):
        print("set_recvbuf -> {}".format(recvbuf))
        assert isinstance(recvbuf, BitBuffer)
        self.packet_bbuf = recvbuf

    def parse_dtag(self):
        """ get the value of the dtag field and set it into self.dtag.
        if dtagSize in the rule is zero, default dtag is adopted.
        XXX need to be considered.
        """
        dtag_size = self.rule.get("dtagSize", 0)
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
        win_size = self.rule.get("WSize", 0)
        if win_size != 0:
            self.win = self.packet_bbuf.get_bits(win_size)
        return win_size

    def parse_fcn(self):
        '''
        parse fcn in the frame.
        assuming that fcn_size is not zero.
        '''
        self.fcn = self.packet_bbuf.get_bits(self.rule["FCNSize"])
        return self.rule["FCNSize"]

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
        pos = rule["ruleLength"]
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
#        pos = rule["ruleLength"]
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
        print("frag_sender_rx")
        print(packet_bbuf)
        #input("")
        self.init_param()
        self.set_recvbuf(packet_bbuf)
        self.rule = rule
        self.rule_id = self.packet_bbuf.get_bits(rule["ruleLength"])
        pos = self.rule["ruleLength"]
        pos += self.parse_dtag()
        pos += self.parse_win()
        pos += self.parse_cbit()
        if self.cbit == 0:
            pos += self.parse_bitmap()
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
        print("frag_receiver_rx")
        print(packet_bbuf)
        
        self.init_param()
        self.set_recvbuf(packet_bbuf)
        self.rule = rule
        self.rule_id = self.packet_bbuf.get_bits(rule["ruleLength"])
        pos = self.rule["ruleLength"]
        pos += self.parse_dtag()
        pos += self.parse_win()
        pos += self.parse_fcn()
        if self.fcn == get_fcn_all_1(self.rule):
            if self.packet_bbuf.count_remaining_bits() < self.rule["L2WordSize"]:
                # this is a Sender Abort message.
                self.abort = True
                return
            # this is a All-1 message.
            pos += self.parse_mic()
        elif self.fcn == 0:
            print('FCN ALL-0 found!')
            self.ack_request = True
            # this is a ACK REQ message
        self.payload = self.packet_bbuf.get_bits_as_buffer()
        #TODO: Parse ACK REQ