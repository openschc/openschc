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
        pprint(*args, **kw)

def dtrace(*args, **kw):
    print(*args, **kw)
    
#---------------------------------------------------------------------------
