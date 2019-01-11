#! /usr/bin/env python3
#---------------------------------------------------------------------------

import logging
import threading
import argparse

import json
import base64, binascii
import struct

import select
import socket
import time
import sched

import warnings
import requests

import bottle # pip install bottle || wget https://bottlepy.org/bottle.py
from bottle import post, request, response

try:
    import tornado.ioloop
    import tornado.web
    with_tornado = True
except:
    print("cannot import tornado")
    with_tornado = False

import sys
sys.path.append("../../PLIDO-tanupoo")
import fragment

from fraglogic import WindowAckModeSender

#---------------------------------------------------------------------------

def bytes_to_hex(data, with_new_line=False, with_repr=True):
    result = ""
    for i,b in enumerate(bytearray(data)):
        if i == 0:
            pass
        elif i%16 == 0:
            if with_new_line:
                result += "\n"
            else: result += " "
        else: result += " "
        result += "%02x" % b
    if with_repr:
        result += " "+repr(data)
    return result

#---------------------------------------------------------------------------

class FragmentationManager:
    """The fragmentation manager handles the logic of the fragment sending etc.
    """
    
    def __init__(self):
        self.nb_bit_bitmap = 1
        self.max_fcn_per_window = self.nb_bit_bitmap - 1 # included
        
        self.window = 0
        self.fcn = self.max_fcn_per_window # protocol FCN
        self.fragment_index = 0 #
        self.content = None
        self.state = "init"

    def event_packet(self, raw_packet):
        if self.state == "init":
            print("(ignored) Dev. packet:", repr(raw_packet))
            self.state = "fragment"
            self.content = ["to be", "or not to", " be, that's", "the question"]
            return self.get_current_fragment()
        elif self.state == "fragment":
            return self.process_ack(raw_packet)
        else: raise ValueError("bad state", self.state)

    def get_current_fragment(self):
        print("fragment window={} fcn={} current_frag_index={}".format(
            self.window, self.fcn, self.fragment_index))
        header = struct.pack(b"!BB", self.window, self.fcn)
        return header + bytes(self.content[self.fragment_index].encode("ascii"))

    def process_ack(self, raw_packet):
        print("process_ack", bytes_to_hex(raw_packet))
        if len(raw_packet) != struct.calcsize("!BB"):
            print("XXX: bad ack size", len(raw_packet))
            return b"XXX:bad"
        window, bitmap = struct.unpack("!BB", raw_packet)
        print("window={}, bitmap={}".format(window, bitmap))
        if window != self.window:
            print("warning: bad window number", window, self.window)
            return b"XXX:bad-window"
        if bitmap != 1: #XXX
            print("warning: incomplete bitmap", bitmap, 1)
            return b"XXX:bad-bitmap"

        # Next fragment
        self.window = (self.window+1) % 2 # protocol
        # - because it will be the first of the new window:
        self.fcn = self.max_fcn_per_window 
        self.fragment_index += 1 # internal data structure

        if self.fragment_index == len(self.content):
            print("Finished trasnmission of fragments")
            return b""

        if self.fragment_index == len(self.content)-1:
            # protocol - because it is the end of the content in this case:
            self.fcn = 1 
            return self.get_current_fragment() # XXX + "MIC"
        else:
            return self.get_current_fragment()

#---------------------------------------------------------------------------

# FRAGMENT_FORMAT = {
#     # 0|0|12345678|12345678
#     "hdr_size": 16,
#     "rid_size": 0,
#     "rid_shift": 0,
#     "rid_mask": 0x0000,
#     "dtag_size": 0,
#     "dtag_shift": 0,
#     "dtag_mask": 0x0000,
#     "win_size": 1,
#     "win_shift": 8,
#     "win_mask": 0x0100,
#     "fcn_size": 1,
#     "fcn_shift": 0,
#     "fcn_mask": 0x01,
#     }

FRAGMENT_FORMAT = fragment.fp_ietf100_win

class SystemManager:
    def add_event(self, rel_time, callback, args):
        XXX

    def send_packet(self, packet):
        XXX

# {'srcbuf': b'The crow has flown away:\nswaying in the evening sun,\naleafless tree.', 'max_fcn': 255, 'win_size': 255, 'win_mask': 57896044618658097711785492504343953926634992332820282019728792003956564819967, 'fcn': 255, 'end_of_fragment': 255, 'base_hdr': 256}



class SimulSystemManager:
    def __init__(self):
        self.scheduler = sched.scheduler(self.get_clock, self.wait_delay)
        self.clock = 0
        self.receive_packet_callback = None
        self.inject_receive_list = []
        
    # sched.scheduler API
        
    def get_clock(self):
        return self.clock

    def wait_delay(self, delay):
        self.clock += delay

    def run(self):
        self.scheduler.run()

    # external API
        
    def add_event(self, rel_time, callback, args):
        self.scheduler.enter(rel_time, 0, callback, args)

    def send_packet(self, packet):
        #print("SEND:", bytes_to_hex(packet))
        print("SEND", packet)
        if len(self.inject_receive_list) > 0:
            inject_packet = self.inject_receive_list.pop(0)
            if self.receive_packet_callback != None:
                print("injected packet:", inject_packet)
                self.add_event(0, self.receive_packet_callback,
                               (inject_packet,))

    def set_receive_packet_callback(self, callback):
        self.receive_packet_callback = callback

    def set_inject_receive_list(self, packet_list):
        self.inject_receive_list = packet_list[:]
        
            
class RealTimeSystemManager:
    """
    Manage event queue in real time
    Send and receive packet from an UDP port
    """
    def __init__(self, dest_address_and_port, listen_port=None, time_scale=1):
        self.time_t0 = time.time()
        self.time_scale = time_scale
        self.receive_packet_callback = None
        self.scheduler = sched.scheduler(self.get_clock, self.wait_delay)
        self.destination = dest_address_and_port
        
        self.sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if listen_port == None:
            unused, listen_port = dest_address_and_port
        print("UDP listening on port {}".format(listen_port))
        self.sd.bind(("", listen_port))
        
        self.add_event(1e8, "should not be called", ())
        self.inject_receive_done = False
        self.inject_receive_list = []

    def set_inject_receive_list(self, packet_list):
        self.inject_receive_list = packet_list[:]

    def set_receive_packet_callback(self, callback):
        self.receive_packet_callback = callback
        
    def get_clock(self):
        return self.time_t0 + (time.time()-self.time_t0) * self.time_scale

    def wait_delay(self, delay):
        #delay *= self.time_scale
        # Note: we might wait for less time than expected if packet received
        if len(self.inject_receive_list) > 0 and not self.inject_receive_done:
            inject_packet = self.inject_receive_list.pop(0)
            self.inject_receive_done = True
            if inject_packet != None and self.receive_packet_callback != None:
                print("injected packet:", inject_packet)
                self.receive_packet_callback(inject_packet)
                return

        read_list,unused,unused = select.select([self.sd],[],[], delay)
        self.inject_receive_done = False
        if len(read_list) > 0:
            assert read_list[0] is self.sd
            port = self.destination[1]
            packet, address_and_port = self.sd.recvfrom(2**16)
            if self.receive_packet_callback != None:
                self.receive_packet_callback(packet)

    def run(self):
        self.scheduler.run()
        
    def add_event(self, rel_time, callback, args):
        self.scheduler.enter(rel_time, 0, callback, args)

    def send_packet(self, packet):
        #print("SEND:", bytes_to_hex(packet))
        print("SEND", packet)
        self.sd.sendto(packet, self.destination)


def test_real_time_system_manager(args):
    system = RealTimeSystemManager((args.address, args.port), args.listen_port)
    start_time = time.time()
    def periodic_display_function():
        elapsed_time = system.get_clock()-start_time
        print("current time={} - display".format(elapsed_time))
        system.add_event(1.5, periodic_display_function, ())
    def periodic_send_function():
        elapsed_time = system.get_clock()-start_time
        print("current time={} - send".format(elapsed_time))
        system.send_packet("<packet from {}>".format(elapsed_time))
        system.add_event(2, periodic_send_function, ())
    system.add_event(0, periodic_display_function, ())
    system.add_event(0, periodic_send_function, ())    
    system.run()

        
def test_window_ack_manager_internal():
    reply_list = [b"\x00", b"\x01"]
        
    simul_system_manager = SimulSystemManager()
    packet = b"The crow has flown away:\nswaying in the evening sun,\naleafless tree."
    window_ack_manager = WindowAckModeSender(
        simul_system_manager, FRAGMENT_FORMAT, #fragment.fp,
        full_packet=packet, rule_id=0, dtag=0, window_size=7, fragment_size=4)

    def send_callback():
        #global window_ack_manager, simul_system_manager
        if len(reply_list) > 0:
            print("REPLY")
            reply_packet = reply_list.pop(0)
            simul_system_manager.add_event(1, window_ack_manager.event_packet, (reply_packet,))
    simul_system_manager.send_callback = send_callback # XXX
    
    simul_system_manager.add_event(0, window_ack_manager.start, ())
    simul_system_manager.run()

def really_test_window_ack_manager(args, system):
    packet = ( b"The crow has flown away: "
              +b"- swaying in the evening sun, "
              +b"- a leafless tree.")
    window_ack_manager = WindowAckModeSender(
        system, FRAGMENT_FORMAT, #fragment.fp,
        full_packet=packet,
        rule_id=0, dtag=0,
        window_max_size=4, fragment_size=4)
    system.set_receive_packet_callback(window_ack_manager.event_packet)
    if args.inject:
        inject_receive_list = ([None]*12 + [b"\x00\xfe"] + [None]*20
                               + [b"\x01\xfe"])
        system.set_inject_receive_list(inject_receive_list)
    system.add_event(0, window_ack_manager.start, ())
    system.run()

    
def test_window_ack_manager(args):
    system = RealTimeSystemManager((args.address, args.port),
                                   args.listen_port, args.time_scale)
    really_test_window_ack_manager(args, system)

def test_window_ack_manager_simul(args):
    system = SimulSystemManager()    
    really_test_window_ack_manager(args, system)

    
#---------------------------------------------------------------------------
# POST packet processing

def process_packet(frag_manager, json_request):
    '''
    Processes one packet, in base64 in json_request["data"]
    Returns the packet that should be sent back as a json structure, with 
    at least {"data": <base 64 of packet>, ""}
    '''
    post_request = json.loads(json_request)

    if "data" in post_request:
        raw_packet = binascii.a2b_base64(post_request["data"])
        print(">>>PACKET:", bytes_to_hex(raw_packet))
        raw_reply_packet = frag_manager.event_packet(raw_packet)
    else:
        # This is a join
        print(">>>>JOIN")
        raw_reply_packet = b""

    print("<<<REPLY:", bytes_to_hex(raw_reply_packet))

    json_response = {
        "fport": 2,
        "data": binascii.b2a_base64(raw_reply_packet).decode("ascii")
    }
    return json_response

#---------------------------------------------------------------------------
# Bottle version
# -> bottle is simpler (one file), problem is for scheduling timers
# threading is probably needed

@post('/')
def device_packet_handler():
    global frag_manager
    print("--- received data")
    # https://stackoverflow.com/questions/14988887/reading-post-body-with-bottle-py
    response.set_header('Content-Type', 'application/json')
    raw_request = request.body.read()
    json_response = process_packet(frag_manager, raw_request)
    raw_response = json.dumps(json_response)
    return raw_response

#bottle.run(host='localhost', port=3112, debug=True)

#---------------------------------------------------------------------------
# Tornado version

# https://gist.github.com/cjgiridhar/3274687
def run_tornado(args):
    global frag_manager
    version = "magicarpe" if args.bis else "green"
    frag_manager = FragmentationManager(version)
    
    class Alive(tornado.web.RequestHandler):
        def get(self):
            self.write("server is alive")
    
    class PostHandler(tornado.web.RequestHandler):
        def post(self):
            raw_request = self.request.body
            json_request = raw_request.decode("ascii")
            json_response = process_packet(frag_manager, json_request)
            raw_response = json.dumps(json_response)
            self.write(raw_response)
    
    application = tornado.web.Application([
        (r"/alive", Alive),
        (r"/", PostHandler)
    ])

    application.listen(args.port, address=args.address)
    tornado.ioloop.IOLoop.instance().start()

#---------------------------------------------------------------------------

def cmd_run_server(args):
    global frag_manager
    version = "magicarpe" if args.bis else "green"
    if not args.tornado:
        frag_manager = FragmentationManager(version)        
        bottle.run(host=args.address, port=args.port, debug=args.debug)
    else:
        run_tornado(args)

#---------------------------------------------------------------------------

def cmd_post(args):
    # http://docs.python-requests.org/en/master/user/quickstart/#make-a-request
    raw_packet = b"hello-from-python"
    packet_b64 = binascii.b2a_base64(raw_packet).decode("ascii")
    s = json.dumps({"data":packet_b64, "fport":2})
    r = requests.post("http://{}:{}".format(args.address, args.port), data = s)
    print(r.text)

#---------------------------------------------------------------------------

def cmd_simple(args):
    # http://docs.python-requests.org/en/master/user/quickstart/#make-a-request
    if args.step == 0:   raw_packet = b"\x00\x00"
    elif args.step == 1: raw_packet = b"\x00\x01"
    elif args.step == 2: raw_packet = b"\x01\x01"
    elif args.step == 3: raw_packet = b"\x00\x01"
    elif args.step == 4: raw_packet = b"\x01\x01"
    else: raise ValueError("unmanaged step", args.step)

    packet_b64 = binascii.b2a_base64(raw_packet).decode("ascii")
    s = json.dumps({"data":packet_b64, "fport":2})
    r = requests.post("http://{}:{}".format(args.address, args.port), data = s)
    json_reply = json.loads(r.text)
    if "data" in json_reply:
        packet = binascii.a2b_base64(json_reply["data"]).decode("ascii")
        packet
    else: print("reply:", r.text)

#---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

parser_server = subparsers.add_parser("server", help="run as POST server")
parser_server.add_argument("--address", default="0.0.0.0")
parser_server.add_argument("--port", default=3112)
parser_server.add_argument("--debug", default=False, action="store_true")
parser_server.add_argument("--bis", default=False, action="store_true")
parser_server.add_argument("--tornado", default=False, action="store_true")

parser_post = subparsers.add_parser("post", help="post a message")
parser_post.add_argument("--port", default=3112)
parser_post.add_argument("--address", default="localhost") 

parser_simple = subparsers.add_parser(
    "simple", help="send one step of simple fragmentation")
parser_simple.add_argument("--port", default=3112)
parser_simple.add_argument("--step", type=int, default=0)
parser_simple.add_argument("--address", default="localhost") 

parser_test_window_ack = subparsers.add_parser(
    "simul-win-ack", help="test window ack manager")
parser_test_window_ack.add_argument(
    "--inject", default=False, action="store_true")

parser_test_emul = subparsers.add_parser("test-emul")
parser_test_emul.add_argument("--address", default="localhost")
parser_test_emul.add_argument("--port", type=int, default=9999,
                              help="destination port")
parser_test_emul.add_argument("--listen-port", type=int, default=9999)

parser_test_udp_window_ack = subparsers.add_parser(
    "udp-win-ack", help="test window ack manager")
parser_test_udp_window_ack.add_argument("--address", default="localhost")
parser_test_udp_window_ack.add_argument(
    "--port", type=int, default=9999, help="destination port")
parser_test_udp_window_ack.add_argument("--data", type=int, default=9999)
parser_test_udp_window_ack.add_argument("--listen-port", type=int, default=9999)
parser_test_udp_window_ack.add_argument(
    "--inject", default=False, action="store_true")
parser_test_udp_window_ack.add_argument(
    "--time-scale", default=1, type=float) # not working

args = parser.parse_args()

if args.command == "server":
    cmd_run_server(args)
elif args.command == "post":
    cmd_post(args)
elif args.command == "simple":
    cmd_simple(args)
elif args.command == "simul-win-ack":
    test_window_ack_manager_simul(args)
elif args.command == "udp-win-ack":
    test_window_ack_manager(args)    
elif args.command == "test-emul":
    test_real_time_system_manager(args)
else: raise ValueError("bad command name", args.command)
    
#---------------------------------------------------------------------------
