"""
.. module:: net_sim_sched
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from gen_base_import import *  # used for now for differing modules in py/upy
from gen_utils import dprint

# XXX: this scheduler can be optimized by not sorting every time
class SimulScheduler:
    def __init__(self):
        self.queue = []
        self.clock = 0
        self.next_event_id = 0
        self.observer = None

    def set_observer(self, observer):
        assert self.observer is None
        self.observer = observer
        
    # sched.scheduler API

    def get_clock(self):
        return self.clock

    def _wait_delay(self, delay):
        self.clock += delay

    def run(self):
        while len(self.queue) > 0:
            self.queue.sort()
            event_info = self.queue.pop(0)
            self.clock, event_id, callback, args = event_info
            if self.observer is not None:
                self.observer("sched-pre-event", event_info)
            callback(*args)
            if self.observer is not None:
                self.observer("sched-post-event", event_info)
            dprint("Queue running event -> {}, callback -> {}".format(event_id, callback.__name__))

    # external API

    def add_event(self, rel_time, callback, args):
        dprint("Add event {}".format([e[:-2]+(e[-2].__name__,)+e[-1:] for e in self.queue]))
        dprint("callback set -> {}".format(callback.__name__))
        assert rel_time >= 0
        event_id = self.next_event_id
        self.next_event_id += 1
        clock = self.get_clock()
        abs_time = clock+rel_time
        self.queue.append((abs_time, event_id, callback, args))
        return event_id

    def cancel_event(self, event_id):
        for i,full_event in enumerate(self.queue):
            if full_event[1] == event_id:
                self.queue.pop(i)
                return True
        return False

    def get_next_event_time(self):
        if len(self.queue) == 0:
            return None
        else:
            self.queue.sort()
            return self.queue[0][0]

#---------------------------------------------------------------------------
