
import pybinutil as pb
from schc_param import *
import schc_fragment_state as sfs
import schc_fragment_holder as sfh
import schc_rule

STATE_ERROR = -1
STATE_INIT = 0
STATE_CONT = 2
STATE_SEND_ALL0 = 3
STATE_RETRY_ALL0 = 4
STATE_WIN_DONE = 5
STATE_SEND_ALL1 = 6
STATE_RETRY_ALL1 = 7
STATE_DONE = 9

state_dict = {
    "ERROR": STATE_ERROR,
    "INIT": STATE_INIT,
    "CONT": STATE_CONT,
    "SEND_ALL0": STATE_SEND_ALL0,
    "RETRY_ALL0": STATE_RETRY_ALL0,
    "WIN_DONE": STATE_WIN_DONE,
    "SEND_ALL1": STATE_SEND_ALL1,
    "RETRY_ALL1": STATE_RETRY_ALL1,
    "DONE": STATE_DONE,
    }

def default_logger(*arg):
    pass

class fragment_factory:

    def __init__(self, C, rid, logger=default_logger):
        '''
        C: context instance.
        rid: Rule ID.
        '''
        self.R = schc_rule.schc_rule(C, rid)
        self.logger = logger
        #
        self.logger(1, "mode={0:s}".format(self.R.mode.name))
        self.logger(1, "each field size: rid={0} dtag={self.dtag_size} win={self.win_size} fcn={self.fcn_size} bitmap={self.bitmap_size} cbit={self.cbit_size} mic={self.mic_size}".format(self.R.C.rid_size, self=self.R))

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
        win_head: indicating the head of current window.
                 it is held until the bitmap check is completed.
        pos: indicating the head of the data to be sent.

                   win_head        pos
                      |             |
                      v             v
        srcbuf |.........................
        '''
        if type(srcbuf) == str:
            self.srcbuf = bytearray(srcbuf, encoding="utf-8")
        elif type(srcbuf) == bytearray or type(srcbuf) == bytes:
            self.srcbuf = bytearray(recvbuf)
        else:
            raise TypeError("srcbuf must be str, bytes or bytearray.")
        #
        self.win_head = 0
        self.pos = 0
        self.dtag = dtag
        self.mic, mic_size = self.R.C.mic_func.get_mic(self.srcbuf)
        self.win = 0
        self.__init_window()
        self.state = sfs.fragment_state(state_dict, logger=self.logger)
        self.state.set(STATE_INIT)

    def next_fragment(self, l2_size):
        '''
        l2_size: the caller can specify the size of the payload anytime.
        '''
        if self.R.mode == SCHC_MODE.NO_ACK and self.state.get() == STATE_SEND_ALL1:
            # no more fragments to be sent
            return self.state.set(STATE_DONE), None

        #
        if self.state.get() == STATE_SEND_ALL0:
            # it comes here when the timeout happens while waiting for the
            # ack response from the receiver even though either all-0 was sent.
            if self.R.mode == SCHC_MODE.WIN_ACK_ALWAYS:
                self.missing = self.missing_prev
                self.state.set(STATE_RETRY_ALL0)
            else:
                # here, for ACK-ON-ERROR
                self.state.set(STATE_WIN_DONE)
                pass
        elif self.state.get() == STATE_SEND_ALL1:
            # here, the case the sender sent all-1, but no response from the
            # receiver.
            self.missing = self.missing_prev
            self.state.set(STATE_RETRY_ALL1)
        #
        if self.state.get() in [STATE_RETRY_ALL0, STATE_RETRY_ALL1]:
            if self.missing == 0:
                raise AssertionError("fault state in missing == 0")
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
                if self.state.get() == STATE_RETRY_ALL0:
                    fgh = self.fgh_list[self.R.fcn_all_0]
                else:
                    # i.e. SCHC_FRAG_RETRY_ALL1
                    fgh = self.fgh_list[self.R.fcn_all_1]
            else:
                fgh = self.fgh_list[self.R.max_fcn - p]
            # the state should be set to the previous one
            # after retransmitting all the missing fragments.
            if self.missing == 0:
                return self.state.back(), fgh
            # in others, return CONT,
            # however don't need to change the state.
            # i.e RETRY_ALL0 or RETRY_ALL1.
            return STATE_CONT, fgh
        #
        # defragment for transmitting.
        #
        fgp_size = l2_size  # default size of the fragment payload
        if self.R.mode == SCHC_MODE.NO_ACK:
            if self.pos + l2_size < len(self.srcbuf):
                self.fcn = 0
                fgh = sfh.frag_sender_tx(self.R, self.dtag,
                                fcn=self.fcn,
                                payload=self.srcbuf[self.pos:self.pos+fgp_size])
                self.state.set(STATE_CONT)
            else:
                # this is the last fragment.
                fgp_size = len(self.srcbuf) - self.pos
                self.fcn = 1
                fgh = sfh.frag_sender_tx(self.R, self.dtag,
                                fcn=self.fcn, mic=self.mic,
                                payload=self.srcbuf[self.pos:self.pos+fgp_size])
                self.state.set(STATE_SEND_ALL1)
            #
            self.n_frags_sent += 1
            self.pos += fgp_size
            return self.state.get(), fgh
        else:
            if self.state.get() == STATE_WIN_DONE:
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
            if self.pos + l2_size < len(self.srcbuf):
                self.bitmap |= 1<<self.fcn
                fgh = sfh.frag_sender_tx(self.R, self.dtag,
                            win=self.win, fcn=self.fcn,
                            payload=self.srcbuf[self.pos:self.pos+fgp_size])
                if self.fcn == self.R.fcn_all_0:
                    self.state.set(STATE_SEND_ALL0)
                else:
                    self.state.set(STATE_CONT)
            else:
                # this is the last window.
                fgp_size = len(self.srcbuf) - self.pos
                self.fcn = self.R.fcn_all_1
                self.bitmap |= 1
                fgh = sfh.frag_sender_tx(self.R, self.dtag,
                            win=self.win, fcn=self.fcn, mic=self.mic,
                            payload=self.srcbuf[self.pos:self.pos+fgp_size])
                self.state.set(STATE_SEND_ALL1)
            #
            # save the local bitmap for retransmission
            # this is for the case when the receiver will not respond.
            self.missing_prev = self.bitmap
            # store the packet for the future retransmission.
            self.fgh_list[self.fcn] = fgh
            self.pos += fgp_size
            return self.state.get(), fgh

    def parse_ack(self, recvbuf, peer):
        if self.R.mode == SCHC_MODE.NO_ACK:
            raise AssertionError("parse_ack() must not be called in NO-ACK mode.")
        #
        # XXX here, must check the peer expected.
        #
        if self.state.get() == STATE_SEND_ALL0:
            fgh = sfh.frag_sender_rx_all0_ack(recvbuf, self.R,
                                              self.dtag, self.win)
        elif self.state.get() == STATE_SEND_ALL1:
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
            if self.state.get() == STATE_SEND_ALL0:
                return self.state.set(STATE_RETRY_ALL0), fgh
            elif self.state.get() == STATE_SEND_ALL1:
                return self.state.set(STATE_RETRY_ALL1), fgh
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
            if self.state.get() == STATE_SEND_ALL0:
                return self.state.set(STATE_WIN_DONE), fgh
            elif self.state.get() == STATE_SEND_ALL1:
                return self.state.set(STATE_DONE), fgh

