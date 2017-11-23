from __future__ import print_function

from pybinutil import *

SCHC_TTL = 60   # 60 seconds

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
SCHC_FRAG_WIN_DONE = 4
SCHC_FRAG_SENT_ALL1 = 5
SCHC_FRAG_MISSING = 6

SCHC_DEFRAG_ERROR = -1
SCHC_DEFRAG_INIT = 0
SCHC_DEFRAG_DONE = 1
SCHC_DEFRAG_CONT = 2
SCHC_DEFRAG_GOT_ALL0 = 3
SCHC_DEFRAG_GOT_ALL1 = 4
SCHC_DEFRAG_ACK = 5

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
                 ack=False):
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
        buf_size = self.R.hdr_size + len(mic) + 8*len(payload)
        # XXX need to be improved.
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

    def __init__(self, state=None):
        self.state = state

    def set(self, new_state):
        self.state_prev = self.state
        self.state = new_state
        debug_print("state: ", self.state_prev, "->", self.state)
        return self.state

    def back(self):
        debug_print("state: ", self.state, "->", self.state_prev)
        self.state = self.state_prev
        self.state_prev = None
        return self.state

    def get(self):
        return self.state

class schc_fragment:

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

    def __init__(self, context, rid, debug=0):
        global debug_level
        debug_level = debug
        self.C = context
        self.R = schc_rule(context, rid)
        debug_print("max_fcn =", self.R.max_fcn,
                    "bitmap_size =", self.R.bitmap_size)

    def __init_window(self):
        self.bitmap = 0
        self.missing = 0
        self.missing_prev = self.R.bitmap_all_1
        self.fpg_list = []

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
        self.srcbuf = srcbuf
        self.win_head = 0
        self.pos = 0
        self.dtag = dtag
        self.fgh = schc_fragment_holder(self.C, rule=self.R, dtag=dtag)
        self.state = schc_state_holder(state=SCHC_DEFRAG_INIT)
        if self.R.mode != SCHC_MODE_NO_ACK:
            self.__init_window()

    def next_fragment(self, l2_size):
        '''
        l2_size: the caller can specify the size of the payload anytime.
        '''
        if self.state.get() == SCHC_FRAG_DONE:
            # no more fragments to be sent and ack check has been done.
            return SCHC_FRAG_DONE, None
        if self.state.get() in [SCHC_FRAG_SENT_ALL0, SCHC_FRAG_SENT_ALL1]:
            # it comes here when the timeout happens while waiting for the
            # ack response from the receiver
            # even though either all-0 or all-1 was sent.
            # just changes the state into MISSING to retransmit fragments.
            #
            # set the previous value of the missing to retransmit the fragments
            # that are sent immediately before retransmission.
            self.missing = self.missing_prev
            self.state.set(SCHC_FRAG_MISSING)
        if self.missing:
            if self.state.get() != SCHC_FRAG_MISSING:
                raise AssertionError("fault state in missing")
            # if there are any missing fragments,
            # the sender only needs to send missed fragments.
            # however, doesn't need to care the local bitmap,
            # doesn't need to use all-0/all1.
            if self.R.mode == SCHC_MODE_NO_ACK:
                raise AssertionError("no-ack mode must not come here in next_fragment().")
            s = pybinutil.int_to_bit(self.missing,self.R.bitmap_size)
            p = s.index("1")
            debug_print("retransmitting. p=",p, "bitmap=", s)
            packet = self.fpg_list[p]
            self.missing = int(s[:p]+"0"+s[p+1:], 2)
            # the state should be set to the previous one
            # after retransmitting all the missing fragments.
            if self.missing == 0:
                return self.state.back(), packet
            # in others
            # don't need to change the state. i.e MISSING.
            return SCHC_FRAG_CONT, packet
        #
        # defragment for transmitting.
        #
        if self.state.get() == SCHC_FRAG_WIN_DONE:
            # XXX
            # here handle more than 1 bit wide window
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
            debug_print("fcn =", self.fcn, "pos =", self.pos,
                        "size =", fgp_size)
        else:
            # in window mode, needs to maintain the local bitmap.
            self.fgh.set_win(self.win)
            if self.state.get() == SCHC_FRAG_SENT_ALL1:
                # if this fragment is all-1, bit-0 must be set.
                self.bitmap |= 1
            else:
                self.bitmap |= 1<<self.fcn
            debug_print("fcn =", self.fcn, "pos =", self.pos,
                        "size =", fgp_size, "win =", self.win,
                        "bitmap =",
                        pybinutil.int_to_bit(self.bitmap,self.R.bitmap_size))
        #
        packet = self.fgh.add_payload(self.srcbuf[self.pos:self.pos+fgp_size],
                                      mic=mic)
        self.pos += fgp_size
        #
        if self.R.mode != SCHC_MODE_NO_ACK:
            # store the packet for the future retransmission.
            self.fpg_list.append(packet)
        #
        return self.state.get(), packet

    def is_ack_ok(self, recvbuf):
        #
        fgh = schc_fragment_holder(self.C, recvbuf=recvbuf, ack=True)
        #
        self.missing = self.bitmap & ~fgh.bitmap
        self.missing_prev = self.missing
        debug_print("sent    :", pybinutil.int_to_bit(self.bitmap,self.R.bitmap_size))
        debug_print("received:", pybinutil.int_to_bit(fgh.bitmap,self.R.bitmap_size))
        debug_print("missing :", pybinutil.int_to_bit(self.missing,self.R.bitmap_size))
        if self.missing:
            # set new bitmap for new retransmission.
            self.state.set(SCHC_FRAG_MISSING)
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

class schc_defragment_window:
    '''
    in NO_ACK mode: in case of fcn = 0, multiple fragments may exist.
    furthermore, this implementation allows to have more than 1 bit fcn.

    return:
        state, buffer for ack if needed.
        or
        state, None
    '''
    state = None
    fragment_list = {}
    fragment_list_no_ack = []   # contains the fragments (fcn == 0)
    bitmap = 0

    def __init__(self, fgh):
        self.C = fgh.C
        self.R = fgh.R
        self.win = fgh.win
        self.state = schc_state_holder(state=SCHC_DEFRAG_INIT)

    def add(self, fgh):
        debug_print(fgh.dump())
        if fgh.R.mode == SCHC_MODE_NO_ACK:
            return self.add_no_ack(fgh)
        #
        # except NO_ACK mode
        f = self.fragment_list.setdefault(fgh.fcn, {})
        if f:
            debug_print("got a FCN which is received before. replaced it.")
        # add new fragment for the assembling
        self.fragment_list[fgh.fcn] = fgh.payload
        #
        if fgh.fcn == self.R.fcn_all_1:
            self.bitmap |= 1
        else:
            self.bitmap |= 1<<fgh.fcn
        debug_print("bitmap=", pybinutil.int_to_bit(self.bitmap,
                                                    self.R.bitmap_size))
        #
        if fgh.fcn == self.R.fcn_all_0:
            if fgh.R.mode == SCHC_MODE_WIN_ACK_ON_ERROR:
                if self.is_rx_ok():
                    return self.state.set(SCHC_DEFRAG_CONT), None
            return self.state.set(SCHC_DEFRAG_GOT_ALL0), self.make_ack(fgh)
        elif fgh.fcn == self.R.fcn_all_1:
            return self.state.set(SCHC_DEFRAG_GOT_ALL1), self.make_ack(fgh)
        elif self.state.get() in [SCHC_DEFRAG_GOT_ALL0, SCHC_DEFRAG_GOT_ALL1]:
            # check whether all fragments in a window are received during
            # retransmission by the sender.
            #
            # XXX
            # assuming that, in each window except the last one,
            # the bitmap must be filled up by the fragments that sender sends.
            if self.is_rx_ok():
                # don't change the state here. i.e. GOT_ALL0 or GOT_ALL1
                return self.state.get(), self.make_ack(fgh)
            print("XXX got all-1, but don't know whether all fragments are received.")
            return SCHC_DEFRAG_CONT, None
        else:
            # in other case.
            return self.state.set(SCHC_DEFRAG_CONT), None

    def add_no_ack(fgh):
        # NO-ACK mode
        # XXX NO-ACK mode, if FCN is not a counter,
        # it can not be detected whether the sequence of the packets
        # is held or not.
        #
        # XXX draft says that either 0 or 1 is only used for FCN.
        # however, additional feature can be added, that is, other values
        # other value can be used to keep the sequence of the fragments.
        # in this case, reusing a number except of 0 is not allowed.
        '''
        if fgh.fcn == self.R.fcn_all_0:
            f = self.win_list.setdefault(fgh.fcn, [])
            # simply add it into the tail of the list.
            self.win_list[0].append(fgh.payload)
        else:
            self.win_list[0].fgh.fcn = fgh.payload
        if fgh.fcn == self.R.fcn_all_1:
            return SCHC_DEFRAG_GOT_ALL1, None
        return SCHC_DEFRAG_CONT, None
        '''
        if fgh.fcn == self.R.fcn_all_0:
            # if all-0, simply add it into the tail of the list.
            fragment_list_no_ack.append(fgh.payload)
        else:
            # if othere case, replace it.
            self.fragment_list[fgh.fcn] = fgh.payload
        #
        if fgh.fcn == self.R.fcn_all_1:
            return SCHC_DEFRAG_GOT_ALL1, None
        return SCHC_DEFRAG_CONT, None

    def assemble(self):
        if fgh.R.mode == SCHC_MODE_NO_ACK:
            a = "".join([i for i in self.fragment_list_no_ack])
            return a + "".join([i[1] for i in self.fragment_list.items()])
        # except NO_ACK
        return "".join([i[1] for i in sorted(self.fragment_list.items())])

    def is_rx_ok(self):
        debug_print("checking RX bitmap local=",
                    pybinutil.int_to_bit(self.bitmap, self.R.bitmap_size))
        if self.bitmap == self.R.bitmap_all_1:
            return True
        return False

    def make_ack(self, fgh):
        self.ack_hdr = schc_fragment_holder(self.C, fgh=fgh)
        self.ack_hdr.set_bitmap(self.bitmap)
        # XXX need padding
        # XXX when bitmap can be cleared.
        #self.bitmap = 0
        return self.ack_hdr.buf

class schc_defragment_message:
    '''
    defragment fragments into a message
    '''
    #
    #      parent tree      :  it holds
    #      in the factory   :     from here
    #                       :
    #                       :
    #     msg_list ---+--- dtag -+- win -+- fcn - frag 
    #                 |     :    |       +- fcn - frag 
    #                 |     :    |
    #                 |     :    +- win -+- fcn - frag 
    #                 |     :    |       +- fcn - frag 
    #                 +--- dtag          +- fcn - frag 
    #
    # ## NO_ACK
    #                 +--- dtag -+- fcn[0] - frag - frag - ...

    win_list = {}
    ttl = SCHC_TTL
    win = 0

    def __init__(self, fgh):
        self.R = fgh.R
        self.fgh = fgh

    def add(self, fgh):
        w = self.win_list.setdefault(fgh.win, schc_defragment_window(fgh))
        return w.add(fgh)

    def is_new_win(self, win):
        # XXX move it to the parent ?
        # check whether the win is changed or not.
        for i in win_list.keys():
            if win != i:
                return True
        return False

    def assemble(self, fcn):
        return "".join([ i[1].assemble() for i in
                        sorted(self.win_list.items())])

    def is_alive(self):
        self.ttl -= 1
        if self.ttl > 0:
            return True
        return False

debug_level = 0

def debug_print(*argv):
    if debug_level:
        print("DEBUG: ", argv)

class schc_defragment_factory:
    # XXX should check thread safe

    #
    # msg_list ---+--- dtag ---+--- win ---+--- frag 
    #             |            |           +--- frag 
    #             |            |
    #             |            +--- win ---+--- frag 
    #             |            |           +--- frag 
    #
    msg_list = {}

    def __init__(self, debug=0):
        global debug_level
        debug_level = debug

    def defrag(self, context, recvbuf):
        '''
        context: context instance
        recvbuf: bytearray received
        '''
        fgh = schc_fragment_holder(context, recvbuf=recvbuf)
        #
        # search the list for the fragment.
        # XXX dtag is the unique key ?
        # Q. same dtag can be used in the different messages in same time ?
        #m = self.msg_list.get(fgh.dtag)
        #if not m:
        #    self.msg_list[fgh.dtag] = schc_defragment_message(fgh)
        #    m = self.msg_list[fgh.dtag]
        m = self.msg_list.setdefault(fgh.dtag, schc_defragment_message(fgh))
        #
        return m.add(fgh)

    def purge(self):
        # XXX no thread safe
        for dtag in self.msg_list.iterkeys():
            if self.msg_list[dtag].is_alive():
                continue
            # delete it
            self.msg_list.pop(dtag)

