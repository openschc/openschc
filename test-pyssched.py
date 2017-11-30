#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import random
import time
from pyssched import *

def print_time(tag):
    print("called: n=%s delta=%f" % (tag, time.time() - t0))

t0 = time.time()
s = pyssched()

n = 0

while True:

    if len(s.queue):
        print("sched queue len=%d" % len(s.queue))
    timer = s.execute()

    t = random.choice([0, 2, 3])
    if t:
        s.enter(t, 1, print_time, ("%d"%n,))
        n += 1

    if timer > 0.:
        print("sleeping in %f" % timer)
    time.sleep(timer)

