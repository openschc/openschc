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
import gen_bitarray

RECORD_FILE_NAME = "record.log"
LOGGING_FILE_NAME = "logging.log"
TRACE_FILE_NAME = "trace.log"
PRINT_FILE_NAME = "print.log"
INIT_FILE_NAME = "init.log"
PACKET_FILE_NAME = "packet.log"


def json_sanitize(value):
    if isinstance(value, bytes):
        return "<bytes>"+value.hex()
    elif isinstance(value, bytearray):
        return "<bytearray>"+value.hex()
    elif isinstance(value, gen_bitarray.BitBuffer):
        result = io.StringIO()
        value.display(file=result)
        return "<bitarray>"+result.getvalue()
    else:
        return "<skipped {}>".format(type(value))

class SimulResultManager:
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self._ensure_dir()

    def get_file_name(self, suffix):
        assert self.dir_name is not None
        return os.path.join(self.dir_name, suffix)

    def open(self, file_name, *args, **kwargs):
        return open(self.get_file_name(file_name), *args, **kwargs)

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
        self.previous_dtrace = gen_utils.set_trace_function(self.trace_function)
        unused = gen_utils.set_print_function(self.print_function)
        self.log_line_list = []
        self.trace_line_list = [] # print could also be recorded for tests?
        self.print_line_list = []

        self.record_file = self.manager.open(RECORD_FILE_NAME, "w")
        self.log_file = self.manager.open(LOGGING_FILE_NAME, "w")
        self.trace_file = self.manager.open(TRACE_FILE_NAME, "w")
        self.print_file = self.manager.open(PRINT_FILE_NAME, "w")
        self.packet_file = self.manager.open(PACKET_FILE_NAME, "w")

    def record_initial_state(self, **kw):
        init_file = open(self.manager.get_file_name(INIT_FILE_NAME), "w")
        info = { }
        info["init"] = self.simul.get_init_info(**kw)
        info["state"] = self.simul.get_state_info(**kw)
        format =  self.simul.simul_config.get("record.format")
        if format == "pprint":
            print(pprint.pformat(info), file=init_file)
        elif format == "json":
            print(json.dumps(info, default=json_sanitize), file=init_file)
        else: raise ValueError("unknown record.format", format)
        init_file.close()
        self.has_initial_state = True

    def sched_observer_func(self, event_name, event_info, **kw):
        if event_name == "sched-pre-event":
            return # only record post-event to avoid redundancy

        clock, event_id, callback, args, xxx_extra = event_info # XXX: another argument?
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
        info["state"] = self.simul.get_state_info(**kw)
        format =  self.simul.simul_config.get("record.format")
        if format == "pprint":
            print(pprint.pformat(info), file=self.record_file)
        elif format == "json":
            print(json.dumps(info, default=json_sanitize),
                  file=self.record_file)
        else: raise ValueError("unknown record.format", format)

    def record_packet(self, info):
        format = self.simul.simul_config.get("record.format")
        if format == "pprint":
            print(pprint.pformat(info), file=self.packet_file)
        elif format == "json":
            print(json.dumps(info, default=json_sanitize),
                  file=self.packet_file)
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
        self.packet_file.close()
        if not self.quiet:
            print("> recorded all state in '{}'".format(
                self.manager.get_file_name("")))

    def __del__(self):
        self.print_file.close() # XXX: this is done implicitly anyway

#---------------------------------------------------------------------------
