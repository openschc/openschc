
from pybinutil import *
from schc_fragment_common import *

SCHC_TTL = 60   # 60 seconds

'''
XXX TBD

state for finishing in the last window..
SCHC_FRAG_WAIT_ACK : sending the last window.
SCHC_FRAG_DONE     : all fragments are received by the receiver,
                     ready to shutdown.
'''
SCHC_DEFRAG_ERROR = -1
SCHC_DEFRAG_INIT = 0
SCHC_DEFRAG_DONE = 1
SCHC_DEFRAG_CONT = 2
SCHC_DEFRAG_GOT_ALL0 = 3
SCHC_DEFRAG_MISSING_ALL0 = 4
SCHC_DEFRAG_GOT_ALL1 = 5
SCHC_DEFRAG_MISSING_ALL1 = 6
SCHC_DEFRAG_ACK = 7

def default_logger(*arg):
    pass

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

    def __init__(self, fgh, logger=default_logger):
        self.logger = logger
        self.C = fgh.C
        self.R = fgh.R
        self.win = fgh.win
        self.state = schc_state_holder(state=SCHC_DEFRAG_INIT)

    def add(self, fgh):
        self.logger(fgh.dump())
        if fgh.R.mode == SCHC_MODE_NO_ACK:
            return self.add_no_ack(fgh)
        #
        # except NO_ACK mode
        f = self.fragment_list.setdefault(fgh.fcn, {})
        if f:
            self.logger("got a FCN which is received before. replaced it.")
        # add new fragment for the assembling
        self.fragment_list[fgh.fcn] = fgh.payload
        #
        if fgh.fcn == self.R.fcn_all_1:
            self.bitmap |= 1
        else:
            self.bitmap |= 1<<fgh.fcn
        self.logger("bitmap=", pybinutil.int_to_bit(self.bitmap,
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
        self.logger("checking RX bitmap local=",
                    pybinutil.int_to_bit(self.bitmap, self.R.bitmap_size))
        if self.bitmap == self.R.bitmap_all_1:
            return True
        return False

    def make_ack(self, fgh):
        self.ack_hdr = schc_fragment_holder(self.C, fgh=fgh, logger=self.logger)
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

    def __init__(self, fgh, logger=default_logger):
        self.R = fgh.R
        self.fgh = fgh
        self.logger = logger

    def add(self, fgh):
        w = self.win_list.setdefault(fgh.win, schc_defragment_window(fgh,
                                                                     logger=self.logger))
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

    def __init__(self, logger=default_logger):
        self.logger = logger

    def defrag(self, context, recvbuf):
        '''
        context: context instance
        recvbuf: bytearray received
        '''
        fgh = schc_fragment_holder(context, recvbuf=recvbuf,
                                   logger=self.logger)
        #
        # search the list for the fragment.
        # XXX dtag is the unique key ?
        # Q. same dtag can be used in the different messages in same time ?
        #m = self.msg_list.get(fgh.dtag)
        #if not m:
        #    self.msg_list[fgh.dtag] = schc_defragment_message(fgh)
        #    m = self.msg_list[fgh.dtag]
        m = self.msg_list.setdefault(fgh.dtag, schc_defragment_message(fgh,
                                                                       logger=self.logger))
        #
        return m.add(fgh)

    def purge(self):
        # XXX no thread safe
        for dtag in self.msg_list.iterkeys():
            if self.msg_list[dtag].is_alive():
                continue
            # delete it
            self.msg_list.pop(dtag)

