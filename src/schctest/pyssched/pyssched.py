
'''
derived from python2.7/sched.py
'''
import heapq
import time
from collections import namedtuple

Event = namedtuple('Event', 'time, priority, action, argument')

'''
## Queue length

in Python2, self._queue is list.
in Python3, self._queue is map.

Therefore, you should do like below to get the size of the queue.

    len(list(self.queue))
'''

class ssched:

    def __init__(self, timefunc=time.time):
        '''
        don't need delayfunc
        '''
        self._queue = []
        self.timefunc = timefunc

    def enterabs(self, time, priority, action, argument):
        """Enter a new event in the queue at an absolute time.

        Returns an ID for the event which can be used to remove it,
        if necessary.

        """
        event = Event(time, priority, action, argument)
        heapq.heappush(self._queue, event)
        return event # The ID

    def enter(self, delay, priority, action, argument):
        """A variant that specifies the time as a relative time.

        This is actually the more commonly used interface.

        """
        time = self.timefunc() + delay
        return self.enterabs(time, priority, action, argument)

    def cancel(self, event):
        """Remove an event from the queue.

        This must be presented the ID as returned by enter().
        If the event is not in the queue, this raises ValueError.

        """
        self._queue.remove(event)
        heapq.heapify(self._queue)

    def empty(self):
        """Check whether the queue is empty."""
        return not self._queue

    def run(self):
        '''
        disable run()
        '''
        pass

    def execute(self):
        '''
        execute the actions that are scheduled to be exeucted by now.
        return the wait time to the next item in the queue.
        '''
        q = self._queue
        timefunc = self.timefunc
        pop = heapq.heappop
        now = timefunc()
        while q:
            time, priority, action, argument = checked_event = q[0]
            if now < time:
                return time - now
            else:
                event = pop(q)
                # Verify that the event was not removed or altered
                # by another thread after we last looked at q[0].
                if event is checked_event:
                    action(*argument)
                else:
                    heapq.heappush(q, event)
        # no more entries. 
        return 0.

    @property
    def queue(self):
        """An ordered list of upcoming events.

        Events are named tuples with fields for:
            time, priority, action, arguments

        """
        # Use heapq to sort the queue rather than using 'sorted(self._queue)'.
        # With heapq, two events scheduled at the same time will show in
        # the actual order they would be retrieved.
        events = self._queue[:]
        return map(heapq.heappop, [events]*len(events))

