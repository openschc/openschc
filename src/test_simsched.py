# C.A. 2018

from simsched import SimulScheduler

scheduler = SimulScheduler()

def callback(arg1, arg2, scheduler=scheduler):
    print("clock=%s callback, arg1=%s, arg2=%s" % (
        scheduler.get_clock(), arg1, arg2))
    if arg1 == "1:a1":
        scheduler.add_event(1, callback, ("2:a1", "2:a2"))

scheduler.add_event(3, callback, ("3:a1", "3:a2"))
scheduler.add_event(1, callback, ("1:a1", "1:a2"))
scheduler.run()
