"""
.. module:: simsched
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

# XXX: this scheduler can be optimized by not sorting every time
class SimulScheduler:
    def __init__(self):
        self.queue = []
        self.clock = 0
        self.next_event_id = 0

    # sched.scheduler API

    def get_clock(self):
        return self.clock

    def _wait_delay(self, delay):
        self.clock += delay

    def run(self):
        while len(self.queue) > 0:
            self.queue.sort()
            self.clock, event_id, callback, args = self.queue.pop(0)
            callback(*args)
            print("Queue running event -> {}, callback -> {}".format(event_id, callback.__name__))

    # external API

    def add_event(self, rel_time, callback, args):
        print("Add event {}".format(self.queue))
        print("callback set -> {}".format(callback.__name__))
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
