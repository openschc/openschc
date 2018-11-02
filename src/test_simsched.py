# C.A. 2018

from simsched import SimulScheduler

scheduler = SimulScheduler()

def callback(arg1, arg2, scheduler=scheduler):
    print("clock=%s callback, arg1=%s, arg2=%s" % (scheduler, arg1, arg2))

scheduler.add_event(callback, )
scheduler.run()
