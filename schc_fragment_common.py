
from __future__ import print_function

from pybinutil import *

SCHC_MODE_NO_ACK = 0
SCHC_MODE_WIN_ACK_ALWAYS = 1
SCHC_MODE_WIN_ACK_ON_ERROR = 2

'''
NOTE:
    the boundary of the fragment header is alligned to a byte.
    XXX how do I have to handle the padding ?

    rule_id must be negotiated between the nodes in out-of-band
    before they start communication.
'''

# rule is defined at the other place.
context01 = {
    "rid_pos": 0,
    "rid_size": 0,
}

rule01 = {
    "rid": 1,
    "mode": SCHC_MODE_WIN_ACK_ALWAYS,
    "dtag_size": 0,
    "win_size": 1,
    "fcn_size": 3,
    "bitmap_size": 7,
    "mic_size": 8,
    }

default_rule = 1
default_dtag = 0

def default_logger(*arg):
    pass

class schc_context:
    def __init__(self, cid):
        # XXX need to be better to get a context.
        # something like
        # selc.C = schc_context_get(cid)
        self.C = context01
        #
        self.rid_pos = context01["rid_pos"]
        self.rid_size = context01["rid_size"]

class schc_rule:
    R = None
    def __init__(self, context, rid):
        '''
        context: context instance
        rid: rule id
        '''
        # XXX need to be better to get a rule.
        # XXX schc_rule instance is more likey to keep the static information.
        if rid == 0:
            self.R = rule01
        else:
            # XXX something like below
            # self.R = schc_rule_get(rid)
            pass
        #
        self.rid = self.R["rid"]
        self.mode = self.R["mode"]
        self.rid_size = context.rid_size
        self.dtag_size = self.R["dtag_size"]
        self.win_size = self.R["win_size"]
        self.fcn_size = self.R["fcn_size"]
        self.bitmap_size = self.R["bitmap_size"]
        self.mic_size = self.R["mic_size"]
        #
        # set the postion of each field.
        self.rid_pos = context.rid_pos
        self.dtag_pos = self.rid_pos + self.dtag_size
        self.win_pos = self.dtag_pos + self.dtag_size
        self.fcn_pos = self.win_pos + self.win_size
        self.bitmap_pos = self.win_pos + self.win_size
        self.mic_pos = self.bitmap_pos + self.bitmap_size
        self.payload_pos = self.fcn_pos + self.fcn_size
        self.last_payload_pos = self.mic_pos + self.mic_size

        # XXX sanity check of the rule should be at the different place.
        # check rule_id size
        if rid > (2**self.rid_size)-1:
            raise ValueError("rule_id is too big for the rule id field.")
        #
        # check the bitmap size and fcn size
        self.max_fcn = self.bitmap_size - 1
        if self.max_fcn > (2**self.fcn_size)-1:
            raise ValueError("fcn_size is too small for the bitmap.")
        self.fcn_all_1 = (1<<self.fcn_size)-1
        self.fcn_all_0 = 0
        self.bitmap_all_1 = (2**self.bitmap_size)-1
        #
        #
        # the fragment header is assumed to be aligned to a byte.
        self.hdr_size = (self.rid_size + self.dtag_size + self.win_size +
                         self.fcn_size)
        self.ack_hdr_size = (self.rid_size + self.dtag_size + self.win_size)

class schc_fragment_holder:

    R = None
    buf = None
    dtag = None
    bitmap = None   # hold as a bin string
    mic = None      # XXX hold as a bin string, should it ?
    rid = None

    def __init__(self, context, recvbuf=None, rule=None, dtag=None, fgh=None,
                 ack=False, logger=default_logger):
        '''
        context: context instance.
        recvbuf: buffer received.
        rule: rule to be applied.
        fgh: schc_fragment_holder received from the fragment sender.

        self.hdr_size is the buffer size.
                            hdr_size     buf_size
                               |            |
                               v            v
            buf |............................
        '''
        if fgh is not None:
            # making ack for the fragment receiver.
            self.set_val_ack(context, fgh=fgh)
        elif ack:
            # getting ack for the fragment sender.
            self.get_val_ack(context, recvbuf)
        elif rule is not None:
            # for the fragment sender.
            self.set_val(context, rule, dtag=dtag)
        elif recvbuf is not None:
            # for the fragment receiver.
            self.get_val(context, recvbuf)
        else:
            raise ValueError("either recvbuf or rule must be specified.")

    def set_val(self, context, rule, dtag=None):
        # for the fragment sender.
        self.C = context
        self.R = rule
        #
        buf_size = (self.R.hdr_size>>3)+(1 if self.R.hdr_size%8 else 0)
        self.buf = bytearray(buf_size)
        self.dtag = dtag
        #
        if self.R.rid_size:
            pybinutil.bitset(self.buf, self.R.rid_pos,
                pybinutil.int_to_bit(self.R.rid, self.R.rid_size))
        if self.R.dtag_size:
            self.set_dtag(dtag)
        #
        # the win bit is gonna be set later.

    def set_val_ack(self, context, fgh=None):
        # making ack for the fragment receiver.
        self.C = context
        self.R = fgh.R
        #
        if self.R.mode == SCHC_MODE_NO_ACK:
            raise AssertionError("no-ack mode must not come here in set_val_ack().")
        #
        buf_size = (self.R.ack_hdr_size>>3)+(1 if self.R.ack_hdr_size%8 else 0)
        self.buf = bytearray(buf_size)
        #
        if self.R.rid_size:
            pybinutil.bitset(self.buf, self.R.rid_pos,
                pybinutil.int_to_bit(self.R.rid, self.R.rid_size))
        if self.R.dtag_size:
            self.set_dtag(self.fgh.dtag)
        #
        self.set_win_ack(fgh.win)

    def _get_val_base(self, context, recvbuf):
        self.C = context
        if self.C.rid_size:
            self.rid = pybinutil.bitget(recvbuf, self.C.rid_pos,
                                        self.C.rid_size, integer=True)
            self.R = schc_rule(context, self.rid)
        else:
            self.R = schc_rule(context, 0)  # default
        #
        if self.R.dtag_size:
            self.dtag = pybinutil.bitget(recvbuf, self.R.dtag_pos,
                                        self.R.dtag_size, integer=True)
        else:
            self.dtag = default_dtag
        #
        if self.R.mode != SCHC_MODE_NO_ACK:
            self.win = pybinutil.bitget(recvbuf, self.R.win_pos,
                                        self.R.win_size, integer=True)

    def get_val(self, context, recvbuf):
        # for the fragment receiver.
        self._get_val_base(context, recvbuf)
        #
        self.fcn = pybinutil.bitget(recvbuf, self.R.fcn_pos,
                                    self.R.fcn_size, integer=True)
        #
        if self.fcn == self.R.fcn_all_1:
            self.mic = pybinutil.bitget(recvbuf, self.R.mic_pos,
                                        self.R.mic_size, integer=True)
        # XXX assuming the header is aligned to the byte boundary.
        i = (self.R.hdr_size>>3) + (1 if self.R.hdr_size%8 else 0)
        self.payload = recvbuf[i:]
        self.buf = recvbuf  # place holder

    def get_val_ack(self, context, recvbuf):
        # getting ack for the fragment sender.
        self._get_val_base(context, recvbuf)
        if self.R.mode == SCHC_MODE_NO_ACK:
            raise AssertionError("no-ack mode must not come here in get_val_ack().")
        self.bitmap = pybinutil.bitget(recvbuf, self.R.bitmap_pos,
                                        self.R.bitmap_size, integer=True)

    def set_dtag(self, dtag):
        if self.R.dtag_size:
            pybinutil.bitset(self.buf, self.R.dtag_pos,
                pybinutil.int_to_bit(dtag, self.R.dtag_size))

    def set_fcn(self, fcn):
        pybinutil.bitset(self.buf, self.R.fcn_pos,
               pybinutil.int_to_bit(fcn, self.R.fcn_size))

    def set_win(self, win):
        pybinutil.bitset(self.buf, self.R.win_pos,
            pybinutil.int_to_bit(win, self.R.win_size))

    def set_win_ack(self, win):
        # assuming that self.R exists already.
        # set it into buf
        pybinutil.bitset(self.buf, self.R.win_pos,
            pybinutil.int_to_bit(win, self.R.win_size))

    def set_bitmap(self, bitmap):
        # assuming that self.R exists already.
        # set it into buf
        pybinutil.bitset(self.buf, self.R.bitmap_pos,
            pybinutil.int_to_bit(bitmap, self.R.bitmap_size))

    def add_payload(self, payload, mic=None):
        '''
        payload, mic must be bytearray().
        '''
        buf_size = self.R.hdr_size + len(mic) + 8*len(payload)
        # XXX
        # need to be improved.
        #size = (buf_size>>3)+(1 if buf_size%8 else 0)
        # assumed that them are aligned to the byte boundary.
        new = self.buf[:]
        if mic:
            new += mic
        new += payload
        return new

    def dump(self, packet=None, ack=False, mic=False):
        '''
        ack: if ack is False, the packet is either
             to be passed by the sender when it sends the packet,
             or by the receiver when it receives the packet.
             if ack is True, the packet is either
             to be passed by the sender when it receives the packet as ack,
             or by the receiver when it sends the packet as ack.
        '''
        rid = pybinutil.bitget(self.buf, self.R.rid_pos, self.R.rid_size,
                               integer=True)
        dtag = pybinutil.bitget(self.buf, self.R.dtag_pos, self.R.dtag_size,
                                integer=True)
        ret = "rid:%s dtag:%s" % (rid, dtag)
        if self.R.mode != SCHC_MODE_NO_ACK:
            ret += " win:%s" % pybinutil.bitget(self.buf, self.R.win_pos,
                                                self.R.win_size, integer=True)
        if ack:
            ret += " bitmap:%s" % pybinutil.bitget(self.buf, self.R.mic_pos,
                                                   self.R.mic_size)
        else:
            ret += " fcn:%s" % pybinutil.bitget(self.buf, self.R.fcn_pos,
                                                self.R.fcn_size, integer=True)
        if mic:
            ret += " mic:%s" % pybinutil.bitget(self.buf, self.R.mic_pos,
                                                self.R.mic_size)
        #
        return ret

class schc_state_holder:
    state = None
    state_prev = None

    def __init__(self, state=None, logger=default_logger):
        self.state = state
        self.logger = logger

    def set(self, new_state):
        self.state_prev = self.state
        self.state = new_state
        self.logger(1, "state: ", self.state_prev, "->", self.state)
        return self.state

    def back(self):
        self.logger(1, "state: ", self.state, "->", self.state_prev)
        self.state = self.state_prev
        self.state_prev = None
        return self.state

    def get(self):
        return self.state

