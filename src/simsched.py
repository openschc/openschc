# C.A. 2018


from base_import import *  # used for now for differing modules in py/upy


class SlowSimulScheduler:
    def __init__(self):
        self.queue = []
        self.clock = 0
        self.event_id = 0

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

    # external API

    def add_event(self, rel_time, callback, args):
        assert rel_time >= 0
        clock = self.get_clock()
        abs_time = clock+rel_time
        self.queue.append((abs_time, self.event_id, callback, args))
        self.event_id += 1


    def get_next_event_time(self):


SimulScheduler = SlowSimulScheduler


class SimulSchedulerOld:
    def __init__(self):
        #self.scheduler = sched.scheduler(self.get_clock, self._wait_delay)
        self.scheduler = sched.ssched(self.get_clock)
        self.clock = 0

    # sched.scheduler API

    def get_clock(self):
        return self.clock

    def _wait_delay(self, delay):
        self.clock += delay

    def run(self):
        #self.scheduler.run()
        self.scheduler.execute()

    # external API

    def add_event(self, rel_time, callback, args):
        self.scheduler.enter(rel_time, 0, callback, args)
