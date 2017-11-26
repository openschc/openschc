
from pybinutil import *
from schc_fragment_common import *

'''
XXX TBD

state for finishing in the last window..
SCHC_FRAG_WAIT_ACK : sending the last window.
SCHC_FRAG_DONE     : all fragments are received by the receiver,
                     ready to shutdown.
'''
SCHC_FRAG_ERROR = -1
SCHC_FRAG_INIT = 0
SCHC_FRAG_DONE = 1
SCHC_FRAG_CONT = 2
SCHC_FRAG_SENT_ALL0 = 3
SCHC_FRAG_MISSING_ALL0 = 4
SCHC_FRAG_WIN_DONE = 5
SCHC_FRAG_SENT_ALL1 = 6
SCHC_FRAG_MISSING_ALL1 = 7

def default_logger(*arg):
    pass

class schc_fragment_factory:

    C = None    # the place holder of the context
    R = None    # the place holder of the rule

    # fpg_list: maintain the fragments in a window.
    # XXX
    # Note that the receiver never sends any FCN that the receiver
    # hasn't received.
    # the receiver only sends a bitmap which is recorded the fact
    # sequentially that the receiver received a fragment that the
    # sender sent.
    fpg_list = None

    def __init__(self, context, rid, logger=default_logger):
        self.C = context
        self.R = schc_rule(context, rid)
        self.logger = logger
        self.logger("max_fcn =", self.R.max_fcn,
                    "bitmap_size =", self.R.bitmap_size)

    def __init_window(self):
        self.bitmap = 0
        self.missing = 0
        self.missing_prev = 0
        self.fpg_list = {}

    def setbuf(self, srcbuf, dtag=None):
        '''
        win_head: indicating the head of current window.
                 it is held until the bitmap check is completed.
        pos: indicating the head of the data to be sent.

                   win_head        pos
                      |             |
                      v             v
        srcbuf |.........................
        '''
        if type(srcbuf) == str:
            self.srcbuf = bytearray([ord(srcbuf[i]) for i in range(len(srcbuf))])
        elif type(srcbuf) == bytearray:
            self.srcbuf = srcbuf
        else:
            raise TypeError("srcbuf must be str or bytearray.")
        self.win_head = 0
        self.pos = 0
        self.dtag = dtag
        self.fgh = schc_fragment_holder(self.C, rule=self.R, dtag=dtag)
        self.state = schc_state_holder(state=SCHC_FRAG_INIT,
                                       logger=self.logger)
        if self.R.mode != SCHC_MODE_NO_ACK:
            self.__init_window()

    def next_fragment(self, l2_size):
        '''
        l2_size: the caller can specify the size of the payload anytime.
        '''
        if self.state.get() == SCHC_FRAG_DONE:
            # no more fragments to be sent and ack check has been done.
            return SCHC_FRAG_DONE, None
        if self.state.get() == SCHC_FRAG_SENT_ALL0:
            # it comes here when the timeout happens while waiting for the
            # ack response from the receiver
            # even though either all-0 or all-1 was sent.
            self.missing = self.missing_prev
            self.state.set(SCHC_FRAG_MISSING_ALL0)
        elif self.state.get() == SCHC_FRAG_SENT_ALL1:
            self.missing = self.missing_prev
            self.state.set(SCHC_FRAG_MISSING_ALL1)
        #
        if self.missing:
            if self.state.get() not in [SCHC_FRAG_MISSING_ALL0,
                                        SCHC_FRAG_MISSING_ALL1]:
                raise AssertionError("fault state in missing")
            # if there are any missing fragments,
            # the sender only needs to send missed fragments.
            # doesn't need to send all-0/all1.
            if self.R.mode == SCHC_MODE_NO_ACK:
                raise AssertionError("no-ack mode must not come here in next_fragment().")
            # e.g. N=3
            #   all-0
            #     bit: 0 1 2 3 4 5 6
            #     fcn: 6 5 4 3 2 1 0
            #   all-1
            #     bit: 0 1 6
            #     fcn: 6 5 7
            p, self.missing = pybinutil.find_bit(self.missing, self.R.bitmap_size)
            self.logger("retransmitting.", "fpg_list=", self.fpg_list.keys(), "p=", p,
                        "missing=", pybinutil.int_to_bit(self.missing,self.R.bitmap_size))
            if p == self.R.max_fcn:
                if self.state.get() == SCHC_FRAG_MISSING_ALL0:
                    packet = self.fpg_list[self.R.fcn_all_0]
                else:
                    # i.e. SCHC_FRAG_MISSING_ALL1
                    packet = self.fpg_list[self.R.fcn_all_1]
            else:
                packet = self.fpg_list[self.R.max_fcn - p]
            # the state should be set to the previous one
            # after retransmitting all the missing fragments.
            if self.missing == 0:
                return self.state.back(), packet
            # in others, return CONT,
            # however don't need to change the state. i.e MISSING_ALL0 or MISSING_ALL1.
            return SCHC_FRAG_CONT, packet
        #
        # defragment for transmitting.
        #
        if self.state.get() == SCHC_FRAG_WIN_DONE:
            # try to support more than 1 bit wide window
            # though window bit size is 1 in the draft 7.
            self.win += 1
            self.win &= ((2**self.R.win_size)-1)
            self.fcn = self.R.max_fcn
        elif self.state.get() == SCHC_FRAG_INIT:
            self.win = 0    # initial value is 0
            self.fcn = self.R.max_fcn
        else:
            self.fcn -= 1
        #
        if self.pos + l2_size < len(self.srcbuf):
            fgp_size = l2_size  # the size of the fragment payload
            mic = ""
            if self.fcn == self.R.fcn_all_0:
                self.state.set(SCHC_FRAG_SENT_ALL0)
            else:
                self.state.set(SCHC_FRAG_CONT)
        else:
            # this is the last window.
            fgp_size = len(self.srcbuf) - self.pos
            # XXX need to calculate the mic of self.srcbuf.
            mic = ""
            self.fcn = self.R.fcn_all_1
            self.state.set(SCHC_FRAG_SENT_ALL1)
        #
        self.fgh.set_fcn(self.fcn)
        #
        if self.R.mode == SCHC_MODE_NO_ACK:
            self.logger("fcn =", self.fcn, "pos =", self.pos,
                        "size =", fgp_size)
        else:
            # in window mode, needs to maintain the local bitmap.
            self.fgh.set_win(self.win)
            if self.state.get() == SCHC_FRAG_SENT_ALL1:
                # if this fragment is all-1, bit-0 must be set.
                self.bitmap |= 1
            else:
                self.bitmap |= 1<<self.fcn
            self.logger("fcn =", self.fcn, "pos =", self.pos,
                        "size =", fgp_size, "win =", self.win,
                        "bitmap =",
                        pybinutil.int_to_bit(self.bitmap,self.R.bitmap_size))
            # save the local bitmap for retransmission
            # this is for the case when the receiver will not respond.
            self.missing_prev = self.bitmap
        #
        packet = self.fgh.add_payload(self.srcbuf[self.pos:self.pos+fgp_size],
                                      mic=mic)
        self.pos += fgp_size
        #
        if self.R.mode != SCHC_MODE_NO_ACK:
            # store the packet for the future retransmission.
            self.fpg_list[self.fcn] = packet
        #
        return self.state.get(), packet

    def is_ack_ok(self, recvbuf):
        #
        fgh = schc_fragment_holder(self.C, recvbuf=recvbuf, ack=True)
        #
        self.missing = self.bitmap & ~fgh.bitmap
        # save the local bitmap for retransmission
        self.missing_prev = self.missing
        self.logger("sent    :", pybinutil.int_to_bit(self.bitmap,self.R.bitmap_size))
        self.logger("received:", pybinutil.int_to_bit(fgh.bitmap,self.R.bitmap_size))
        self.logger("missing :", pybinutil.int_to_bit(self.missing,self.R.bitmap_size))
        if self.missing:
            # set new bitmap for new retransmission.
            if self.state.get() == SCHC_FRAG_SENT_ALL0:
                self.state.set(SCHC_FRAG_MISSING_ALL0)
            elif self.state.get() == SCHC_FRAG_SENT_ALL1:
                self.state.set(SCHC_FRAG_MISSING_ALL1)
            else:
                raise AssertionError("fault state, must be sent_all0 or sent_all1")
            return False
        #
        # The receiver looks to have all fragments that the sender sent.
        # win_head can be moved to the next.
        # missing is initialized.
        self.win_head = self.pos
        self.__init_window()
        #
        # if this is the last window, then set DONE into state.
        if self.state.get() == SCHC_FRAG_SENT_ALL0:
            self.state.set(SCHC_FRAG_WIN_DONE)
        elif self.state.get() == SCHC_FRAG_SENT_ALL1:
            self.state.set(SCHC_FRAG_DONE)
        else:
            raise AssertionError("fault state after ack check is completed.")
        return True

