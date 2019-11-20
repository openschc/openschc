#---------------------------------------------------------------------------

import sys
import pprint

enable_debug_print = False

def set_debug_output(state):
    global enable_debug_print
    if state:
        enable_debug_print = True
    else:
        enable_debug_print = False

def dprint(*args, **kw):
    """Debug print"""
    global enable_debug_print
    if enable_debug_print:
        print(*args, **kw)

def dpprint(*args, **kw):
    """Debug print"""
    global enable_debug_print
    if enable_debug_print:
        pprint.pprint(*args, **kw)

trace_print_function = print

def set_trace_function(new_trace_print_function):
    global trace_print_function
    result = trace_print_function
    trace_print_function = new_trace_print_function
    return result

def dtrace(*args, **kw):
    global trace_print_function
    if trace_print_function is not None:
        trace_print_function(*args, **kw)

#---------------------------------------------------------------------------
