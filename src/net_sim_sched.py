"""
.. module:: net_sim_sched
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from gen_base_import import *  # used for now for differing modules in py/upy
from gen_utils import dprint, sanitize_value


# XXX: this scheduler can be optimized by not sorting every time
class SimulScheduler:
    def __init__(self):
        self.queue = []
        self.clock = 0
        self.next_event_id = 0
        self.current_event_id = None
        self.observer = None
        self.item=0

    def set_observer(self, observer):
        assert self.observer is None
        self.observer = observer
        
    # sched.scheduler API

    def get_clock(self):
        return self.clock

    def _wait_delay(self, delay):
        self.clock += delay

    def run(self):
        factor= 10
        if self.item % factor == 0:
            seq = ["|", "/", "-", "\\", "-"]
            print ("{:s}".format(seq[(self.item//factor)%len(seq)]),end="\b", flush=True)
        self.item +=1

        for q in self.queue:
            print ("queue ", q)

        while len(self.queue) > 0:
            self.queue.sort()
            event_info = self.queue.pop(0)
            self.clock, event_id, callback, args, session_id = event_info
            self.current_event_id = event_id
            if self.observer is not None:
                self.observer("sched-pre-event", event_info)
            callback(*args)
            if self.observer is not None:
                self.observer("sched-post-event", event_info)
            dprint("Queue running event -> {}, callback -> {}".format(event_id, callback.__name__))

    # external API

    def add_event(self, rel_time, callback, args, session_id = None):
        dprint("AAdd event {}".format(sanitize_value(self.queue)))
        dprint("AAargs", session_id)
        dprint("callback set -> {}".format(callback.__name__))
        assert rel_time >= 0
        event_id = self.next_event_id
        self.next_event_id += 1
        clock = self.get_clock()
        abs_time = clock + rel_time
        self.queue.append((abs_time, event_id, callback, args, session_id))
        return event_id

    def cancel_event(self, event_id):
        for i,full_event in enumerate(self.queue):
            if full_event[1] == event_id:
                self.queue.pop(i)
                print("Here Cancel Event?")
                return True
        return False

    def cancel_session(self, session_id = None): #TODO
        elm = []
        indices = [i for i, x in enumerate(self.queue) if x[4] == session_id]
        self.queue = [i for j, i in enumerate(self.queue) if j not in indices]
        return elm

    def get_next_event_time(self):
        if len(self.queue) == 0:
            return None
        else:
            self.queue.sort()
            return self.queue[0][0]

    # Internal API for Simulator get_state_info - don't use in other contexts

    def _get_queue_content(self, helper_table={}):
        result = self.queue.copy()
        result.sort()
        return sanitize_value(result, helper_table)

    def _get_event_id(self):
        return self.current_event_id
    

#---------------------------------------------------------------------------
