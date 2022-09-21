import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *

import gen_rulemanager as RM
from protocol import SCHCProtocol
from scapy_connection import *
from gen_utils import dprint, sanitize_value
from gen_bitarray import *
from compr_parser import Unparser

import pprint
import binascii
import socket
import ipaddress


# Create a Rule Manager and upload the rules.
rm = RM.RuleManager()
rm.Add(file="lorawan.json")
rm.Print()