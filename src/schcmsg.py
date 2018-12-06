
from base_import import *  # used for now for differing modules in py/upy

import bitarray

# Copied from schctest/schc_param.py

DEFAULT_FRAGMENT_RID = 1
DEFAULT_L2_SIZE = 8
DEFAULT_RECV_BUFSIZE = 512
DEFAULT_TIMER_T1 = 5
DEFAULT_TIMER_T2 = 10
DEFAULT_TIMER_T3 = 10
DEFAULT_TIMER_T4 = 12
DEFAULT_TIMER_T5 = 14

#class SCHC_MODE(Enum)
class SCHC_MODE():
    NO_ACK = 0
    ACK_ALWAYS = 1
    ACK_ON_ERROR = 2

#---------------------------------------------------------------------------

# 1372       *  The FCN value with all the bits equal to 1 (called All-1)
# 1373          signals the very last tile of a SCHC Packet.  By extension, if
# 1374          windows are used, the last window of a packet is called the
# 1375          All-1 window.

def get_fcn_all_1(rule):
    return (1<<rule["FCNSize"])-1

def get_win_all_1(rule):
    return (1<<rule["windowSize"])-1

def get_MAX_WIND_FCN(rule):
    return (1<<rule["FCNSize"])-2

def get_max_dtag(rule):
    return (1<<rule["dtagSize"])-1

def get_sender_header_size(rule):
    return rule["ruleLength"] + rule["dtagSize"] + rule.get("windowSize", 0) + rule["FCNSize"]

def get_receiver_header_size(rule):
    return rule["ruleLength"] + rule["dtagSize"] + rule.get("windowSize", 0) + 1

def get_mic_size_in_bits(rule):
    assert rule["MICAlgorithm"] == "crc32"
    return 32

#---------------------------------------------------------------------------

'''
NOTE:
    the boundary of the fragment header is alligned to the byte boundary.
    XXX how do I have to handle the padding ?
'''

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

    def set_param(self, rule_id, dtag, win, fcn, mic, bitmap, cbit, payload):
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
                  cbit=None, abort=False, payload=None):
        assert payload is None or isinstance(payload, BitBuffer)
        buffer = BitBuffer()
        #
        # basic fields.
        if self.rule["ruleID"] is not None and self.rule["ruleLength"] is not None:
            buffer.add_bits(self.rule["ruleID"], self.rule["ruleLength"])
        if dtag is not None and self.rule["dtagSize"] is not None:
            assert self.rule["dtagSize"] != None # CA: sanity check
            buffer.add_bits(dtag, self.rule["dtagSize"])
        #
        # extension fields.
        if win is not None and self.rule.get("windowSize") is not None:
            buffer.add_bits(win, self.rule["windowSize"])
        if fcn is not None and self.rule.get("FCNSize") is not None:
            buffer.add_bits(fcn, self.rule["FCNSize"])
        if mic is not None and self.rule.get("MICAlgorithm") is not None:
            mic_size = get_mic_size_in_bits(self.rule)
            assert mic_size % bitarray.BITS_PER_BYTE == 0
            assert len(mic) == mic_size // 8
            buffer.add_bytes(mic)
        if cbit is not None:
            buffer.set_bit(cbit)
        #if bitmap is not None and self.rule.bitmap_size:
        #    buffer.add_bits(bitmap, self.rule.bitmap_size)
        '''
        if abort == True:
            raise RunTimeError("not refactored", "abort == True")
            pb.bit_set(ba, pos, pb.int_to_bit(0xff, 8), extend=True)
            pos += 8
        '''
        #
        if payload is not None:
            # assumed that bit_set() has extended to a byte boundary
            buffer += payload
        #
        # the abort field is implicit, is not needed to set into the parameter.
        self.set_param(self.rule_id, dtag, win, fcn, mic, bitmap, cbit, payload)
        self.packet = buffer

class frag_sender_tx(frag_tx):

    '''
    for the fragment sender to send a message.
    '''
    def __init__(self, rule, rule_id, dtag, win=None, fcn=None, mic=None,
                 cbit=None, payload=None):
        self.init_param()
        self.rule = rule
        self.rule_id = rule_id
        self.make_frag(dtag, win=win, fcn=fcn, mic=mic, payload=payload)

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

    '''
    for the fragment receiver, to make an all1 ack.
        Format: [ Rule ID | DTag |W|C|P1]
        Format: [ Rule ID | DTag |W|C|  Bitmap  |P1]
    '''
    def __init__(self, R, dtag, win=None, cbit=None, bitmap=None):
        self.init_param()
        self.rule = R
        self.make_frag(dtag, win=win, cbit=cbit, bitmap=bitmap)

class frag_receiver_tx_abort(frag_tx):

    '''
    for the fragment receiver, to make an abort message.
        Format: [ Rule ID | DTag |W|0xFF|P1]
    '''
    def __init__(self, R, dtag, win=None, cbit=None, bitmap=None):
        self.init_param()
        self.rule = R
        self.make_frag(dtag, win=win, abort=True)

class frag_rx(frag_base):

    '''
    parent class for receiving message.
    recvbuf: str, bytes, bytearray.
    '''
    def set_recvbuf(self, recvbuf):
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
        if windowSize in the rule is zero, self.win is not set (None).
        """
        win_size = self.rule.get("windowSize", 0)
        if win_size != 0:
            self.win = self.packet_bbuf.get_bits(win_size)
        return win_size

    def parse_fcn(self, pos):
        '''
        parse fcn in the frame.
        assuming that fcn_size is not zero.
        '''
        self.fcn = self.packet_bbuf.get_bits(self.rule["FCNSize"])
        return self.rule["FCNSize"]

    def parse_bitmap(self, pos):
        '''
        parse bitmap in the frame.
        assuming that bitmap_size is not zero.
        '''
        '''
        self.bitmap = pb.bit_get(self.packet, pos, self.rule.bitmap_size,
                                 ret_type=int)
        return self.rule.bitmap_size
        '''
        raise NotImplementedError

    def parse_cbit(self, pos):
        '''
        parse cbit in the frame.
        '''
        self.cbit = self.packet_bbuf.get_bits(1)
        return self.cbit

    def parse_mic(self, pos):
        '''
        parse mic in the frame.
        assuming that mic_size is not zero.
        '''
        mic_size = get_mic_size_in_bits(self.rule)
        self.mic = self.packet_bbuf.get_bits(mic_size)
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

class frag_sender_rx_all1_ack(frag_rx):

    '''
    for the fragment sender to receive the all1 ack.
        Format: [ Rule ID | DTag |W|C|P1]
        Format: [ Rule ID | DTag |W|C|  Bitmap  |P1]
        Format: [ Rule ID | DTag |W| All-1 |  FF  |P1]
    '''
    def __init__(self, recvbuf, rule, dtag, win):
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
        pos += self.parse_cbit(pos)
        if self.cbit == 0:
            pos += self.parse_bitmap(pos)

class frag_sender_rx(frag_rx):

    '''
    message format received by the fragment sender.
        ACK-OK : [ Rule ID | DTag |W|C-1| Pad-0 ]
        ACK-NG : [ Rule ID | DTag |W|C-0| Bitmap | Pad-0 ]
        R-Abort: [ Rule ID | DTag |W|C-1| Pad-1 |
    '''
    def __init__(self, rule, recvbuf):
        '''
        recvbuf: buffer received in bytearray().
        rule: rule instance.
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.rule = rule
        pos = rule["ruleLength"] + rule["dtagSize"]
        pos += self.parse_win()
        # XXX the abort is not supported yet.
        pos += self.parse_cbit(pos)
        if self.cbit == 0:
            pos += self.parse_bitmap(pos)

class frag_receiver_rx(frag_rx):

    '''
    for the fragment receiver to receive the message.
    if FCN is All-0,
        Format: [ Rule ID | DTag |W|FCN|P1][ Payload |P2]
        Format: [ Rule ID | DTag |W|FCN|P1]
    if FCN is All-1,
        Format: [ Rule ID | DTag |W|FCN|  MIC   |P1][ Payload |P2]
        Format: [ Rule ID | DTag |W|FCN|  MIC   |P1]
    Otherwise,
        Format: [ Rule ID | DTag |W|FCN|P1][ Payload |P2]
    XXX Abort message is not supported yet.
        Format: [ Rule ID | DTag |W|FCN|  FF    |P1]
    XXX P1 is not approved in the WG.
    '''
    def __init__(self, rule, recvbuf):
        # XXX for now, C refers to rule itself.
        '''
        C: runtime context.
        recvbuf: buffer received in BitBuffer().
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.rule = rule
        self.rule_id = self.packet_bbuf.get_bits(rule["ruleLength"])
        pos = self.rule["ruleLength"]
        pos += self.parse_dtag()
        pos += self.parse_win()
        pos += self.parse_fcn(pos)
        if self.fcn == get_fcn_all_1(self.rule):
            pos += self.parse_mic(pos)
        self.payload = self.packet_bbuf.copy()
