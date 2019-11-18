
#---------------------------------------------------------------------------

import sys
import json
import pprint

class SimulRecordingObserver:
    """The class is used to record the state of the simulation 
    (e.g. of the nodes) before and after each event.
    """
    def __init__(self, simul, file_name):
        self.simul = simul
        self.out = open(file_name, "w")

    def sched_observer_func(self, event_name, event_info):
        if event_name == "sched-pre-event":
            return # XXX now - only post-event
        clock, event_id, callback, args = event_info
        if event_name == "sched-post-event":
            log_list = self.simul._get_and_reset_record_log_list()
        info = {
            "event": event_name,
            "clock": clock,
            "event-id": event_id,
            "class_name": callback.__self__.__class__.__name__,
            "callback_name": callback.__name__,
            "log_list": log_list
        }
        info = self.simul.get_all_state()
        format =  self.simul.simul_config.get("record.format")
        if format == "pprint":
            print(pprint.pformat(info), file=self.out)
        elif format == "json":
            print(json.dumps(info), file=self.out)
        else: raise ValueError("unknown record.format", format)
        

    def close(self):
        self.out.close()

#---------------------------------------------------------------------------
