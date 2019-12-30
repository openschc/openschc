"""
.. module:: simul
   :platform: Python

Framework for recording simulations:
- The state of every node of the simulation is collected and stored
  after every event (and after).
- All the log(...) and the dtrace(...) that occured between two events
  are recorded with the state

see in `test_frag_new.py`, the entries of `simul_config` starting with 'record'
"""

# TODO: some recording of the add_event / packets sent / cancel_event

import json
import pprint
import io
import os
import gen_utils

RECORD_FILE_NAME = "record.log"
LOGGING_FILE_NAME = "logging.log"
TRACE_FILE_NAME = "trace.log"
PRINT_FILE_NAME = "print.log"

class SimulResultManager:

    def __init__(self, dir_name):
        self.dir_name = dir_name
        self._ensure_dir()

    def get_file_name(self, suffix):
        assert self.dir_name is not None
        return os.path.join(self.dir_name, suffix)

    def _ensure_dir(self):
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)

class SimulRecordingObserver:
    """The class is used to record the state of the simulation
    (e.g. of the nodes) before and after each event.
    """
    def __init__(self, simul):
        self.simul = simul
        self.manager = None
        self.quiet = False

    def start_record(self, dir_name, quiet=False):
        self.manager = SimulResultManager(dir_name)
        self.quiet = quiet
        self.dir_name = dir_name
        self.has_initial_state = False
        self.previous_dtrace = gen_utils.set_trace_function(self.trace_function)
        unused = gen_utils.set_print_function(self.print_function)
        self.log_line_list = []
        self.trace_line_list = [] # print could also be recorded for tests?
        self.print_line_list = []

        self.record_file = open(self.manager.get_file_name(RECORD_FILE_NAME), "w")
        self.log_file = open(self.manager.get_file_name(LOGGING_FILE_NAME), "w")
        self.trace_file = open(self.manager.get_file_name(TRACE_FILE_NAME), "w")
        self.print_file = open(self.manager.get_file_name(PRINT_FILE_NAME), "w")

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
            pass # XXX: do something
        info = {
            "event": event_name,
            "clock": clock,
            "event-id": event_id,
            "class_name": callback.__self__.__class__.__name__,
            "callback_name": callback.__name__,
            "log": self.log_line_list,
            "trace": self.trace_line_list,
            "print": self.print_line_list
        }
        self.log_line_list = []
        self.trace_line_list = []
        self.print_line_list = []
        info["state"] = self.simul.get_all_state(is_init=is_init, **kw)
        format =  self.simul.simul_config.get("record.format")
        if format == "pprint":
            print(pprint.pformat(info), file=self.record_file)
        elif format == "json":
            print(json.dumps(info), file=self.record_file)
        else: raise ValueError("unknown record.format", format)

    def record_log(self, line):
        self.log_file.write(line+"\n")
        self.log_line_list.append(line)

    def trace_function(self, *args, **kw):
        content = io.StringIO()
        print(*args, file=content, **kw)
        self.trace_line_list.append(content.getvalue())
        self.trace_file.write(content.getvalue())
        if self.previous_dtrace is not None and not self.quiet:
            self.previous_dtrace(content.getvalue(), end="")

    def print_function(self, *args, **kw):
        content = io.StringIO()
        print(*args, file=content, **kw)
        self.print_line_list.append(content.getvalue())
        self.print_file.write(content.getvalue())

    def stop_record(self):
        self.record_file.close()
        self.log_file.close()
        self.trace_file.close()
        if not self.quiet:
            print("> recorded all state in '{}'".format(self.manager.get_file_name("")))

    def __del__(self):
        self.print_file.close() # XXX: this is done implicitly anyway

#---------------------------------------------------------------------------
