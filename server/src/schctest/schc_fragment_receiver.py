import pybinutil as pb
from schc_param import *
import schc_fragment_state as sfs
import schc_fragment_message as sfh
from schc_fragment_ruledb import schc_fragment_ruledb
import mic_crc32
import micro_enum
from bitto import my_bit_to

STATE = micro_enum.enum(
    FAIL = -1,
    ABORT = -2,
    INIT = 0,
    CONT = 1,
    CHECK_ALL0 = 14,
    CONT_ALL0 = 15,
    ALL0_OK = 16,
    ALL0_NG = 17,
    WIN_DONE = 19,
    CHECK_ALL1 = 21,
    ALL1_OK = 22,
    ALL1_NG = 23,
    CONT_ALL1 = 24,
    DONE = 99
    )

STATE_MSG = micro_enum.enum(
    INIT = 0,
    CONT = 1,
    CHECKING = 2,
    COLLECTED = 5,
    SERVED = 7,
    DEAD = 9
    )



def default_logger(*arg):
    pass

def default_scheduler(*arg):
    pass

def join_frag_list(frag_list):
    '''Because one cannot use b"".join([...list with bytearray...])'''
    if len(frag_list) == 0:
        return b""
    else:
        res = frag_list[0]
        for frag in frag_list[1:]:
            res += frag
        return res

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
        # empty ALL0 or ALL1 only be acceptable with duplicate FCN.
        if len(f):
            if (fgh.payload == None and
                (self.win_state.get() == STATE.CONT_ALL0 and
                 fgh.fcn == self.R.fcn_all_0)):
                return self.win_state.set(STATE.CHECK_ALL0)
            elif (fgh.payload == None and
                  (self.win_state.get() == STATE.CONT_ALL1 and
                 fgh.fcn == self.R.fcn_all_1)):
                return self.win_state.set(STATE.CHECK_ALL1)
            else:
                self.logger(1, "ERROR: got a FCN which was received before.",
                            self.win_state.get(), self.win, fgh.fcn)
                return STATE.FAIL
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
        elif self.win_state.get() in [STATE.ALL0_NG, STATE.CONT_ALL0]:
            # same as the CONT_ALL1 state.
            if fgh.fcn == self.R.fcn_all_0:
                return self.win_state.set(STATE.CHECK_ALL0)
            elif self.win_state.get() == STATE.ALL0_NG:
                return self.win_state.set(STATE.CONT_ALL0)
            else:
                return STATE.CONT_ALL0
        elif self.win_state.get() == STATE.ALL0_OK:
            # same as the CONT_ALL1 state.
            if fgh.fcn == self.R.fcn_all_0:
                return self.win_state.get()
        elif self.win_state.get() in [STATE.ALL1_NG, STATE.CONT_ALL1]:
            # It doesn't need to check the payload size (i.e. ALL-1 empty).
            # If ALL-1 message is received at CONT_ALL1 state,
            # it just changes the state into CHECK_ALL1 anyway
            # doesn't change the state before it gets any ALL-1 message.
            if fgh.fcn == self.R.fcn_all_1:
                return self.win_state.set(STATE.CHECK_ALL1)
            elif self.win_state.get() == STATE.ALL1_NG:
                return self.win_state.set(STATE.CONT_ALL1)
            else:
                return STATE.CONT_ALL1
        elif self.win_state.get() == STATE.SEND_ACK1:
            # same as the CONT_ALL1 state.
            if fgh.fcn == self.R.fcn_all_1:
                return self.win_state.get()
        else:
            # in other case.
            raise ValueError("invalid state=%s" % self.win_state.pprint())

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
            raise ValueError("invalid state=%s" % self.win_state.pprint())
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
            return join_frag_list(a) + self.__assemble()
            #return "".join(a) + self.__assemble() # XXX:merge

        else:
            return self.__assemble()

    def __assemble(self):
        if self.R.mode != SCHC_MODE.NO_ACK:
            self.logger(1, "  win =", self.win)
        a = []
        for i in sorted(self.fragment_list.items(), reverse=True,
                        key=(lambda kv:
                             (0 if kv[0]==self.R.fcn_all_1 else kv[0]))):
            self.logger(2, "fcn =", i[0], "fragment =", i[1])
            if i[1]:
                a.append(i[1])
        return join_frag_list(a)
        #return "".join(a) # XXX:merge


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
    def __init__(self, R, dtag, scheduler=default_scheduler, timer_t1=5,
                 timer_t3=10, timer_t4=10, timer_t5=15, logger=default_logger):
        self.R = R
        self.dtag = dtag
        self.scheduler = scheduler
        self.timer_t1 = timer_t1
        self.timer_t3 = timer_t3
        self.timer_t4 = timer_t4
        self.timer_t5 = timer_t5
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
        # once the state moves into CHECKING or later,
        # new win must not be received.
        if (len(self.win_list) != 0 and self.win_list[-1].win != fgh.win):
            if self.msg_state not in [STATE_MSG.INIT, STATE_MSG.CONT]:
                self.logger(1, "ERROR: new win is not allowed in CHECK state.")
                return (STATE.FAIL, None)
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
            if ret == STATE.CONT:
                timer = self.timer_t1
            else:
                timer = self.timer_t3
            #
            self.ev = self.scheduler.enter(timer, 1, self.kill, (None,))
            self.logger(3, "scheduling kill %s dtag=%d" % (ret, self.dtag),
                        "ev=", self.ev)
            return ret, None
        elif ret in [STATE.ALL0_OK, STATE.ALL1_OK]:
            if self.ack_payload == None:
                raise AssertionError("ack_payload hasn't been set in %s." % ret)
            return ret, self.ack_payload
        elif ret == STATE.CHECK_ALL0:
            self.ack_payload = None
            if fgh.R.mode == SCHC_MODE.ACK_ON_ERROR:
                # if all the fragments in a window is received, all bits in
                # the internal bitmap are on. i.e. equal to (2**bitmap_size)-1
                # if so, skip to send the ack, otherwise send an ack.
                if w.all_fragments_received():
                    # change the state just for the logging. 
                    w.win_state.set(STATE.ALL0_OK)
                    w.win_state.set(STATE.WIN_DONE)
                    timer = self.timer_t4
                else:
                    self.ack_payload = w.make_ack0(fgh)
                    w.win_state.set(STATE.ALL0_NG)
                    timer = self.timer_t3
            else:
                self.ack_payload = w.make_ack0(fgh)
                if w.all_fragments_received():
                    w.win_state.set(STATE.ALL0_OK)
                    timer = self.timer_t4
                else:
                    w.win_state.set(STATE.ALL0_NG)
                    timer = self.timer_t3
            #
            self.ev = self.scheduler.enter(timer, 1, self.kill, (None,))
            self.logger(3, "scheduling kill %s dtag=%d" % (ret, self.dtag),
                        "ev=", self.ev)
            # ack_payload is going to be None if the state is WIN_DONE.
            return w.win_state.get(), self.ack_payload
        elif ret == STATE.CHECK_ALL1:
            self.msg_state = STATE_MSG.CHECKING
            # check MIC
            # XXX is there the case when the MIC is okey but any fragments have
            # not received ?
            self.ack_payload = None
            if self.R.mode == SCHC_MODE.NO_ACK:
                if self.mic_matched(fgh):
                    # change the state just for the logging. 
                    w.win_state.set(STATE.ALL1_OK), None
                    self.collected()
                    return w.win_state.set(STATE.DONE), None
                else:
                    # change the state just for the logging. 
                    w.win_state.set(STATE.ALL1_NG), None
                    self.kill()
                    return STATE.FAIL, "MIC is not matched."
            else:
                if self.mic_matched(fgh):
                    self.collected()
                    # it has to make the ack payload before change the state.
                    self.ack_payload = w.make_ack1(fgh, cbit=1)
                    timer = self.timer_t4
                    w.win_state.set(STATE.ALL1_OK)
                else:
                    # it has to make the ack payload before change the state.
                    self.ack_payload = w.make_ack1(fgh, cbit=0)
                    timer = self.timer_t3
                    w.win_state.set(STATE.ALL1_NG)
                #
                self.ev = self.scheduler.enter(timer, 1, self.kill, (None,))
                self.logger(3, "scheduling kill %s dtag=%d" % (ret, self.dtag),
                            "ev=", self.ev)
                return w.win_state.get(), self.ack_payload
        elif ret == STATE.DONE:
            raise AssertionError("must not com here for STATE.DONE")
        elif ret == STATE.FAIL:
            return ret, None
        else:
            raise AssertionError("ERROR: must not come in with unknown message state %s" % (ret.name))

    def mic_matched(self, fgh):
        self.logger(1, "calculating mic.")
        self.mic = self.R.C.mic_func.get_mic(self.assemble())
        if fgh.mic == self.mic:
            self.logger(1, "mic is matched.")
            return True
        else:
            self.logger(1, "mic is NOT matched. received={} calculated={}".
                        format(fgh.mic, self.mic))
            return False

    def assemble(self):
        '''
        assuming that no event is scheduled when assemble() is called.
        '''

        # XXX:merge (dominique)
        #message = join_frag_list([i.assemble() for i in self.win_list])
        #return message

        # XXX:merge (soichi)
        #return pb.bit_to("".join([i.assemble() for i in self.win_list]),
        #                 ljust=True)

        message = join_frag_list([i.assemble() for i in self.win_list])
        return my_bit_to(message, ljust=True)

    def collected(self):
        self.msg_state = STATE_MSG.COLLECTED

    def is_collected(self):
        return self.msg_state == STATE_MSG.COLLECTED

    def served(self):
        self.msg_state = STATE_MSG.SERVED

    def is_served(self):
        return self.msg_state == STATE_MSG.SERVED

    def kill(self, *args):
        self.msg_state = STATE_MSG.DEAD

    def is_dead(self):
        return self.msg_state == STATE_MSG.DEAD

    def purge(self):
        if not self.is_dead():
            raise AssertionError("invalid state, message should not be purged.")
        self.ev = None
        if hasattr(self, "win_list"):
            for i in self.win_list:
                i.purge()
            del(self.win_list)
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
    def __init__(self, scheduler=default_scheduler,
                 timer_t1=5, timer_t3=10,
                 timer_t4=10, timer_t5=15, logger=default_logger):
        self.logger = logger
        self.scheduler = scheduler
        self.timer_t1 = timer_t1
        self.timer_t3 = timer_t3
        self.timer_t4 = timer_t4
        self.timer_t5 = timer_t5
        self.msg_list = {}
        # set fragment rule db.
        self.frdb = schc_fragment_ruledb()

    def set_context(self, context_file):
        return self.frdb.load_context_json_file(context_file)

    def set_context_json_str(self, context_json_str):
        return self.frdb.load_context_json_str(context_json_str)
    
    def set_rule(self, cid, rule_file):
        return self.frdb.load_json_file(cid, rule_file)

    def set_rule_json_str(self, cid, rule_json_str):
        return self.frdb.load_json_str(cid, rule_json_str)
    
    def defrag(self, cid, recvbuf):
        '''
        cid: context identifier
        recvbuf: bytearray received
        '''
        C = self.frdb.get_runtime_context(cid)
        fgh = sfh.frag_receiver_rx(C, recvbuf)
        fgh.finalize(self.frdb.get_runtime_rule(cid, fgh.rid))
        # search the list for the fragment.
        # assuming that dtag is the unique key for each originalipv6 packet
        # before fragmented..
        m = self.msg_list.get(fgh.dtag)
        # destruct the message holder if dead
        if m:
            if m.R.mode == SCHC_MODE.NO_ACK:
                if m.is_dead() or m.is_served():
                    self.logger(1, "remove the old message holder for dtag =",
                                fgh.dtag)
                    m = None
            else:
                if m.is_dead():
                    self.logger(1, "remove the old message holder for dtag =",
                                fgh.dtag)
                    m = None
        # create a message holder
        if not m:
            m = defragment_message(fgh.R, fgh.dtag, scheduler=self.scheduler,
                                   timer_t1=self.timer_t1,
                                   timer_t3=self.timer_t3,
                                   timer_t4=self.timer_t4,
                                   timer_t5=self.timer_t5,
                                   logger=self.logger)
            self.msg_list[fgh.dtag] = m
        #
        rx_ret, tx_obj = m.add(fgh)
        if rx_ret == STATE.FAIL:
            # assumeing any message have been showed, just ignore it.
            m.kill()
        elif rx_ret == STATE.ABORT:
            m.kill()
        #
        return rx_ret, fgh, tx_obj

    def dig(self):
        '''
        dig the messages.
        if the state of the message is COLLECTED, assemble the fragments
        and put to the return.
        if the state of the message is DEAD, purge it.
        '''
        self.logger(3, "digging list size =", len(list(self.msg_list.items())))
        ret = []
        purge_list = []
        for k, m in self.msg_list.items():
            if m.is_collected():
                ret.append(m.assemble())
                self.logger(1, "digged dtag =", m.dtag)
                m.served()
            #
            if m.is_dead():
                m.purge()
                purge_list.append(k)
        #
        for i in purge_list:
            self.logger(1, "deleted dtag =", i)
            self.msg_list.pop(i)
        #
        return ret
