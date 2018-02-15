
import pybinutil as pb
from schc_param import *
import schc_fragment_state as sfs
import schc_fragment_holder as sfh
import mic_crc32

STATE_FAIL = -1
STATE_INIT = 0
STATE_CONT = 2
STATE_CHECK_ALL0 = 3
STATE_CONT_ALL0 = 4
STATE_SEND_ACK0 = 5
STATE_CHECK_ALL1 = 6
STATE_CONT_ALL1 = 7
STATE_SEND_ACK1 = 8
STATE_WIN_DONE = 98
STATE_DONE = 99

state_dict = {
    "FAIL": STATE_FAIL,
    "INIT": STATE_INIT,
    "CONT": STATE_CONT,
    "CHECK_ALL0": STATE_CHECK_ALL0,
    "CONT_ALL0": STATE_CONT_ALL0,
    "SEND_ACK0": STATE_SEND_ACK0,
    "CHECK_ALL1": STATE_CHECK_ALL1,
    "CONT_ALL1": STATE_CONT_ALL1,
    "SEND_ACK1": STATE_SEND_ACK1,
    "WIN_DONE": STATE_WIN_DONE,
    "DONE": STATE_DONE,
    }

STATE_MSG_INIT = 0
STATE_MSG_CONT = 1
STATE_MSG_DONE = 2
STATE_MSG_DEAD = 3

def default_logger(*arg):
    pass

def default_scheduler(*arg):
    pass

class defragment_window:
    '''
    in NO_ACK mode: in case of fcn = 0, multiple fragments may exist.
    furthermore, this implementation allows to have more than 1 bit fcn.

    return: state
    '''

    def __init__(self, fgh, logger=default_logger):
        self.logger = logger
        self.R = fgh.R
        self.win = fgh.win
        self.bitmap = 0
        self.mic = None
        self.win_state = sfs.fragment_state(state_dict, logger=self.logger)
        self.win_state.set(STATE_INIT)
        # fragement_list is a dict because FCN is not always sequentially decremented.
        self.fragment_list = {}
        # below list is used to hold the fragments in NO_ACK because FCN is always zero.
        self.fragment_list_no_ack = []

    def add(self, fgh):
        if fgh.R.mode == SCHC_MODE.NO_ACK:
            return self.__add_no_ack_mode(fgh)
        else:
            return self.__add_win_mode(fgh)

    def __add_win_mode(self, fgh):
        '''
        except NO_ACK mode
        '''
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
        self.logger(1, "bitmap=", pb.int_to_bit(self.bitmap,
                                                self.R.bitmap_size))
        #
        # assuming that, in each window except the last one,
        # the bitmap must be filled up by the fragments that sender sends.
        if self.win_state.get() in [STATE_INIT, STATE_CONT]:
            if fgh.fcn == self.R.fcn_all_0:
                # immediately after receiving the all-0
                return self.win_state.set(STATE_CHECK_ALL0)
            elif fgh.fcn == self.R.fcn_all_1:
                # immediately after receiving the all-1
                return self.win_state.set(STATE_CHECK_ALL1)
            else:
                return self.win_state.set(STATE_CONT)
        elif self.win_state.get() == STATE_CONT_ALL0:
            if fgh.fcn == self.R.fcn_all_0 and fgh.payload == None:
                # this is a request of Ack for All-0
                print("XXX Resending of Ack for All-0 not implemented yet.")
                pass
            else:
                # alwas check whether all fragments in a window are received
                # during retransmission by the sender.
                return self.win_state.set(STATE_CHECK_ALL0)
        elif self.win_state.get() == STATE_SEND_ACK0:
            if fgh.fcn == self.R.fcn_all_0 and fgh.payload == None:
                # this is a request of Ack for All-0
                print("XXX Resending of Ack for All-0 not implemented yet.")
                pass
            else:
                # XXX
                self.logger(1, "XXX ignore in SEND_ACK0", fgh.dump())
        elif self.win_state.get() == STATE_CONT_ALL1:
            if fgh.fcn == self.R.fcn_all_1 and fgh.payload == None:
                # this is a request of Ack for All-1
                print("XXX Resending of Ack for All-1 not implemented yet.")
                pass
            else:
                # check whether all fragments in the last window are received
                # during retransmission by the sender.
                return self.win_state.set(STATE_CHECK_ALL1)
        elif self.win_state.get() == STATE_SEND_ACK1:
            if fgh.fcn == self.R.fcn_all_1 and fgh.payload == None:
                # this is a request of Ack for All-1
                print("XXX Resending of Ack for All-1 not implemented yet.")
                pass
            else:
                # XXX
                self.logger(1, "XXX ignore in SEND_ACK1", fgh.dump())
        else:
            # in other case.
            raise ValueError("invalid state=%s", self.win_state.pprint())

    def __add_no_ack_mode(self, fgh):
        '''
        in NO-ACK, the value of the FCN is either 0 or 1.
        therefore, if all-0, simply add it into the tail of the list.
        '''
        if self.win_state.get() in [STATE_INIT, STATE_CONT]:
            if fgh.fcn == self.R.fcn_all_1:
                # immediately after receiving the all-1
                self.fragment_list[fgh.fcn] = fgh.payload
                return self.win_state.set(STATE_CHECK_ALL1)
            else:
                # e.g. fgh.fcn == self.R.fcn_all_0
                self.fragment_list_no_ack.append(fgh.payload)
                return self.win_state.set(STATE_CONT)
        else:
            # in other case.
            raise ValueError("invalid state=%s", self.win_state.pprint())
        # XXX NO-ACK mode, if FCN is not a counter,
        # it can not be detected whether the sequence of the packets
        # is held or not.
        #
        # XXX draft says that either 0 or 1 is only used for FCN.
        # however, additional feature can be added, that is, other values
        # other value can be used to keep the sequence of the fragments.
        # in this case, reusing a number except of 0 is not allowed.

    def assemble(self):
        '''
        return a part of the message assembled in this window.
        NOTE: e.g. FCN order would be, 6 5 4 0 or 6 5 4 7 in case of N=3.
        '''
        if self.R.mode == SCHC_MODE.NO_ACK:
            a = b"".join([i for i in self.fragment_list_no_ack])
            return a + self.__assemble()
        else:
            return self.__assemble()

    def __assemble(self):
        self.logger(1, "assembling ")
        if self.R.mode != SCHC_MODE.NO_ACK:
            self.logger(1, "  win =", self.win)
        for i in sorted(self.fragment_list.items(), reverse=True,
                        key=(lambda kv:
                             (0 if kv[0]==self.R.fcn_all_1 else kv[0]))):
            self.logger(2, "fcn =", i[0], "fragment =",
                        i[1].decode(encoding="utf-8"))
        #
        return b"".join([i[1] for i in
                        sorted(self.fragment_list.items(), reverse=True,
                               key=(lambda kv:(0 if kv[0]==self.R.fcn_all_1 else
                                               kv[0])))])

    def all_fragments_received(self):
        self.logger(1, "checking all-0 fragments, local bitmap=",
                    pb.int_to_bit(self.bitmap, self.R.bitmap_size))
        if self.bitmap == self.R.bitmap_all_1:
            return True
        return False

    def make_ack0(self, fgh):
        if self.win_state.get() != STATE_CHECK_ALL0:
            raise AssertionError("ERROR: must not come into make_ack0().")
        # make it only the case immediately after receiving the all-0.
        # otherwise, it does nothing.
        # i.e. prev_state == CONT or INIT.
        if self.win_state.get_prev() not in [STATE_CONT, STATE_INIT]:
            return None
        else:
            return sfh.frag_receiver_tx_all0_ack(self.R, fgh.dtag, win=fgh.win,
                                                 bitmap=self.bitmap)

    def make_ack1(self, fgh, cbit=None):
        if self.win_state.get() != STATE_CHECK_ALL1:
            raise AssertionError("ERROR: must not come into make_ack1().")
        # only the case immediately after receiving the all-1,
        # i.e. state == CHECK_ALL1 and prev_state == CONT/INIT
        if self.win_state.get_prev() not in [STATE_CONT, STATE_INIT]:
            return None
        else:
            return sfh.frag_receiver_tx_all1_ack(self.R, fgh.dtag,
                                                 win=fgh.win, cbit=cbit,
                                                 bitmap=(None if cbit == None
                                                         else self.bitmap))

    def kill(self):
        # XXX others should be set None ?
        fragment_list = None
        self.fragment_list_no_ack = None

class defragment_message:
    '''
    defragment fragments into a message
    '''
    def __init__(self, R, dtag, scheduler=default_scheduler, timeout=5,
                 logger=default_logger):
        self.R = R
        self.dtag = dtag
        self.scheduler = scheduler
        self.timeout = timeout
        self.logger = logger
        self.win_list = []
        self.win = 0
        self.msg_state = STATE_MSG_INIT
        self.ev = None

    def add(self, fgh):
        '''
        return the message state and an buffer.
        '''
        if self.msg_state == STATE_MSG_DEAD:
            raise AssertionError("ERROR: must not come in if the message state is dead.")
        #
        if len(self.win_list) == 0 or self.win_list[-1].win != fgh.win:
            self.logger(1, "new window has been created. win =", fgh.win)
            k = defragment_window(fgh, logger=self.logger)
            self.win_list.append(k)
        #
        w = self.win_list[-1]
        ret = w.add(fgh)
        #
        if self.ev:
            self.logger(3, "canceling ev=.", self.ev)
            self.scheduler.cancel(self.ev)
            self.ev = None
        #
        if ret in [STATE_CONT, STATE_CONT_ALL0, STATE_CONT_ALL1]:
            self.ev = self.scheduler.enter(self.timeout, 1, self.kill, (None,))
            self.logger(3, "scheduling kill 1 dtag=", self.dtag, "ev=", self.ev)
            return ret, None
        elif ret == STATE_CHECK_ALL0:
            ack_payload = None
            if fgh.R.mode == SCHC_MODE.WIN_ACK_ON_ERROR:
                # if all the fragments in a window is received, all bits in
                # the internal bitmap are on. i.e. equal to (2**bitmap_size)-1
                # if so, skip to send the ack, otherwise send an ack.
                if w.all_fragments_received():
                    ret = w.win_state.set(STATE_WIN_DONE)
                else:
                    ret = w.win_state.set(STATE_CONT_ALL0)
            else:
                if w.all_fragments_received():
                    ack_payload = w.make_ack0(fgh)
                    ret = w.win_state.set(STATE_SEND_ACK0)
                else:
                    ret = w.win_state.set(STATE_CONT_ALL0)
            #
            self.ev = self.scheduler.enter(self.timeout, 1, self.kill, (None,))
            self.logger(3, "scheduling kill 2 dtag=", self.dtag, "ev=", self.ev)
            return ret, ack_payload
        elif ret == STATE_CHECK_ALL1:
            # check MIC
            # XXX is there the case when the MIC is okey but any fragments have
            # not received ?
            if self.mic_matched(fgh):
                # msg_state will be into DONE when finish() will be called.
                self.ev = self.scheduler.enter(self.timeout, 1, self.finish, (None,))
                self.logger(3, "scheduling finish dtag=", self.dtag, "ev=", self.ev)
                ack_payload = w.make_ack1(fgh, cbit=1)
                return w.win_state.set(STATE_SEND_ACK1), ack_payload
            else:
                ack_payload = w.make_ack1(fgh, cbit=0)
                return w.win_state.set(STATE_CONT_ALL1), ack_payload
        elif ret == STATE_DONE:
            # msg_state will be into DEAD in assemble()
            raise AssertionError("must not com here for STATE_DONE")
            #return ret, self.assemble(kill=True)
        else:
            raise AssertionError("ERROR: must not come in with unknown message state %d" % (ret))

    def mic_matched(self, fgh):
        self.logger(1, "calculating mic.")
        self.mic, mic_size = self.R.C.mic_func.get_mic(self.assemble(kill=False))
        if fgh.mic == self.mic:
            self.logger(1, "mic is matched.")
            return True
        else:
            self.logger(1, "mic is NOT matched.")
            return False

    def assemble(self, kill=False):
        '''
        assuming that no event is scheduled when assemble() is called.
        '''
        message = b"".join([i.assemble() for i in self.win_list])
        if kill == True:
            self.kill()
        return message

    def finish(self, *args):
        self.ev = None
        self.msg_state = STATE_MSG_DONE

    def kill(self, *args):
        self.ev = None
        for i in self.win_list:
            i.kill()
        self.msg_state = STATE_MSG_DEAD
        self.win_list = None
        # XXX others ?

class defragment_factory:
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
    def __init__(self, scheduler=default_scheduler, timeout=5,
                 logger=default_logger):
        self.logger = logger
        self.scheduler = scheduler
        self.timeout = timeout
        self.msg_list = {}

    def defrag(self, C, recvbuf):
        '''
        C: context instance
        recvbuf: bytearray received
        '''
        fgh = sfh.frag_receiver_rx(recvbuf, C)
        # search the list for the fragment.
        # assuming that dtag is the unique key for each originalipv6 packet
        # before fragmented..
        m = self.msg_list.get(fgh.dtag)
        # destruct the message holder if dead
        if m and m.msg_state == STATE_MSG_DEAD:
            self.logger(1, "kill the old message holder for dtag =", fgh.dtag)
            m = None
        # create a message holder
        if not m:
            m = defragment_message(fgh.R, fgh.dtag, scheduler=self.scheduler,
                                   timeout=self.timeout, logger=self.logger)
            self.msg_list[fgh.dtag] = m
        #
        rx_ret, tx_obj = m.add(fgh)
        return rx_ret, fgh, tx_obj

    def dig(self):
        '''
        dig the message whose state is DONE.
        here, only non-NO_ACK mode is dealt.
        if NO_ACK mode, the message assembled has been returned to the
        application.
        '''
        ret = []
        for k, m in self.msg_list.items():
            if m.msg_state == STATE_MSG_DONE and m.R.mode != SCHC_MODE.NO_ACK:
                ret.append(m.assemble(kill=True))
                self.logger(1, "digged dtag = %s" % m.dtag)
        return ret

