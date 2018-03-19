#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import sys
import argparse

try:
    from pypacket_dissector import dissector as dis
except:
    import dissector as dis

def read_file(filename, verbose=False, debug=False):
    with open(filename) as f:
        data = f.buffer.read()
    #
    if verbose:
        print(dis.dissector.dump_byte(data))
    #
    ret3 = dis.dissector(data)
    print(dis.dump_pretty(ret3))

def read_stdin(filename, verbose=False, debug=False):
    sep = [ bytes([i]) for i in b"\x00\x01\x02SEP\xff" ]
    sep_end = sep[-1]
    sep_len = len(sep)
    while True:
        mark = 0
        data = bytearray()
        while True:
            b = sys.stdin.buffer.read(1)
            if sep[mark] == b:
                if b == sep_end:
                    data = data[:-sep_len]
                    break
                else:
                    mark += 1
                    data += b
                continue
            #
            mark = 0
            data += b
        #
        if verbose:
            print(dis.dump_byte(data))
        ret = dis.dissector(data)
        print(dis.dump_pretty(ret))

def parse_args():
    p = argparse.ArgumentParser(description="a packet dissector."
                                epilog="")
    p.add_argument("target", metavar="TARGET", type=str,
                   help="""specify a filename containing
                   packet data.  '-' allows the stdin as the input.""")
    p.add_argument("-v", action="store_true", dest="f_verbose",
                   help="enable verbose mode.")
    p.add_argument("-d", action="store_true", dest="f_debug",
                   help="enable debug mode.")

    args = p.parse_args()
    return args

'''
main
'''
opt = parse_args()

if opt.target == "-":
    read_stdin(opt.target, verbose=opt.f_verbose, debug=opt.f_debug)
else:
    read_file(opt.target, verbose=opt.f_verbose, debug=opt.f_debug)
