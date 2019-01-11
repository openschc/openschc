#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from socket import *
import pybinutil as pb
import pyssched as ps
import traceback
from schc_param import *
import schc_fragment_receiver as sfr
from debug_print import *

def parse_args():
    p = argparse.ArgumentParser(
            description="a sample code for the fragment receiver.",
            epilog="")
    p.add_argument("server_port", metavar="PORT", type=int,
                   help="specify the port number in the server.")
    p.add_argument("--address", action="store", dest="server_address",
                   default="",
                   help="specify the ip address of the server to be bind. default is any.")
    p.add_argument("--context-file", action="store", dest="context_file",
                   help="specify the file name containing a context.")
    p.add_argument("--rule-file", action="store", dest="_rule_files",
                   help="specify the file name containing a rule.")
    p.add_argument("--timer", action="store", dest="timer_t1",
                   type=int, default=DEFAULT_TIMER_T1,
                   help="specify the number of timer T1.")
    p.add_argument("--timer-t3", action="store", dest="timer_t3",
                   type=int, default=DEFAULT_TIMER_T3,
                   help="specify the number of timer T3.")
    p.add_argument("--timer-t4", action="store", dest="timer_t4",
                   type=int, default=DEFAULT_TIMER_T4,
                   help="specify the number of timer T4.")
    p.add_argument("--timer-t5", action="store", dest="timer_t5",
                   type=int, default=DEFAULT_TIMER_T5,
                   help="specify the number of timer T5.")
    p.add_argument("-d", action="append_const", dest="_f_debug",
                   default=[], const=1, help="increase debug mode.")
    p.add_argument("--debug", action="store", dest="_debug_level",
                   type=int, default=-1, help="specify a debug level.")
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
debug_set_level(opt.debug_level)

# set up the ruledb.
context_file = "example-rule/context-001.json"
rule_files = [
    "example-rule/fragment-rule-001.json",
    "example-rule/fragment-rule-002.json",
    "example-rule/fragment-rule-003.json"
    ]
#
sched = ps.ssched()
factory = sfr.defragment_factory(scheduler=sched,
                                 timer_t1=opt.timer_t1,
                                 timer_t3=opt.timer_t3,
                                 timer_t4=opt.timer_t4,
                                 timer_t5=opt.timer_t5,
                                 logger=debug_print)
cid = factory.set_context(context_file)
factory.set_rule(cid, rule_files)

# set up the server.
server = (opt.server_address, opt.server_port)
debug_print(1, "server:", server)
s = socket(AF_INET, SOCK_DGRAM)
s.bind(server)

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
        rx_data, peer = s.recvfrom(DEFAULT_RECV_BUFSIZE)
        debug_print(1, "message from:", peer)
        #
        # XXX here, should find a context for the peer.
        #
        ret, rx_obj, tx_obj = factory.defrag(cid, rx_data)
        debug_print(1, "parsed:", rx_obj.dump())
        debug_print(2, "hex   :", rx_obj.full_dump())
        #
        if ret in [sfr.STATE.CONT, sfr.STATE.CONT_ALL0, sfr.STATE.CONT_ALL1]:
            pass
        elif ret == sfr.STATE.ABORT:
            debug_print(1, "abort.")
            debug_print(1, "sent  :", tx_obj.dump())
            s.sendto(tx_obj.packet, peer)
        elif ret in [sfr.STATE.ALL0_OK, sfr.STATE.ALL0_NG]:
            if tx_obj:
                debug_print(1, "sening ack for all-0.", tx_obj.dump())
                debug_print(2, "packet:", tx_obj.full_dump())
                s.sendto(tx_obj.packet, peer)
        elif ret in [sfr.STATE.ALL1_OK, sfr.STATE.ALL1_NG]:
            if tx_obj:
                debug_print(1, "sending ack for all-1.", tx_obj.dump())
                debug_print(2, "packet:", tx_obj.full_dump())
                s.sendto(tx_obj.packet, peer)
            if ret == sfr.STATE.ALL1_OK:
                debug_print(1, "finished")
                debug_print(1, "waiting for something in %d seconds." %
                        opt.timer_t3)
        elif ret == sfr.STATE.DONE:
            debug_print(1, "finished.")
        elif ret in [sfr.STATE.WIN_DONE]:
            # ignore it
            pass
        else:
            debug_print(1, ret, ":", tx_obj)

    except Exception as e:
        if "timeout" in repr(e):
            debug_print(1, "timed out:", repr(e))
        else:
            debug_print(1, "Exception: [%s]" % repr(e))
            debug_print(0, traceback.format_exc())

