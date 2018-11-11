
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
    return (1<<rule.fcn_size)-1

def get_MAX_WIND_FCN(rule):
    return (1<<rule.fcn_size)-2

def get_max_dtag(rule):
    return (1<<rule.dtag_size)-1

def get_header_size(rule):
    return rule.rule_id_size + rule.dtag_size + rule.window_size + rule.fcn_size

def get_mic_size_in_bits(rule):
    assert rule.mic_algorithm == "crc32"
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
        if dtag > (2**self.rule.dtag_size) - 1:
            raise ValueError("dtag is too big than the field size.")

    def dump(self):
        x = ""
        if self.rule_id != None:
            x += ("rule_id:%s" % pb.int_to_bit(self.rule_id, self.rule.rule_id_size))
        if self.dtag != None:
            if len(x) != 0: x += " "
            x += ("dtag:%s" % pb.int_to_bit(self.dtag, self.rule.dtag_size))
        if self.win != None:
            if len(x) != 0: x += " "
            x += ("w:%d" % self.win)
        if self.fcn != None:
            if len(x) != 0: x += " "
            x += ("fcn:%s" % pb.int_to_bit(self.fcn, self.rule.fcn_size))
        if self.mic != None:
            if len(x) != 0: x += " "
            x += ("mic:%s" % pb.int_to_bit(self.mic, self.rule.mic_size))
            x += ("(0x%s)" % "".join(["%02x"%((self.mic>>i)&0xff)
                                     for i in [24,16,8,0]]))
        if self.cbit != None:
            if len(x) != 0: x += " "
            x += ("cbit:%d" % self.cbit)
        if self.bitmap != None:
            if len(x) != 0: x += " "
            x += ("bitmap:%s" % pb.int_to_bit(self.bitmap, self.rule.bitmap_size))
        if self.payload != None:
            if len(x) != 0: x += " "
            x += ("payload:%s" % self.payload)
        #
        return x

    def full_dump(self):
        return " ".join(["%02x"%i for i in self.packet])

class frag_tx(frag_base):

    '''
    parent class for sending message.
    '''
    def make_frag(self, dtag, win=None, fcn=None, mic=None, bitmap=None,
                  cbit=None, abort=False, payload=None):
        '''
        payload: bytearray of the SCHC fragment payload.
        '''
        #
        buffer = BitBuffer()
        #
        # basic fields.
        if self.rule.rule_id is not None and self.rule.rule_id_size is not None:
            buffer.add_bits(self.rule.rule_id, self.rule.rule_id_size)
        if dtag is not None and self.rule.dtag_size is not None:
            assert self.rule.dtag_size != None # CA: sanity check
            buffer.add_bits(dtag, self.rule.dtag_size)
        #
        # extension fields.
        if win is not None and self.rule.window_size is not None:
            buffer.add_bits(win, self.rule.window_size)
        if fcn is not None and self.rule.fcn_size is not None:
            buffer.add_bits(fcn, self.rule.fcn_size)
        if mic != None and self.rule.mic_algorithm is not None:
            mic_size = get_mic_size_in_bits(self.rule)
            assert mic_size % bitarray.BITS_PER_BYTE == 0
            assert len(mic) == mic_size // 8
            buffer.add_bytes(mic)
        if cbit != None:
            buffer.set_bit(cbit)
        if bitmap != None and self.rule.bitmap_size:
            buffer.add_bits(bitmap, self.rule.bitmap_size)
        if abort == True:
            raise RunTimeError("not refactored", "abort == True")
            pb.bit_set(ba, pos, pb.int_to_bit(0xff, 8), extend=True)
            pos += 8
        #
        if payload != None:
            # assumed that bit_set() has extended to a byte boundary
            buffer.add_bytes(payload)
        #
        # the abort field is implicit, is not needed to set into the parameter.
        self.set_param(self.rule_id, dtag, win, fcn, mic, bitmap, cbit, payload)
        self.packet = buffer

class frag_sender_tx(frag_tx):

    '''
    for the fragment sender to send a message.
    '''
    def __init__(self, rule, rule_id, dtag, win=None, fcn=None, mic=None,
                 bitmap=None, cbit=None, payload=None):
        self.init_param()
        self.rule = rule
        self.rule_id = rule_id
        self.make_frag(dtag, win=win, fcn=fcn, mic=mic, bitmap=bitmap,
                       cbit=cbit, payload=payload)

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
        self.packet = recvbuf
        return # XXX: remove the rest
        if type(recvbuf) == str:
            self.packet = bytearray(recvbuf, encoding="utf-8")
        elif type(recvbuf) in [bytearray, bytes]:
            self.packet = bytearray(recvbuf)
        else:
            raise TypeError("recvbuf must be str, bytes or bytearray.")

    def parse_rule_id(self, C, exp_rule_id=None):
        '''
        parse rule_id in the frame.
        exp_rule_id: if non-None, check the rule_id whether it's expected.
        '''
        if C.rule_id_size:
            rule_id = self.packet.get_bits(C.rule_id_size)
            if exp_rule_id != None and rule_id != exp_rule_id:
                raise ValueError("rule_id unexpected.")
        else:
            rule_id = C.default_rule_id
        #
        self.rule_id = rule_id
        return C.rule_id_size

    def parse_dtag(self, pos, exp_dtag=None):
        '''
        parse dtag in the frame.
        exp_dtag: if non-None, check the dtag whether it is expected.
        '''
        if self.rule.dtag_size:
            dtag = self.packet.get_bits(self.rule.dtag_size)
            if exp_dtag != None and dtag != exp_dtag:
                raise ValueError("dtag unexpected.")
        else:
            dtag = self.rule.C.default_dtag
        #
        self.dtag = dtag
        return self.rule.dtag_size

    def parse_win(self, pos, exp_win=None):
        '''
        parse win in the frame.
        exp_win: if non-None, check the win whether it is expected.
        if window_size is zero, self.win is not set.
        '''
        if self.rule.window_size:
            win = self.packet.get_bits(self.rule.window_size)
            if exp_win is not None and win is not exp_win:
                raise ValueError("the value of win unexpected. win=%d expected=%d" % (win, exp_win))
            self.win = win
        return self.rule.window_size

    def parse_fcn(self, pos):
        '''
        parse fcn in the frame.
        assuming that fcn_size is not zero.
        '''
        self.fcn = self.packet.get_bits(self.rule.fcn_size)
        return self.rule.fcn_size

    def parse_bitmap(self, pos):
        '''
        parse bitmap in the frame.
        assuming that bitmap_size is not zero.
        '''
        self.bitmap = pb.bit_get(self.packet, pos, self.rule.bitmap_size,
                                 ret_type=int)
        return self.rule.bitmap_size

    def parse_cbit(self, pos):
        '''
        parse cbit in the frame.
        '''
        self.cbit = pb.bit_get(self.packet, pos, 1, ret_type=int)
        return 1

    def parse_mic(self, pos):
        '''
        parse mic in the frame.
        assuming that mic_size is not zero.
        '''
        mic_size = get_mic_size_in_bits(self.rule)
        self.mic = self.packet.get_bits(mic_size)
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
    def __init__(self, recvbuf, R, dtag, exp_win=None):
        '''
        recvbuf: buffer received in bytearray().
        R: rule instance.
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.rule = R
        pos = 0
        pos += self.parse_rule_id(self.rule.C, exp_rule_id=self.rule.rule_id)
        pos += self.parse_dtag(pos, exp_dtag=dtag)
        pos += self.parse_win(pos, exp_win=exp_win)
        # XXX the abort is not supported yet.
        pos += self.parse_bitmap(pos)

class frag_sender_rx_all1_ack(frag_rx):

    '''
    for the fragment sender to receive the all1 ack.
        Format: [ Rule ID | DTag |W|C|P1]
        Format: [ Rule ID | DTag |W|C|  Bitmap  |P1]
        Format: [ Rule ID | DTag |W| All-1 |  FF  |P1]
    '''
    def __init__(self, recvbuf, R, dtag, win):
        '''
        recvbuf: buffer received in bytearray().
        R: rule instance.
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.rule = R
        pos = 0
        pos += self.parse_rule_id(self.rule.C, exp_rule_id=self.rule.rule_id)
        pos += self.parse_dtag(pos, exp_dtag=dtag)
        pos += self.parse_win(pos, exp_win=win)
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
    def __init__(self, recvbuf, R, dtag, win):
        '''
        recvbuf: buffer received in bytearray().
        R: rule instance.
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.rule = R
        pos = 0
        pos += self.parse_rule_id(self.rule.C, exp_rule_id=self.rule.rule_id)
        pos += self.parse_dtag(pos, exp_dtag=dtag)
        pos += self.parse_win(pos, exp_win=win)
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
    def __init__(self, C, recvbuf):
        '''
        C: runtime context.
        recvbuf: buffer received in bytearray().
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.__pos = 0
        self.__pos += self.parse_rule_id(C)

    def finalize(self, R):
        self.rule = R
        pos = self.__pos
        pos += self.parse_dtag(pos)
        pos += self.parse_win(pos)
        pos += self.parse_fcn(pos)
        if self.fcn == get_fcn_all_1(self.rule):
            pos += self.parse_mic(pos)
        payload_bit_len = self.packet.count_remaining_bits()
        self.payload = self.packet.get_bits_as_buffer(payload_bit_len)
