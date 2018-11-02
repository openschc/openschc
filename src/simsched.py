# C.A. 2018


from base_import import *  # used for now for differing modules in py/upy

class SimulScheduler:
    def __init__(self):
        self.scheduler = sched.scheduler(self.get_clock, self._wait_delay)
        self.clock = 0

    # sched.scheduler API

    def get_clock(self):
        return self.clock

    def _wait_delay(self, delay):
        self.clock += delay

    def run(self):
        self.scheduler.run()

    # external API

    def add_event(self, rel_time, callback, args):
        self.scheduler.enter(rel_time, 0, callback, args)


class RealTimeScheduler:
    """XXX.TODO"""
    pass
