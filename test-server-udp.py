#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
from socket import *
import schc_fragment_receiver as sfr
from pybinutil import *

debug_level = 0

def debug_print(*argv):
    if debug_level:
        print("DEBUG: ", argv)

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
    #p.add_argument("-O", action="store", dest="out_file", default="-",
    #    help="specify a output file, default is stdout.")
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

server = (opt.server_address, opt.server_port)
print("server:", server)

s = socket(AF_INET, SOCK_DGRAM)
s.bind(server)

# just send a message to trigger the lorawan network server.
def send_client_trigger(s):
    msg = "Hey!"
    try:
        s.settimeout(1)
        s.sendto(msg, server)
    except Exception as e:
        print("ERROR: ", e)
        exit(0)
    print("sent: ", msg)

# send_client_trigger(s)

#
context = sfr.schc_context(0)
factory = sfr.schc_defragment_factory(logger=debug_print)

opt.timeout_all_1 = 2

s.settimeout(None)
while True:

    print("waiting...")
    try:
        rx_data, client = s.recvfrom(128)
        # for py2, py3 compatibility
        if type(rx_data) == str:
            rx_data = bytearray([ord(rx_data[i]) for i in range(len(rx_data))])
        print("received:", pybinutil.to_hex(rx_data), "from", client)

        # trying to defrag
        ret, buf = factory.defrag(context, rx_data)
        if ret == sfr.SCHC_DEFRAG_CONT:
            print("not yet")
        elif ret == sfr.SCHC_DEFRAG_GOT_ALL0:
            print("sent ack.", pybinutil.to_hex(buf))
            s.sendto(buf, client)
        elif ret == sfr.SCHC_DEFRAG_GOT_ALL1:
            print("received." % (pybinutil.to_hex(buf)))
            print("finished, but waiting something in %d seconds." % opt.timeout_all_1)
            s.sendto(buf, client)
            s.settimeout(opt.timeout_all_1) # XXX it should be done in the factory.
        elif ret == sfr.SCHC_DEFRAG_ACK:
            print("sending ack")
            s.sendto(buf, client)
            print("sent: ", pybinutil.to_hex(buf))
        else:
            print("DEBUG:", ret, buf)

    except Exception as e:
        print("XXX", e)
        #print("XXX timeout [%s]" % dir(e))

if ret == sfr.SCHC_DEFRAG_WAIT1:
    print("done.")
    pybinutil.to_hex(buf)
