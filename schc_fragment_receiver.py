import pybinutil as pb
from schc_param import *
import schc_fragment_state as sfs
import schc_fragment_holder as sfh
import mic_crc32
from enum import Enum, unique, auto

@unique
class SCHC_RECEIVER_STATE(Enum):
    FAIL = auto()
    ABORT = auto()
    INIT = auto()
    CONT = auto()
    CHECK_ALL0 = auto()
    CONT_ALL0 = auto()
    SEND_ACK0 = auto()
    CHECK_ALL1 = auto()
    CONT_ALL1 = auto()
    SEND_ACK1 = auto()
    WIN_DONE = auto()
    DONE = auto()

STATE = SCHC_RECEIVER_STATE

@unique
class SCHC_RECEIVER_MSG_STATE(Enum):
    INIT = auto()
    CONT = auto()
    DONE = auto()
    DYING = auto()
    DEAD = auto()

STATE_MSG = SCHC_RECEIVER_MSG_STATE

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
        self.win_state = sfs.fragment_state(STATE, logger=self.logger)
        self.win_state.set(STATE.INIT)
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
            self.logger(1, "got a FCN which was received before. replaced it.")
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
        if self.win_state.get() in [STATE.INIT, STATE.CONT]:
            if fgh.fcn == self.R.fcn_all_0:
                # immediately after receiving the all-0
                return self.win_state.set(STATE.CHECK_ALL0)
            elif fgh.fcn == self.R.fcn_all_1:
                # immediately after receiving the all-1
                return self.win_state.set(STATE.CHECK_ALL1)
            elif self.win_state.get() == STATE.INIT:
                # fnc is neigher all-0 nor all-1, if it's first fragment.
                return self.win_state.set(STATE.CONT)
            else:
                # otherwise,
                return STATE.CONT
        elif self.win_state.get() == STATE.CONT_ALL0:
            if fgh.fcn == self.R.fcn_all_0:
                # same as the CONT_ALL1 state.
                return self.win_state.set(STATE.CHECK_ALL0)
            else:
                return self.win_state.get()
        elif self.win_state.get() == STATE.SEND_ACK0:
            if fgh.fcn == self.R.fcn_all_0 and fgh.payload == None:
                # this is a request of Ack for All-0
                print("XXX Resending of Ack for All-0 not implemented yet.")
                pass
            else:
                # XXX
                self.logger(1, "XXX ignore in SEND_ACK0", fgh.dump())
        elif self.win_state.get() == STATE.CONT_ALL1:
            if fgh.fcn == self.R.fcn_all_1:
                # It doesn't need to check the payload size (i.e. ALL-1 empty).
                # It just changes the state into CHECK_ALL1 anyway
                # if the message is of ALL-1 at CONT_ALL1 state.
                return self.win_state.set(STATE.CHECK_ALL1)
            else:
                # don't change the state before it gets any ALL-1 message.
                return self.win_state.get()
        elif self.win_state.get() == STATE.SEND_ACK1:
            if fgh.fcn == self.R.fcn_all_1 and fgh.payload == None:
                # this is a request of Ack for All-1
                print("XXX Resending of Ack for All-1 not implemented yet.")
                pass
            else:
                self.logger(1, "ignore the message in SEND_ACK1", fgh.dump())
                return STATE.FAIL
        else:
            # in other case.
            raise ValueError("invalid state=%s", self.win_state.pprint())

    def __add_no_ack_mode(self, fgh):
        '''
        in NO-ACK, the value of the FCN is either 0 or 1.
        therefore, if all-0, simply add it into the tail of the list.
        XXX it cannot detect whether the messages have been reordered or not.
        '''
        if self.win_state.get() in [STATE.INIT, STATE.CONT]:
            if fgh.fcn == self.R.fcn_all_1:
                # immediately after receiving the all-1
                self.fragment_list[fgh.fcn] = fgh.payload
                return self.win_state.set(STATE.CHECK_ALL1)
            else:
                # e.g. fgh.fcn == self.R.fcn_all_0
                self.fragment_list_no_ack.append(fgh.payload)
                return self.win_state.set(STATE.CONT)
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
        self.logger(1, "assembling ")
        if self.R.mode == SCHC_MODE.NO_ACK:
            a = []
            for i in self.fragment_list_no_ack:
                self.logger(2, "fcn =", 0, "fragment =", i)
                a.append(i)
            return b"".join(a) + self.__assemble()
        else:
            return self.__assemble()

    def __assemble(self):
        if self.R.mode != SCHC_MODE.NO_ACK:
            self.logger(1, "  win =", self.win)
        a = []
        for i in sorted(self.fragment_list.items(), reverse=True,
                        key=(lambda kv:
                             (0 if kv[0]==self.R.fcn_all_1 else kv[0]))):
            self.logger(2, "fcn =", i[0], "fragment =", i)
            if i[1]:
                a.append(i[1])
        return b"".join(a)

    def all_fragments_received(self):
        self.logger(1, "checking all-0 fragments, local bitmap=",
                    pb.int_to_bit(self.bitmap, self.R.bitmap_size))
        if self.bitmap == self.R.bitmap_all_1:
            self.logger(1, "received all fragments.")
            return True
        else:
            self.logger(1, "not received all fragments.")
            return False

    def make_ack0(self, fgh):
        if self.win_state.get() != STATE.CHECK_ALL0:
            raise AssertionError("ERROR: must not come into make_ack0().")
        # XXX should it be make an ack only immediately after received all-0.
        #if self.win_state.get_prev() not in [STATE.CONT, STATE.INIT]:
        #    return None
        else:
            return sfh.frag_receiver_tx_all0_ack(self.R, fgh.dtag, win=fgh.win,
                                                 bitmap=self.bitmap)

    def make_ack1(self, fgh, cbit=None):
        if self.win_state.get() != STATE.CHECK_ALL1:
            raise AssertionError("ERROR: must not come into make_ack1().")
        # XXX should it be make an ack only immediately after received all-1.
        #if self.win_state.get_prev() not in [STATE.CONT, STATE.INIT]:
        #    return None
        else:
            return sfh.frag_receiver_tx_all1_ack(self.R, fgh.dtag,
                                                 win=fgh.win, cbit=cbit,
                                                 bitmap=(None if cbit == None
                                                         else self.bitmap))

    def purge(self):
        # XXX others should be set None ?
        del(self.fragment_list)
        del(self.fragment_list_no_ack)

class defragment_message:
    '''
    defragment fragments into a message
    '''
    def __init__(self, R, dtag, scheduler=default_scheduler, timer=5,
                 timer_t3=10, logger=default_logger):
        self.R = R
        self.dtag = dtag
        self.scheduler = scheduler
        self.timer = timer
        self.timer_t3 = timer_t3
        self.logger = logger
        self.win_list = []
        self.win = 0
        self.msg_state = STATE_MSG.INIT
        self.ev = None

    def add(self, fgh):
        '''
        return the message state and an buffer.
        '''
        if self.msg_state == STATE_MSG.DEAD:
            raise AssertionError("ERROR: must not come in if the message state is dead.")
        # check the message whether it is the first fragment of this session.
        if fgh.R.mode != SCHC_MODE.NO_ACK and self.msg_state == STATE_MSG.INIT:
            if fgh.win == 0 and fgh.fcn == self.R.max_fcn:
                self.msg_state = STATE_MSG.CONT
            else:
                return (STATE.ABORT,
                        sfh.frag_receiver_tx_abort(self.R, fgh.dtag,
                                                   win=fgh.win))
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
        if ret in [STATE.CONT, STATE.CONT_ALL0, STATE.CONT_ALL1]:
            self.ev = self.scheduler.enter(self.timer, 1, self.purge, (True,))
            self.logger(3, "scheduling purge 1 dtag=", self.dtag, "ev=", self.ev)
            return ret, None
        elif ret == STATE.CHECK_ALL0:
            ack_payload = None
            if fgh.R.mode == SCHC_MODE.ACK_ON_ERROR:
                # if all the fragments in a window is received, all bits in
                # the internal bitmap are on. i.e. equal to (2**bitmap_size)-1
                # if so, skip to send the ack, otherwise send an ack.
                if w.all_fragments_received():
                    ret = w.win_state.set(STATE.WIN_DONE)
                else:
                    ack_payload = w.make_ack0(fgh)
                    ret = w.win_state.set(STATE.CONT_ALL0)
            else:
                ack_payload = w.make_ack0(fgh)
                if w.all_fragments_received():
                    ret = w.win_state.set(STATE.SEND_ACK0)
                else:
                    ret = w.win_state.set(STATE.CONT_ALL0)
            #
            self.ev = self.scheduler.enter(self.timer, 1, self.purge, (True,))
            self.logger(3, "scheduling purge 2 dtag=", self.dtag, "ev=", self.ev)
            # ack_payload is going to be None if the state is WIN_DONE.
            return ret, ack_payload
        elif ret == STATE.CHECK_ALL1:
            # check MIC
            # XXX is there the case when the MIC is okey but any fragments have
            # not received ?
            if self.mic_matched(fgh):
                if self.R.mode == SCHC_MODE.NO_ACK:
                    self.finish()
                    return w.win_state.set(STATE.DONE), None
                else:
                    self.finish()
                    self.ev = self.scheduler.enter(self.timer_t3, 1,
                                                   self.purge, (True,))
                    self.logger(3, "scheduling purge 3 dtag=",
                                self.dtag, "ev=", self.ev)
                    # it has to make the ack payload before change the state.
                    ack_payload = w.make_ack1(fgh, cbit=1)
                    return (w.win_state.set(STATE.SEND_ACK1), ack_payload)
            else:
                # it has to make the ack payload before change the state.
                ack_payload = w.make_ack1(fgh, cbit=0)
                return (w.win_state.set(STATE.CONT_ALL1), ack_payload)
        elif ret == STATE.DONE:
            raise AssertionError("must not com here for STATE.DONE")
        elif ret == STATE.FAIL:
            return ret, None
        else:
            raise AssertionError("ERROR: must not come in with unknown message state %s" % (ret.name))

    def mic_matched(self, fgh):
        self.logger(1, "calculating mic.")
        self.mic, mic_size = self.R.C.mic_func.get_mic(self.assemble())
        if fgh.mic == self.mic:
            self.logger(1, "mic is matched.")
            return True
        else:
            self.logger(1, "mic is NOT matched.")
            return False

    def assemble(self):
        '''
        assuming that no event is scheduled when assemble() is called.
        '''
        message = b"".join([i.assemble() for i in self.win_list])
        return message

    def finish(self, *args):
        self.msg_state = STATE_MSG.DONE

    def kill(self, *args):
        self.msg_state = STATE_MSG.DYING

    def purge(self, *args):
        '''
        args: (ev, ): ev is True means purge is called from an event.
        '''
        #if self.msg_state != STATE_MSG.DYING:
        #    self.logger(1, "WARNING: this message hasn't been showed.", self)
        if args[0] == False and self.ev:
            self.logger(3, "schedule cancelled dtag=",
                                self.dtag, "ev=", self.ev)
            self.scheduler.cancel(self.ev)
        self.ev = None
        if hasattr(self, "win_list"):
            for i in self.win_list:
                i.purge()
            del(self.win_list)
        self.msg_state = STATE_MSG.DEAD
        # XXX others ?

class defragment_factory:
    '''
                        win_list
                           :
          msg_list         :       fragment_list { fcn:payload }
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
    def __init__(self, scheduler=default_scheduler, timer=5, timer_t3=10,
                 logger=default_logger):
        self.logger = logger
        self.scheduler = scheduler
        self.timer = timer
        self.timer_t3 = timer_t3
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
        if m:
            if m.R.mode == SCHC_MODE.NO_ACK:
                if m.msg_state in [STATE_MSG.DEAD, STATE_MSG.DYING]:
                    self.logger(1, "remove the old message holder for dtag =",
                                fgh.dtag)
                    m = None
            else:
                if m.msg_state == STATE_MSG.DEAD:
                    self.logger(1, "remove the old message holder for dtag =",
                                fgh.dtag)
                    m = None
                elif m.msg_state in [STATE_MSG.DONE, STATE_MSG.DYING]:
                    # later check whether it is a ALL-1 empty.
                    pass
        # create a message holder
        if not m:
            m = defragment_message(fgh.R, fgh.dtag, scheduler=self.scheduler,
                                   timer=self.timer, timer_t3=self.timer_t3,
                                   logger=self.logger)
            self.msg_list[fgh.dtag] = m
        #
        rx_ret, tx_obj = m.add(fgh)
        if rx_ret == STATE.FAIL:
            # assumeing any message have been showed, just ignore it.
            m.purge((False,))
        elif rx_ret == STATE.ABORT:
            m.purge((False,))
        #
        return rx_ret, fgh, tx_obj

    def dig(self):
        '''
        dig the messages.
        if the state of the message is DONE, assemble and put to the return.
        if the state of the message is DYING, purge it.
        '''
        self.logger(3, "digging list size =", len(self.msg_list.items()))
        ret = []
        purge_list = []
        for k, m in self.msg_list.items():
            if m.msg_state == STATE_MSG.DONE:
                ret.append(m.assemble())
                self.logger(1, "digged dtag =", m.dtag)
                m.kill()
            #
            if m.msg_state == STATE_MSG.DEAD:
                m.purge((False,))
                purge_list.append(k)
        #
        for i in purge_list:
            self.logger(1, "deleted dtag =", i)
            self.msg_list.pop(i)
        #
        return ret
