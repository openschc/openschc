#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

try:
    from pypacket_dissector import encoder as en
except:
    import encoder as en

def parse_args():
    p = argparse.ArgumentParser(description="a packet encoder.", epilog="")
    p.add_argument("infile", metavar="INFILE", nargs="?", type=str,
                   default="-",
                   help='''specify a filename containing json.
                   default is stdin.''')
    p.add_argument("-v", action="store_true", dest="f_verbose",
                   help="enable verbose mode.")
    p.add_argument("-d", action="store_true", dest="f_debug",
                   help="enable debug mode.")

    args = p.parse_args()
    return args

opt = parse_args()
if opt.infile == "-":
    jo = sys.stdin.read()
else:
    jo = open(opt.infile, "r").read()
#
jd = en.load_json_packet(jo)
ret = en.encoder(jd)
sys.stdout.buffer.write(ret)

