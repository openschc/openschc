#---------------------------------------------------------------------------

import sys
import pprint

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

#---------------------------------------------------------------------------
