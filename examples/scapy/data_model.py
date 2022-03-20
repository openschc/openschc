import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *
import scapy.contrib.coap as scapy_coap


import gen_rulemanager as RM
#import compr_parser as parser
from compr_core import *
from protocol import SCHCProtocol

from scapy_connection import *

from gen_utils import dprint, sanitize_value


import sched

import protocol

import pprint
import binascii

import socket
import ipaddress

import time, datetime

from yangson import DataModel


class debug_protocol:
    def _log(*arg):
        print (arg)

#parse = parser.Parser(debug_protocol)
rm    = RM.RuleManager()
rm.Add(file="ipv6.json")
rm.Print()

rm.add_sid_file("ietf-schc@2022-02-15.sid")
yr = rm.to_yang()
pprint.pprint (yr)

ycbor = rm.to_yang_coreconf()
print (binascii.hexlify(ycbor))

# dm = DataModel.from_file("description.json")

# print (dm.ascii_tree())

# inst = dm.from_raw(yr)
# print ("validation", inst.validate())
# print(dm.ascii_tree(no_types=True, val_count=True), end='')
