#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import sys.implementation
import sys
MICROPYTHON = ( ("implementation" in dir(sys)) and (sys.implementation.name == "micropython"))
if not MICROPYTHON:
    import sys
    import argparse
    import traceback
    from socket import *
import time

if MICROPYTHON:
    def display_mem_available(str):
        gc.collect()
        print (str+', available memory: ', gc.mem_free())
    import gc
    display_mem_available('after "import gc"')
    print ('this is your chance: press Ctrl+C to interrupt execution ...', end='')
    time.sleep(3)
    print ('\nresuming execution')
    import socket

import pybinutil as pb
if not MICROPYTHON:
    import random
from schc_param import *
import schc_fragment_sender as sfs
from debug_print import *
from schc_fragment_ruledb import schc_fragment_ruledb

if not MICROPYTHON:
    def func_loss_list():
        return (n_packet in opt.loss_list)

    def func_loss_rate():
        return (random.random() < opt.loss_rate)

    def func_loss_random():
        return random.choice([True, False])

def schc_sender(msg):
    debug_print(2, "message:", bytes(msg, "utf-8"))
    # XXX assuming that the rule_id is not changed in a session.

    # check if the L2 size is enough to put the message.
    if opt.l2_size >= len(msg):
        debug_print(1, "no need to fragment this message.")
        return

    # prepare fragmenting
    factory = sfs.fragment_factory(frr, logger=debug_print)
    factory.setbuf(msg, dtag=opt.dtag)

    # main loop
    debug_print(1, "L2 payload size: %s" % opt.l2_size)

    global n_packet
    n_packet = 0

    while True:

        # CONT: send it and get next fragment.
        # WAIT_ACK: send it and wait for the ack.
        # DONE: dont need to send it.
        # ERROR: error happened.
        ret, tx_obj = factory.next_fragment(opt.l2_size)
        n_packet += 1

        # error!
        if ret == sfs.STATE.FAIL:
            raise AssertionError("something wrong in fragmentation.")
        elif ret == sfs.STATE.DONE:
            debug_print(1, "done.")
            break
            # end of the main loop

        if not MICROPYTHON and opt.func_packet_loss and opt.func_packet_loss() == True:
            debug_print(1, "packet dropped.")
        else:
            if not MICROPYTHON:
                s.sendto(tx_obj.packet, server)
            else:
                s.send(tx_obj.packet)
            debug_print(1, "sent  :", tx_obj.dump())
            debug_print(2, "hex   :", tx_obj.full_dump())

        if factory.R.mode != SCHC_MODE.NO_ACK and ret != sfs.STATE.CONT:
            # WAIT_ACK
            # a part of or whole fragments have been sent and wait for the ack.
            debug_print(1, "waiting an ack.", factory.state.pprint())
            try:
                if not MICROPYTHON:
                    rx_data, peer = s.recvfrom(DEFAULT_RECV_BUFSIZE)
                else:
                    rx_data, peer = s.rcv(DEFAULT_RECV_BUFSIZE), None
                debug_print(1, "message from:", peer)
                #
                ret, rx_obj = factory.parse_ack(rx_data, peer)
                debug_print(1, "parsed:", rx_obj.dump())
                debug_print(2, "hex   :", rx_obj.full_dump())
                #
                if ret == sfs.STATE.DONE:
                    # finish if the ack against all1 is received.
                    debug_print(1, "done.")
                    break
                    # end of the main loop

            except Exception as e:
                if "timeout" in repr(e):
                    debug_print(1, "timed out to wait for the ack.")
                else:
                    debug_print(1, "Exception: [%s]" % repr(e))
                    if not MICROPYTHON:
                        debug_print(0, traceback.format_exc())

        time.sleep(opt.interval)

if not MICROPYTHON:
    def parse_args():
        def test_1in3(v):
            return not ((v[0] and v[1]) or (v[1] and v[2]) or (v[2] and v[0]))

        p = argparse.ArgumentParser(
                description="a sample code for the fragment sender.",
                epilog="")
        p.add_argument("server_address", metavar="SERVER",
                       help="specify the ip address of the server.")
        p.add_argument("server_port", metavar="PORT", type=int,
                       help="specify the port number in the server.")
        p.add_argument("-I", action="store", dest="msg_file", default="-",
                       help="specify the file name containing the message, default is stdin.")
        p.add_argument("--read-each-line", action="store_true", dest="read_each_line",
                       help="enable to read each line, not a whole message at once.")
        p.add_argument("--interval", action="store", dest="interval", type=int,
                       default=1, help="specify the interval for each sending.")
        p.add_argument("--timeout", action="store", dest="timeout",
                       type=int, default=DEFAULT_TIMER_T2,
                       help="specify the number of time to wait for ACK.")
        p.add_argument("--l2-size", action="store", dest="l2_size", type=int,
                       default=DEFAULT_L2_SIZE,
                       help="specify the payload size of L2. default is %d." %
                       DEFAULT_L2_SIZE)
        '''
        p.add_argument("--rid", action="store", dest="rule_id", type=int,
                       default=DEFAULT_FRAGMENT_RID,
                       help="specify the rule id.  default is %d" %
                       DEFAULT_FRAGMENT_RID)
        '''
        p.add_argument("--context-file", action="store", dest="context_file",
                       required=True,
                       help="specify the file name containing a context.")
        p.add_argument("--rule-file", action="store", dest="rule_file",
                       required=True,
                       help="specify the file name containing a rule.")
        p.add_argument("--dtag", action="store", dest="_dtag",
                       help="specify the DTag.  default is random.")
        p.add_argument("--loss-list", action="store", dest="loss_list", default=None,
                       help="specify the index numbers to be lost for test. e.g.  --loss-list=3,8 means the 3rd and 8th packets are going to be lost.")
        p.add_argument("--loss-rate", action="store", dest="loss_rate",
                       type=float, default=None,
                       help="specify the rate of the packet loss. e.g.  --loss-rate=0.2 means 20%% to be dropped.")
        p.add_argument("--loss-random", action="store_true", dest="loss_random",
                       help="enable to lose a fragment randomly for test.")
        p.add_argument("-d", action="append_const", dest="_f_debug", default=[],
                       const=1, help="increase debug mode.")
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
        # set loss options if needed.
        #
        if not test_1in3([args.loss_list != None, args.loss_rate != None,
                          args.loss_random]):
            print("ERROR: you can specify only one of the options of loss.")
            exit(1)
        if args.loss_list != None:
            args.func_packet_loss = func_loss_list
            # set loss list, overwritten.
            args.loss_list = [int(i) for i in args.loss_list.split(",")]
        elif args.loss_rate != None:
            args.func_packet_loss = func_loss_rate
        elif args.loss_random:
            args.func_packet_loss = func_loss_random
        else:
            args.func_packet_loss = None
        #
        # fix DTag
        if args._dtag == None:
            args.dtag = None
        else:
            try:
                args.dtag = int(args._dtag)
            except ValueError:
                print("ERROR: dtag must be a number if you specify it.")
                exit(1)

        return args

'''
main code
'''

if MICROPYTHON:
    display_mem_available('starting main')

if not MICROPYTHON:
    opt = parse_args()
else:
    class opt:          # TODO: read from a configuration file
        msg_file        = "test/message.txt"
        server_address  = 11111
        server_port     = 9999
        read_each_line  = True
        interval        = 10
        timeout         = DEFAULT_TIMER_T2
        l2_size         = 6
        context_file    = "example-rule/context-001.json"
        rule_file       = "example-rule/fragment-rule-002.json"
        dtag            = 3
        debug_level     = 2
debug_set_level(opt.debug_level)

frdb = schc_fragment_ruledb()
cid = frdb.load_context_json_file(opt.context_file)
rid = frdb.load_json_file(cid, opt.rule_file)
frr = frdb.get_runtime_rule(cid, rid)

server = (opt.server_address, opt.server_port)
debug_print(1, "server:", server)


if not MICROPYTHON:
    print("Running on computer, transport method is UDP/IP")
    s = socket.socket(AF_INET, SOCK_DGRAM)
    #s.setblocking(True)
    s.settimeout(opt.timeout)
else:
    print("Running on embedded target, transport method is LoRaWAN")
    from network import LoRa
#   lora = LoRa(mode=LoRa.LORAWAN)
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915)
    from binascii import unhexlify
    dev_eui = unhexlify('7A AB 77 D0 31 21 08 E0'.replace(' ',''))
    app_eui = unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
    app_key = unhexlify('11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11'.replace(' ',''))
    import pycom
    pycom.heartbeat(False)
    mac = lora.mac()
    print ('MAC:', end='')
    print(hex(mac[0]), end='-')
    print(hex(mac[1]), end='-')
    print(hex(mac[2]), end='-')
    print(hex(mac[3]), end='-')
    print(hex(mac[4]), end='-')
    print(hex(mac[5]), end='-')
    print(hex(mac[6]), end='-')
    print(hex(mac[7]))

    # join a network using OTAA (Over the Air Activation)
    #lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), dr=2, timeout=0)
    lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)
    # wait until the module has joined the network
    print('Attempting to join .',end='')
    time.sleep(8)
    while not lora.has_joined():
        time.sleep(5)
        print('.',end='')
    print('Joined = ',lora.has_joined())
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.bind(0x02);
    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 4)
    s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)
    print("after setsockopt")
    # make the socket blocking
    s.setblocking(True)
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.send(bytes([0x01, 0x02, 0x03]))

# create a message buffer
if not MICROPYTHON and opt.msg_file == "-": # no standard inpu ton eembedded dev
    stream = sys.stdin
else:
    stream = open(opt.msg_file)

with stream as fp:
    if opt.read_each_line:
        for line in fp:
            print("sending ",line)
            schc_sender(line)
    else:
        schc_sender("".join(fp.readlines()))
