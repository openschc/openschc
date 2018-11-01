
#from __future__ import print_function

import pybinutil as pb
from schc_param import *

'''
NOTE:
    the boundary of the fragment header is alligned to the byte boundary.
    XXX how do I have to handle the padding ?
'''

class frag_holder():
    '''
    base class for operation of message.
    packet: a bytearray transmitted or a bytearray received.
    '''
    def init_param(self):
        self.rid = None
        self.dtag = None
        self.win = None
        self.fcn = None
        self.mic = None
        self.bitmap = None
        self.cbit = None
        self.payload = None
        self.packet = None

    def set_param(self, rid, dtag, win, fcn, mic, bitmap, cbit, payload):
        self.rid = rid
        self.dtag = dtag
        self.win = win
        self.fcn = fcn
        self.mic = mic
        self.bitmap = bitmap
        self.cbit = cbit
        self.payload = payload
        # check the field size.
        if dtag > (2**self.R.dtag_size) - 1:
            raise ValueError("dtag is too big than the field size.")

    def dump(self):
        x = ""
        if self.rid != None:
            x += ("rid:%s" % pb.int_to_bit(self.rid, self.R.C.rid_size))
        if self.dtag != None:
            if len(x) != 0: x += " "
            x += ("dtag:%s" % pb.int_to_bit(self.dtag, self.R.dtag_size))
        if self.win != None:
            if len(x) != 0: x += " "
            x += ("w:%d" % self.win)
        if self.fcn != None:
            if len(x) != 0: x += " "
            x += ("fcn:%s" % pb.int_to_bit(self.fcn, self.R.fcn_size))
        if self.mic != None:
            if len(x) != 0: x += " "
            x += ("mic:%s" % pb.int_to_bit(self.mic, self.R.C.mic_size))
            x += ("(0x%s)" % "".join(["%02x"%((self.mic>>i)&0xff)
                                     for i in [24,16,8,0]]))
        if self.cbit != None:
            if len(x) != 0: x += " "
            x += ("cbit:%d" % self.cbit)
        if self.bitmap != None:
            if len(x) != 0: x += " "
            x += ("bitmap:%s" % pb.int_to_bit(self.bitmap, self.R.bitmap_size))
        if self.payload != None:
            if len(x) != 0: x += " "
            x += ("payload:%s" % self.payload)
        #
        return x

    def full_dump(self):
        return " ".join(["%02x"%i for i in self.packet])

class frag_tx(frag_holder):

    '''
    parent class for sending message.
    '''
    def make_frag(self, dtag, win=None, fcn=None, mic=None, bitmap=None,
                  cbit=None, abort=False, payload=None):
        '''
        payload: bit string of the SCHC fragment payload.
        '''
        #
        ba = bytearray()
        pos = 0
        #
        # basic fields.
        if self.R.rid != None and self.R.C.rid_size:
            pb.bit_set(ba, 0, pb.int_to_bit(self.R.rid, self.R.C.rid_size),
                       extend=True)
            pos += self.R.C.rid_size
        if dtag != None and self.R.dtag_size:
            pb.bit_set(ba, pos, pb.int_to_bit(dtag, self.R.dtag_size),
                       extend=True)
            pos += self.R.dtag_size
        #
        # extension fields.
        if win != None and self.R.win_size:
            pb.bit_set(ba, pos, pb.int_to_bit(win, self.R.win_size),
                       extend=True)
            pos += self.R.win_size
        if fcn != None and self.R.fcn_size:
            pb.bit_set(ba, pos, pb.int_to_bit(fcn, self.R.fcn_size),
                       extend=True)
            pos += self.R.fcn_size
        if mic != None and self.R.C.mic_size:
            pb.bit_set(ba, pos, pb.int_to_bit(mic, self.R.C.mic_size),
                       extend=True)
            pos += self.R.C.mic_size
        if cbit != None and self.R.cbit_size:
            pb.bit_set(ba, pos, pb.int_to_bit(cbit, self.R.cbit_size),
                       extend=True)
            pos += self.R.cbit_size
        if bitmap != None and self.R.bitmap_size:
            pb.bit_set(ba, pos, pb.int_to_bit(bitmap, self.R.bitmap_size),
                       extend=True)
            pos += self.R.bitmap_size
        if abort == True:
            pb.bit_set(ba, pos, pb.int_to_bit(0xff, 8),
                       extend=True)
            pos += 8
        #
        if payload != None:
            # assumed that bit_set() has extended to a byte boundary.
            pb.bit_set(ba, pos, payload, extend=True)
        #
        # the abort field is implicit, is not needed to set into the parameter.
        self.set_param(self.R.rid, dtag, win, fcn, mic, bitmap, cbit, payload)
        self.packet = ba

class frag_sender_tx(frag_tx):

    '''
    for the fragment sender to send a message.
    '''
    def __init__(self, R, dtag, win=None, fcn=None, mic=None, bitmap=None,
                 cbit=None, payload=None):
        self.init_param()
        self.R = R
        self.make_frag(dtag, win=win, fcn=fcn, mic=mic, bitmap=bitmap,
                       cbit=cbit, payload=payload)

class frag_receiver_tx_all0_ack(frag_tx):

    '''
    for the fragment receiver, to make an all0 ack.
        Format: [ Rule ID | DTag |W|  Bitmap  |P1]
    '''
    def __init__(self, R, dtag, win=None, bitmap=None):
        self.init_param()
        self.R = R
        self.make_frag(dtag, win=win, bitmap=bitmap)

class frag_receiver_tx_all1_ack(frag_tx):

    '''
    for the fragment receiver, to make an all1 ack.
        Format: [ Rule ID | DTag |W|C|P1]
        Format: [ Rule ID | DTag |W|C|  Bitmap  |P1]
    '''
    def __init__(self, R, dtag, win=None, cbit=None, bitmap=None):
        self.init_param()
        self.R = R
        self.make_frag(dtag, win=win, cbit=cbit, bitmap=bitmap)

class frag_receiver_tx_abort(frag_tx):

    '''
    for the fragment receiver, to make an abort message.
        Format: [ Rule ID | DTag |W|0xFF|P1]
    '''
    def __init__(self, R, dtag, win=None, cbit=None, bitmap=None):
        self.init_param()
        self.R = R
        self.make_frag(dtag, win=win, abort=True)

class frag_rx(frag_holder):

    '''
    parent class for receiving message.
    recvbuf: str, bytes, bytearray.
    '''
    def set_recvbuf(self, recvbuf):
        if type(recvbuf) == str:
            self.packet = bytearray(recvbuf, encoding="utf-8")
        elif type(recvbuf) in [bytearray, bytes]:
            self.packet = bytearray(recvbuf)
        else:
            raise TypeError("recvbuf must be str, bytes or bytearray.")

    def parse_rid(self, C, exp_rid=None):
        '''
        parse rid in the frame.
        exp_rid: if non-None, check the rid whether it's expected.
        '''
        if C.rid_size:
            rid = pb.bit_get(self.packet, 0, C.rid_size, ret_type=int)
            if exp_rid != None and rid != exp_rid:
                raise ValueError("rid unexpected.")
        else:
            rid = C.default_rid
        #
        self.rid = rid
        return C.rid_size

    def parse_dtag(self, pos, exp_dtag=None):
        '''
        parse dtag in the frame.
        exp_dtag: if non-None, check the dtag whether it is expected.
        '''
        if self.R.dtag_size:
            dtag = pb.bit_get(self.packet, pos, self.R.dtag_size, ret_type=int)
            if exp_dtag != None and dtag != exp_dtag:
                raise ValueError("dtag unexpected.")
        else:
            dtag = self.R.C.default_dtag
        #
        self.dtag = dtag
        return self.R.dtag_size

    def parse_win(self, pos, exp_win=None):
        '''
        parse win in the frame.
        exp_win: if non-None, check the win whether it is expected.
        if win_size is zero, self.win is not set.
        '''
        if self.R.win_size:
            win = pb.bit_get(self.packet, pos, self.R.win_size, ret_type=int)
            if exp_win != None and win != exp_win:
                raise ValueError("the value of win unexpected. win=%d expected=%d" % (win, exp_win))
            self.win = win
        return self.R.win_size

    def parse_fcn(self, pos):
        '''
        parse fcn in the frame.
        assuming that fcn_size is not zero.
        '''
        self.fcn = pb.bit_get(self.packet, pos, self.R.fcn_size, ret_type=int)
        return self.R.fcn_size

    def parse_bitmap(self, pos):
        '''
        parse bitmap in the frame.
        assuming that bitmap_size is not zero.
        '''
        self.bitmap = pb.bit_get(self.packet, pos, self.R.bitmap_size,
                                 ret_type=int)
        return self.R.bitmap_size

    def parse_cbit(self, pos):
        '''
        parse cbit in the frame.
        assuming that cbit_size is not zero.
        '''
        self.cbit = pb.bit_get(self.packet, pos, self.R.cbit_size, ret_type=int)
        return self.R.cbit_size

    def parse_mic(self, pos):
        '''
        parse mic in the frame.
        assuming that mic_size is not zero.
        '''
        self.mic = pb.bit_get(self.packet, pos, self.R.C.mic_size, ret_type=int)
        return self.R.C.mic_size

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
    def __init__(self, recvbuf, R, dtag, win):
        '''
        recvbuf: buffer received in bytearray().
        R: rule instance.
        '''
        self.init_param()
        self.set_recvbuf(recvbuf)
        self.R = R
        pos = 0
        pos += self.parse_rid(self.R.C, exp_rid=self.R.rid)
        pos += self.parse_dtag(pos, exp_dtag=dtag)
        pos += self.parse_win(pos, exp_win=win)
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
        self.R = R
        pos = 0
        pos += self.parse_rid(self.R.C, exp_rid=self.R.rid)
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
        self.__pos += self.parse_rid(C)

    def finalize(self, R):
        self.R = R
        pos = self.__pos
        pos += self.parse_dtag(pos)
        pos += self.parse_win(pos)
        pos += self.parse_fcn(pos)
        if self.fcn == self.R.fcn_all_1:
            pos += self.parse_mic(pos)
        payload_bit_len = len(self.packet)*8 - pos
        self.payload = pb.bit_get(self.packet, pos, payload_bit_len)

