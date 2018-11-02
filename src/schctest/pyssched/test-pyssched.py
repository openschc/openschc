from __future__ import print_function

import random
import time

try:
    from pyssched import pyssched as ps
except:
    import pyssched as ps

def print_time(tag):
    print("called: n=%s delta=%f" % (tag, time.time() - t0))

t0 = time.time()
s = ps.ssched()

n = 0

while True:

    if not s.empty():
        print("sched queue len=%d" % len(list(s.queue)))
    timer = s.execute()

    t = random.choice([0, 2, 3])
    if t:
        s.enter(t, 1, print_time, ("%d"%n,))
        n += 1

    if timer > 0.:
        print("sleeping in %f" % timer)
    time.sleep(timer)

