MICROPYTHON = True

import pybinutil as pb
from schc_param import *
import schc_fragment_state as sfs
import schc_fragment_holder as sfh
from schc_fragment_ruledb import schc_fragment_ruledb
import micro_enum
if not MICROPYTHON:
    from random import randint

STATE = micro_enum.enum(
    FAIL = -1,
    INIT = 0,
    CONT = 1,
    SEND_ALL0 = 7,
    RETRY_ALL0 = 8,
    WIN_DONE = 9,
    SEND_ALL1 = 11,
    RETRY_ALL1 = 12,
    DONE = 19
    )

def default_logger(*arg):
    pass

def rdu8(a):
    '''
    a: a size in bit.
    return a size in byte.
    '''
    return ((a+7)&(~7))>>3

class fragment_factory:

    def __init__(self, R, logger=default_logger):
        '''
        R: fragment runtime rule.
        '''
        self.R = R
        self.logger = logger
        #
        self.logger(1, "mode={0:d}".format(self.R.mode))
        #self.logger(1, "each field size: rid={0} dtag={self.dtag_size} win={self.win_size} fcn={self.fcn_size} bitmap={self.bitmap_size} cbit={self.cbit_size} mic={self.C.mic_size}".format(self.R.C.rid_size, self=self.R))

    def __init_window(self):
        '''
        fgh_list: maintain the fragments in a window.
        '''
        self.bitmap = 0
        self.missing = 0
        self.missing_prev = 0
        self.fgh_list = {}
        self.fcn = None
        # only use in NO_ACK mode
        self.n_frags_sent = 0

    def setbuf(self, srcbuf, dtag=None):
        '''
        srcbuf: holder of the data to be sent.
        dtag: dtag number. taken randomly if None.
        win_head: indicating the head of current window.
                 it is held until the bitmap check is completed.
        pos: indicating the head of the data to be sent.

                   win_head        pos
                      |             |
                      v             v
        srcbuf |.........................
        '''
        if type(srcbuf) == str:
#            self.srcbuf = bytearray(srcbuf, "utf-8")
            self.srcbuf = bytearray(srcbuf)
        elif type(srcbuf) in [bytearray, bytes]:
            self.srcbuf = bytearray(recvbuf)
        else:
            raise TypeError("srcbuf must be str, bytes or bytearray.")
        #
        self.win_head = 0
        self.pos = 0
        self.dtag = dtag
        if self.dtag == None:
            if not MICROPYTHON:
                self.dtag = randint(0, (2**self.R.dtag_size)-1)
            else:
                # should use counter here
                self.dtag = 3
        self.mic, self.mic_size = self.R.C.mic_func.get_mic(self.srcbuf)
        self.win = 0
        self.__init_window()
        self.state = sfs.fragment_state(STATE, logger=self.logger)
        self.state.set(STATE.INIT)

    def get_payload_base_size(self, l2_size):
        h = self.R.C.rid_size + self.R.dtag_size + self.R.fcn_size
        max_pyld_size = rdu8(l2_size*8 - h)
        min_pyld_size = rdu8(l2_size*8 - h - self.mic_size)
        if max_pyld_size < 1:
            raise AssertionError("L2 size is too small than header. hdr=%d L2=%d" % (h, l2_size*8))
        if min_pyld_size < 1:
            raise AssertionError("L2 size is too small for mic. hdr+mic=%d L2=%d" % (h+self.mic_size, l2_size*8))
        return max_pyld_size, min_pyld_size

    def next_fragment(self, l2_size):
        '''
        l2_size: the caller can specify the size of the payload anytime.

        XXX Note that it doesn't care the l2_size in retransmitting.
        if the size is changed in that case,
        the packet will not be changed as it was.  needs to be improved.
        '''
        # compute the max/min payload size.
        max_pyld_size, min_pyld_size = self.get_payload_base_size(l2_size)
        #
        if self.R.mode == SCHC_MODE.NO_ACK and self.state.get() == STATE.SEND_ALL1:
            # no more fragments to be sent
            return self.state.set(STATE.DONE), None

        #
        if self.state.get() == STATE.SEND_ALL0:
            # it comes here when the timeout happens while waiting for the
            # ack response from the receiver even though either all-0 was sent.
            if self.R.mode == SCHC_MODE.ACK_ALWAYS:
                self.missing = self.missing_prev
                self.state.set(STATE.RETRY_ALL0)
            else:
                # here, for ACK-ON-ERROR
                self.state.set(STATE.WIN_DONE)
                pass
        elif self.state.get() == STATE.SEND_ALL1:
            # here, the case the sender sent all-1, but no response from the
            # receiver.
            self.missing = self.missing_prev
            self.state.set(STATE.RETRY_ALL1)
        #
        if self.state.get() in [STATE.RETRY_ALL0, STATE.RETRY_ALL1]:
            # if all the missing fragments has been sent, resend the empty ALL.
            if self.missing == 0:
                # set the state into the previous one.
                self.state.back()
                if self.state.get() == STATE.SEND_ALL0:
                    fgh = sfh.frag_sender_tx(self.R, self.dtag, win=self.win,
                                             fcn=self.R.fcn_all_0)
                elif self.state.get() == STATE.SEND_ALL1:
                    fgh = sfh.frag_sender_tx(self.R, self.dtag, win=self.win,
                                             fcn=self.R.fcn_all_1, mic=self.mic)
                else:
                    AssertionError("invalid state in retransmission %s" %
                                   self.state.get())
                #
                return self.state.get(), fgh
            # if there are any missing fragments,
            # the sender only needs to send missed fragments.
            # doesn't need to send all-0/all1.
            if self.R.mode == SCHC_MODE.NO_ACK:
                raise AssertionError("no-ack mode must not come here in next_fragment().")
            # e.g. N=3, Max FCN = 7
            #   all-0
            #     bit: 1 2 3 4 5 6 7
            #     fcn: 6 5 4 3 2 1 0
            #   all-1
            #     bit: 1 2 3 4 5 6 7
            #     fcn: 6 5         7
            p, self.missing = pb.bit_find(self.missing, self.R.bitmap_size)
            self.logger(1, "retransmitting.",
                        "fgh_list=", self.fgh_list.keys(), "p=", p, "missing=",
                        pb.int_to_bit(self.missing,self.R.bitmap_size))
            if p == None or p > self.R.max_fcn:
                raise AssertionError("in missing check, p must be from 1 to %d"
                                     % self.R.max_fcn)
            if p == self.R.max_fcn:
                if self.state.get() == STATE.RETRY_ALL0:
                    fgh = self.fgh_list[self.R.fcn_all_0]
                else:
                    # i.e. SCHC_FRAG_RETRY_ALL1
                    fgh = self.fgh_list[self.R.fcn_all_1]
            else:
                fgh = self.fgh_list[self.R.max_fcn - p]
            # in others, return CONT,
            # however don't need to change the internal state.
            # i.e RETRY_ALL0 or RETRY_ALL1.
            return STATE.CONT, fgh
        #
        # defragment for transmitting.
        #
        rest_size = len(self.srcbuf) - self.pos
        if self.R.mode == SCHC_MODE.NO_ACK:
            if rest_size > min_pyld_size:
                if rest_size >= max_pyld_size:
                    pyld_size = max_pyld_size
                else:
                    pyld_size = rest_size
                self.fcn = 0
                mic = None
                state = STATE.CONT
            else:
                # this is the last fragment.
                pyld_size = rest_size
                self.fcn = 1
                mic = self.mic
                state = STATE.SEND_ALL1
            #
            fgh = sfh.frag_sender_tx(self.R, self.dtag,
                            fcn=self.fcn, mic=mic,
                            payload=self.srcbuf[self.pos:self.pos+pyld_size])
            self.state.set(state)
            self.n_frags_sent += 1
            self.pos += pyld_size
            return self.state.get(), fgh
        else:
            if self.state.get() == STATE.WIN_DONE:
                # try to support more than 1 bit wide window
                # though the bit size is 1 in the draft 7.
                self.win += 1
                self.win &= ((2**self.R.win_size)-1)
                self.fcn = self.R.max_fcn
            else:
                if self.fcn == None:
                    self.fcn = self.R.max_fcn
                else:
                    self.fcn -= 1
            # in above, just set fcn.
            # then will check below if the packet is the last one.
            # if so, set fcn into all-1 at that time..
            if rest_size > min_pyld_size:
                self.bitmap |= 1<<self.fcn
                if rest_size >= max_pyld_size:
                    pyld_size = max_pyld_size
                else:
                    pyld_size = rest_size
                fgh = sfh.frag_sender_tx(self.R, self.dtag,
                            win=self.win, fcn=self.fcn,
                            payload=self.srcbuf[self.pos:self.pos+pyld_size])
                if self.fcn == self.R.fcn_all_0:
                    self.state.set(STATE.SEND_ALL0)
                else:
                    self.state.set(STATE.CONT)
            else:
                # this is the last window.
                self.bitmap |= 1
                pyld_size = rest_size
                self.fcn = self.R.fcn_all_1
                fgh = sfh.frag_sender_tx(self.R, self.dtag,
                            win=self.win, fcn=self.fcn, mic=self.mic,
                            payload=self.srcbuf[self.pos:self.pos+pyld_size])
                self.state.set(STATE.SEND_ALL1)
            #
            # save the local bitmap for retransmission
            # this is for the case when the receiver will not respond.
            self.missing_prev = self.bitmap
            # store the packet for the future retransmission.
            self.fgh_list[self.fcn] = fgh
            self.pos += pyld_size
            return self.state.get(), fgh

    def parse_ack(self, recvbuf, peer):
        if self.R.mode == SCHC_MODE.NO_ACK:
            raise AssertionError("parse_ack() must not be called in NO-ACK mode.")
        #
        # XXX here, must check the peer expected.
        #
        if self.state.get() == STATE.SEND_ALL0:
            fgh = sfh.frag_sender_rx_all0_ack(recvbuf, self.R,
                                              self.dtag, self.win)
        elif self.state.get() == STATE.SEND_ALL1:
            fgh = sfh.frag_sender_rx_all1_ack(recvbuf, self.R,
                                              self.dtag, self.win)
        else:
            raise TypeError("state must be either sent_all0 or sent_all1 when parse_ack() is called. but, state=%d" % self.state.get())
        if fgh.cbit == 1:
            self.logger(1, "cbit is on.")
            self.missing = 0
        else:
            # get the missing fragments.
            if fgh.bitmap == None:
                raise ValueError("no bitmap found")
            # set new bitmap for retransmission.
            self.missing = self.bitmap & ~fgh.bitmap
            # save the local bitmap for retransmission
            self.missing_prev = self.missing
            self.logger(1, "bitmap tx:", pb.int_to_bit(self.bitmap,self.R.bitmap_size))
            self.logger(1, "bitmap rx:", pb.int_to_bit(fgh.bitmap,self.R.bitmap_size))
            self.logger(1, "missing  :", pb.int_to_bit(self.missing,self.R.bitmap_size))
        #
        if self.missing:
            if self.state.get() == STATE.SEND_ALL0:
                return self.state.set(STATE.RETRY_ALL0), fgh
            elif self.state.get() == STATE.SEND_ALL1:
                return self.state.set(STATE.RETRY_ALL1), fgh
        else:
            #
            # The receiver looks to have all fragments that the sender sent.
            # win_head can be moved to the next.
            # missing is initialized.
            self.win_head = self.pos
            self.__init_window()
            #
            # if this is the last window, then set it into DONE state.
            # Note that in ACK-ON-ERROR, it will be set it into DONE later.
            if self.state.get() == STATE.SEND_ALL0:
                return self.state.set(STATE.WIN_DONE), fgh
            elif self.state.get() == STATE.SEND_ALL1:
                return self.state.set(STATE.DONE), fgh
