#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
from socket import *
import schc_fragment_receiver as sfr
from pybinutil import *
from simple_sched import *

debug_level = 0

def debug_print(*argv):
    level = argv[0]
    if debug_level >= level:
        print("DEBUG: ", argv[1:])

# just send a message to trigger the lorawan network server.
def send_client_trigger(s):
    msg = "Hey!"
    try:
        s.settimeout(1)
        s.sendto(msg, server)
    except Exception as e:
        debug_print(1, "ERROR: ", e)
        exit(0)
    debug_print(1, "sent: ", msg)

def parse_args():
    p = argparse.ArgumentParser(description="this is example.",
                                epilog="this is the tail story.")
    p.add_argument("server_port", metavar="PORT", type=int,
        help="specify the port number in the server.")
    p.add_argument("--address", action="store", dest="server_address",
        default="",
        help="specify the ip address of the server to be bind. default is any.")
    p.add_argument("--port", action="store", dest="conf_file", default="",
        help="specify the configuration file.")
    p.add_argument("--timeout", action="store", dest="timeout",
        type=int, default=3,
        help="specify the number of the timeout.")
    p.add_argument("-v", action="store_true", dest="f_verbose", default=False,
        help="enable verbose mode.")
    p.add_argument("-d", action="append_const", dest="_f_debug", default=[],
        const=1, help="increase debug mode.")
    p.add_argument("--verbose", action="store_true", dest="f_verbose",
        default=False, help="enable verbose mode.")
    p.add_argument("--debug", action="store", dest="_debug_level",
        type=int, default=-1,
        help="specify a debug level.")
    p.add_argument("--version", action="version", version="%(prog)s 1.0")

    args = p.parse_args()
    if len(args._f_debug) and args._debug_level != -1:
        print("ERROR: use either -d or --debug option.")
        exit(1)
    if args._debug_level == -1:
        args._debug_level = 0
    args.debug_level = len(args._f_debug) + args._debug_level

    return args

'''
main
'''
opt = parse_args()
debug_level = opt.debug_level

# set up the server
server = (opt.server_address, opt.server_port)
debug_print(1, "server:", server)

s = socket(AF_INET, SOCK_DGRAM)
s.bind(server)

# call the client trigger if this server is running on the end node.
# send_client_trigger(s)

#
sched = simple_sched.simple_sched()
context = sfr.schc_context(0)
factory = sfr.schc_defragment_factory(scheduler=sched, logger=debug_print)

while True:

    # execute scheduler and get the number for timeout..
    timer = sched.execute()
    if not timer:
        s.setblocking(True)
    else:
        s.settimeout(timer)

    # find a message for which a sender has sent all-1.
    for i in factory.dig():
        debug_print(1, "defragmented message: [%s]" % i)

    try:
        #
        # if timeout happens recvfrom() here, go to exception.
        #
        rx_data, client = s.recvfrom(128)
        # for py2, py3 compatibility
        if type(rx_data) == str:
            rx_data = bytearray([ord(rx_data[i]) for i in range(len(rx_data))])
        debug_print(1, "received:", pybinutil.to_hex(rx_data), "from", client)

        # trying to defrag
        ret, data = factory.defrag(context, rx_data)
        if ret == sfr.SCHC_DEFRAG_CONT:
            pass
        elif ret == sfr.SCHC_DEFRAG_GOT_ALL0:
            debug_print(1, "sent ack.", pybinutil.to_hex(data))
            s.sendto(data, client)
        elif ret == sfr.SCHC_DEFRAG_DONE:
            debug_print(1, "finished.")
            debug_print(1, data)
        elif ret == sfr.SCHC_DEFRAG_GOT_ALL1:
            debug_print(1, "received." % pybinutil.to_hex(data))
            s.sendto(data, client)
            debug_print(1, "finished, but waiting something in %d seconds." %
                        opt.timeout)
        else:
            debug_print(1, "DEBUG:", ret, buf)

    except Exception as e:
        if "timeout" in repr(e):
            debug_print(1, "timed out")
        else:
            debug_print(1, "Exception: [%s]" % repr(e))

