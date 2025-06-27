#---------------------------------------------------------------------------

import sys
import pprint
import types

enable_debug_print = False

def set_debug_output(state):
    global enable_debug_print
    if state:
        enable_debug_print = True
    else:
        enable_debug_print = False

print_function = print

def set_print_function(new_print_function):
    global print_function
    result = print_function
    print_function = new_print_function
    return result

def dprint(*args, **kw):
    """Debug print"""
    global enable_debug_print
    if enable_debug_print:
        print_function(">", *args, **kw)
        sys.stdout.flush()

def dpprint(*args, **kw):
    """Debug print"""
    global enable_debug_print
    if enable_debug_print:
        text = pprint.pformat(*args, **kw)
        print_function(text, end="")
        sys.stdout.flush()

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
        sys.stdout.flush()

#---------------------------------------------------------------------------

def sanitize_value(value, helper_table={}):
    """Sanitize value for printing"""
    result = {}
    if isinstance(value, types.MethodType):
        instance = value.__self__
        if instance is not None:
            class_name = instance.__class__.__name__
            method_name = value.__func__.__name__
            result["class"] = class_name
            result["method"] = method_name
            if class_name in helper_table:
                result = helper_table[class_name](instance, result.copy())
        else:
            raise ValueError("Not implemented yet: unbound methods", value)
    elif isinstance(value, tuple):
        result = tuple(sanitize_value(x, helper_table) for x in value)
    elif isinstance(value, list):
        result = [sanitize_value(x, helper_table) for x in value]
    elif isinstance(value, dict):
        result = { k:sanitize_value(v, helper_table) for k,v in value.items() }
    elif isinstance(value, object) and value.__class__.__module__ == "frag_msg":
        result = "<instance of {}>".format(value.__class__.__name__)
    else:
        result = value
    return result

#---------------------------------------------------------------------------
