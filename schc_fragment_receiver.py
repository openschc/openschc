
from pybinutil import *
from schc_fragment_common import *

'''
XXX TBD

state for finishing in the last window..
'''
SCHC_DEFRAG_ERROR = -1
SCHC_DEFRAG_INIT = 0
SCHC_DEFRAG_CONT = 2
SCHC_DEFRAG_GOT_ALL0 = 3
SCHC_DEFRAG_MISSING_ALL0 = 4
SCHC_DEFRAG_GOT_ALL1 = 5
SCHC_DEFRAG_MISSING_ALL1 = 6
SCHC_DEFRAG_DONE = 9

SCHC_DEFRAG_MSG_INIT = 0
SCHC_DEFRAG_MSG_CONT = 1
SCHC_DEFRAG_MSG_DONE = 2
SCHC_DEFRAG_MSG_DEAD = 3

def default_logger(*arg):
    pass

def default_scheduler(*arg):
    pass

class schc_defragment_window:
    '''
    in NO_ACK mode: in case of fcn = 0, multiple fragments may exist.
    furthermore, this implementation allows to have more than 1 bit fcn.

    return: state
    '''

    def __init__(self, fgh, logger=default_logger):
        self.logger = logger
        self.C = fgh.C
        self.R = fgh.R
        self.win = fgh.win
        self.bitmap = 0
        self.state = schc_state_holder(state=SCHC_DEFRAG_INIT,
                                       logger=self.logger)
        # fragement_list is a dict because FCN is not always sequentially decremented.
        self.fragment_list = {}
        # below list is used to hold the fragments in NO_ACK because FCN is always zero.
        self.fragment_list_no_ack = []

    def add(self, fgh):
        self.logger(1, fgh.dump())
        if fgh.R.mode == SCHC_MODE_NO_ACK:
            return self.add_no_ack(fgh)
        #
        # except NO_ACK mode
        f = self.fragment_list.setdefault(fgh.fcn, {})
        if f:
            self.logger(1, "got a FCN which is received before. replaced it.")
        # add new fragment for the assembling
        self.fragment_list[fgh.fcn] = fgh.payload
        #
        if fgh.fcn == self.R.fcn_all_1:
            self.bitmap |= 1
        else:
            self.bitmap |= 1<<fgh.fcn
        self.logger(1, "bitmap=", pybinutil.int_to_bit(self.bitmap,
                                                    self.R.bitmap_size))
        #
        if fgh.fcn == self.R.fcn_all_0:
            if fgh.R.mode == SCHC_MODE_WIN_ACK_ON_ERROR:
                if self.is_rx_ok():
                    return self.state.set(SCHC_DEFRAG_CONT)
            return self.state.set(SCHC_DEFRAG_GOT_ALL0)
        elif fgh.fcn == self.R.fcn_all_1:
            return self.state.set(SCHC_DEFRAG_GOT_ALL1)
        elif self.state.get() in [SCHC_DEFRAG_GOT_ALL0, SCHC_DEFRAG_GOT_ALL1]:
            # check whether all fragments in a window are received during
            # retransmission by the sender.
            #
            # XXX
            # assuming that, in each window except the last one,
            # the bitmap must be filled up by the fragments that sender sends.
            if self.is_rx_ok():
                # don't change the state here. i.e. GOT_ALL0 or GOT_ALL1
                return self.state.get()
            self.logger(1, "WARN: XXX got all-1, but don't know whether all fragments are received.")
            return SCHC_DEFRAG_CONT
        else:
            # in other case.
            return self.state.set(SCHC_DEFRAG_CONT)

    def add_no_ack(fgh):
        # NO-ACK mode
        #
        #     return the tuple of (ret, callback, tuple-of-args)
        #
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
            return self.state.set(SCHC_DEFRAG_DONE)
        return self.state.set(SCHC_DEFRAG_CONT)

    def assemble(self):
        '''
        return a part of the message assembled in this window.
        NOTE: FCN order would be, 6 5 4 0 or 6 5 4 7.
        '''
        if self.R.mode == SCHC_MODE_NO_ACK:
            a = "".join([i for i in self.fragment_list_no_ack])
            return a + self.__assemble()
        # except NO_ACK
        return self.__assemble()

    def __assemble(self):
        self.logger(1, "assembling win =", self.win)
        for i in sorted(self.fragment_list.items(), reverse=True,
                               key=(lambda kv:(0 if kv[0]==self.R.fcn_all_1 else
                                               kv[0]))):
            self.logger(1, "fcn =", i[0], "fragment =", i[1].decode())
        #
        return "".join([i[1].decode() for i in
                        sorted(self.fragment_list.items(), reverse=True,
                               key=(lambda kv:(0 if kv[0]==self.R.fcn_all_1 else
                                               kv[0])))])

    def is_rx_ok(self):
        self.logger(1, "checking RX bitmap local=",
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

    def kill(self):
        # XXX others ?
        fragment_list = None
        fragment_list_no_ack = None

class schc_defragment_message:
    '''
    defragment fragments into a message
    '''
    def __init__(self, fgh, scheduler=default_scheduler, timeout=5, logger=default_logger):
        self.R = fgh.R
        self.fgh = fgh
        self.dtag = fgh.dtag
        self.scheduler = scheduler
        self.timeout = timeout
        self.logger = logger
        self.win_list = []
        self.win = 0
        self.state = SCHC_DEFRAG_MSG_INIT
        self.ev = None

    def add(self, fgh):
        '''
        return state and an ack message
        '''
        if self.state == SCHC_DEFRAG_MSG_DEAD:
            raise AssertionError("ERROR: must not come in if the state is dead.")
        #
        if len(self.win_list) == 0 or self.win_list[-1].win != fgh.win:
            self.logger(1, "new window has been created. win =", fgh.win)
            k = schc_defragment_window(fgh, logger=self.logger)
            self.win_list.append(k)
            #self.win_list.append(schc_defragment_window(fgh, logger=self.logger))
        #
        w = self.win_list[-1]
        ret = w.add(fgh)
        #
        if self.ev:
            self.logger(2, "canceling ev=.", self.ev)
            self.scheduler.cancel(self.ev)
            self.ev = None
        #
        if ret == SCHC_DEFRAG_CONT:
            self.state = SCHC_DEFRAG_MSG_CONT
            self.ev = self.scheduler.enter(self.timeout, 1, self.kill, (None,))
            self.logger(2, "scheduling kill dtag=", self.dtag, "ev=", self.ev)
            return ret, None
        elif ret == SCHC_DEFRAG_GOT_ALL0:
            self.state = SCHC_DEFRAG_MSG_CONT
            self.ev = self.scheduler.enter(self.timeout, 1, self.kill, (None,))
            self.logger(2, "scheduling kill dtag=", self.dtag, "ev=", self.ev)
            return ret, w.make_ack(fgh)
        elif ret == SCHC_DEFRAG_DONE:
            # XXX if self.R.mode == SCHC_MODE_NO_ACK:
            # state will be into DEAD in assemble()
            return ret, self.assemble((None,))
        elif ret == SCHC_DEFRAG_GOT_ALL1:
            # XXX if self.R.mode != SCHC_MODE_NO_ACK:
            # state will be into DONE when finish() will is called.
            self.ev = self.scheduler.enter(self.timeout, 1, self.finish,
                                           (None,))
            self.logger(2, "scheduling finish dtag=", self.dtag, "ev=", self.ev)
            return ret, w.make_ack(fgh)
        else:
            raise AssertionError("ERROR: must not come in with unknown state %d"
                                 % (ret))

    def assemble(self, args):
        '''
        assuming that no event is scheduled when assemble() is called.
        '''
        message = "".join([i.assemble() for i in self.win_list])
        self.kill()
        return message

    def finish(self, args):
        self.ev = None
        self.state = SCHC_DEFRAG_MSG_DONE

    def kill(self):
        self.ev = None
        for i in self.win_list:
            i.kill()
        self.state = SCHC_DEFRAG_MSG_DEAD
        self.win_list = None
        # XXX others ?

class schc_defragment_factory:
    '''
                        win_list
                           :
          msg_list         :       fragment_list
              :            :         :
              :            :         :
              -------+-- dtag --+-- win -+- fcn - frag 
                     |     :    |    :   +- fcn - frag 
                     |     :    |    :
                     |     :    +-- win -+- fcn - frag 
                     |     :         :   +- fcn - frag 
                     +-- dtag        :   +- fcn - frag 
     
          ## NO_ACK
                     +-- dtag --+-- fcn[0] - frag - frag - ...
    '''
    def __init__(self, scheduler=default_scheduler, timeout=5, logger=default_logger):
        self.logger = logger
        self.scheduler = scheduler
        self.timeout = timeout
        self.msg_list = {}

    def defrag(self, context, recvbuf):
        '''
        context: context instance
        recvbuf: bytearray received
        '''
        fgh = schc_fragment_holder(context, recvbuf=recvbuf,
                                   logger=self.logger)
        # search the list for the fragment.
        # XXX dtag is the unique key ?
        # XXX Q. same dtag can be used in the different messages in same time ?
        m = self.msg_list.get(fgh.dtag)
        # destruct the message holder if dead
        if m and m.state == SCHC_DEFRAG_MSG_DEAD:
            self.logger(1, "kill the old message holder for dtag =", fgh.dtag)
            m = None
        # create a message holder
        if not m:
            m = schc_defragment_message(fgh, scheduler=self.scheduler,
                                        timeout=self.timeout,
                                        logger=self.logger)
            self.msg_list[fgh.dtag] = m
        #
        return m.add(fgh)

    def dig(self):
        '''
        dig the message whose state is DONE.
        '''
        ret = []
        for k, v in self.msg_list.items():
            if v.state == SCHC_DEFRAG_MSG_DONE and v.R.mode != SCHC_MODE_NO_ACK:
                # if NO_ACK mode, assuming that the message assembled has been returned.
                ret.append(v.assemble(True))
                self.logger(1, "digged dtag = %s" % v.dtag)
        return ret

