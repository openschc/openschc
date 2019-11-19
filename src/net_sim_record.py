
#---------------------------------------------------------------------------
"""
Framework for recording simulations:
- The state of every node of the simulation is collected and stored
  after every event (and after).
- All the log(...) and the dtrace(...) that occured between two events
  are recorded with the state

see in `test_frag_new.py`, the entries of `simul_config` starting with 'record'
"""

# TODO: some recording of the add_event / packets sent / cancel_event

import sys
import json
import pprint
import io
import gen_utils

class SimulRecordingObserver:
    """The class is used to record the state of the simulation
    (e.g. of the nodes) before and after each event.
    """
    def __init__(self, simul):
        self.simul = simul


    def start_record(self, file_name):
        self.file_name = file_name
        self.has_initial_state = False
        self.previous_dtrace = gen_utils.set_trace_function(self.trace_function)
        self.out = open(file_name, "w")
        self.log_line_list = []
        self.trace_line_list = [] # print could also be recorded for tests?

    def sched_observer_func(self, event_name, event_info, **kw):
        is_init = False
        if event_name == "sched-pre-event":
            if not self.has_initial_state:
                event_name = "sim-start"
                is_init = True
                self.has_initial_state = True
            else:
                return # note: only post-event is used (except for init).
        clock, event_id, callback, args = event_info
        if event_name == "sched-post-event":
            self
        info = {
            "event": event_name,
            "clock": clock,
            "event-id": event_id,
            "class_name": callback.__self__.__class__.__name__,
            "callback_name": callback.__name__,
            "log": self.log_line_list,
            "trace": self.trace_line_list
        }
        self.log_line_list = []
        self.trace_line_list = []
        info["state"] = self.simul.get_all_state(is_init=is_init, **kw)
        format =  self.simul.simul_config.get("record.format")
        if format == "pprint":
            print(pprint.pformat(info), file=self.out)
        elif format == "json":
            print(json.dumps(info), file=self.out)
        else: raise ValueError("unknown record.format", format)


    def record_log(self, line):
        self.log_line_list.append(line)

    def trace_function(self, *args, **kw):
        content = io.StringIO()
        print(*args, **kw, file=content, end="")
        self.trace_line_list.append(content.getvalue())
        if self.previous_dtrace is not None:
            self.previous_dtrace(content.getvalue())

    def stop_record(self):
        self.out.close()
        print("+ recorded all state in '{}'".format(self.file_name))

#---------------------------------------------------------------------------
