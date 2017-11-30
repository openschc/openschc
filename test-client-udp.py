#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
from socket import *
import schc_fragment_sender as sfs
import time
from pybinutil import *
from random import choice

debug_level = 0

def debug_print(*argv):
    level = argv[0]
    if debug_level >= level:
        print("DEBUG: ", argv[1:])

def parse_args():
    p = argparse.ArgumentParser(description="this is SCHC example.",
                                epilog=".")
    p.add_argument("server_address", metavar="SERVER",
                   help="specify the ip address of the server.")
    p.add_argument("server_port", metavar="PORT", type=int,
                   help="specify the port number in the server.")
    p.add_argument("-I", action="store", dest="msg_file", default="-",
                   help="specify the file name including the message, default is stdin.")
    p.add_argument("--interval", action="store", dest="interval", type=int,
                   default=1, help="specify the interval for each sending.")
    p.add_argument("--fgp-size", action="store", dest="fgp_size", type=int,
                   default=4, help="specify the payload size in the fragment. default is 4.")
    p.add_argument("--rid", action="store", dest="rule_id", type=int, default=0,
                   help="specify the rule id.  default is 0")
    p.add_argument("--loss", action="store", metavar="LOSS_LIST", dest="_str_loss_list", default="",
                   help="specify the index numbers to be lost for test. e.g.  --loss=3,8 means the 3rd and 8th packets are going to be lost.")
    p.add_argument("--loss-random", action="store_true", dest="loss_random",
                   help="enable to lose a fragment randomly for test.")
    p.add_argument("-v", action="store_true", dest="f_verbose", default=False,
                   help="enable verbose mode.")
    p.add_argument("-d", action="append_const", dest="_f_debug", default=[],
                   const=1, help="increase debug mode.")
    p.add_argument("--verbose", action="store_true", dest="f_verbose",
                   default=False, help="enable verbose mode.")
    p.add_argument("--debug", action="store", metavar="DEBUG_LEVEL", dest="_debug_level",
                   type=int, default=-1, help="specify a debug level.")
    p.add_argument("--version", action="version", version="%(prog)s 1.0")

    args = p.parse_args()
    if len(args._f_debug) and args._debug_level != -1:
        print("ERROR: use either -d or --debug option.")
        exit(1)
    if args._debug_level == -1:
        args._debug_level = 0
    args.debug_level = len(args._f_debug) + args._debug_level
    #
    args.loss_list = []
    if args._str_loss_list:
        args.loss_list = [int(i) for i in args._str_loss_list.split(",")]

    return args

'''
main code
'''
opt = parse_args()
debug_level = opt.debug_level

server = (opt.server_address, opt.server_port)
debug_print(1, "server:", server)

s = socket(AF_INET, SOCK_DGRAM)
#s.setblocking(True)
s.settimeout(5)

# create a message buffer
if opt.msg_file == "-":
    fp = sys.stdin
else:
    fp = open(opt.msg_file)

#message = "".join(fp.readlines())
message = "Hello, this is a fragmentation test of SCHC."
fgp_size = opt.fgp_size

# fragment instance
context = sfs.schc_context(0)
factory = sfs.schc_fragment_factory(context, opt.rule_id, logger=debug_print)
factory.setbuf(message)

n_packet = 0

while True:

    # CONT: send it and get next fragment.
    # WAIT_ACK: send it and wait for the ack.
    # DONE: dont need to send it.
    # ERROR: error happened.
    tx_ret, tx_data, = factory.next_fragment(fgp_size)
    n_packet += 1

    # whole fragments have been sent and all the ack has been received.
    if tx_ret == sfs.SCHC_FRAG_DONE:
        debug_print(1, "done.")
        break

    # error!
    if tx_ret == sfs.SCHC_FRAG_ERROR:
        raise AssertionError("something wrong in fragmentation.")
        break

    if n_packet in opt.loss_list or (opt.loss_random and choice([True, False])):
        debug_print(1, "drop packet", pybinutil.to_hex(tx_data))
        continue

    debug_print(1, "packet", pybinutil.to_hex(tx_data))

    try:
        s.sendto(tx_data, server)
    except Exception as e:
        debug_print(1, e)
        debug_print(1, "timeout in sending")
        continue

    # CONT
    if tx_ret == sfs.SCHC_FRAG_CONT:
        # need to rest fragmentation.
        time.sleep (opt.interval)
        continue

    # WAIT_ACK
    # a part of or whole fragments have been sent and wait for the ack.
    debug_print(1, "waiting an ack", tx_ret)
    try:
        rx_data, peer = s.recvfrom(128)
        # for py2, py3 compatibility
        if type(rx_data) == str:
            rx_data = bytearray([ord(rx_data[i]) for i in range(len(rx_data))])
        debug_print(1, "received:", pybinutil.to_hex(rx_data), "from", peer)

        ack_ok = factory.is_ack_ok(rx_data)
        if ack_ok:
            continue
    except Exception as e:
        debug_print(1, e)
        debug_print(1, "timeout in receive")

