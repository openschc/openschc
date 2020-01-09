#!/usr/bin/env python

import argparse
import sched
import sys
import select
import socket
import os

# --------------------------------------------------

sys.path.extend(["../../src"]) # XXX: temporary

import gen_rulemanager
import protocol

# --------------------------------------------------

MAX_PACKET_SIZE = 1024*1024

# --------------------------------------------------

def address_to_string(address):
    host,port = address
    return "{}|{}".format(host, port)

def string_to_address(string_address):
    str_host, str_port = string_address.split("|")
    return (str_host, int(str_port))

# --------------------------------------------------

class UdpUpperLayer:
    def __init__(self):
        self.protocol = None

    # ----- AbstractUpperLayer interface (see: architecture.py)
    
    def _set_protocol(self, protocol):
        self.protocol = protocol

    def recv_packet(self, address, raw_packet):
        raise NotImplementedError("XXX:to be implemented")

    # ----- end AbstractUpperLayer interface

    def send_later(self, delay, udp_dst, packet):
        assert self.protocol is not None
        scheduler = self.protocol.get_system().get_scheduler()
        scheduler.add_event(delay, self._send_now, (udp_dst, packet))

    def _send_now(self, udp_dst, packet):
        dst_address = address_to_string(udp_dst)
        self.protocol.schc_send(dst_address, packet)

# --------------------------------------------------        

class UdpLowerLayer:
    def __init__(self, udp_src, udp_dst):
        self.protocol = None
        self.sd = None
        self.udp_src = udp_src
        self.udp_dst = udp_dst

    # ----- AbstractLowerLayer interface (see: architecture.py)
        
    def _set_protocol(self, protocol):
        self.protocol = protocol
        self._actual_init()

    def send_packet(self, packet, dst_str_address, transmit_callback):
        if dst_str_address is None or dst_str_address == "*":
            dst_address = self.udp_dst
        else:
            dst_address = string_to_address(dst_str_address)
        self.sd.sendto(packet, dst_address)            
        if transmit_callback is not None:
            transmit_callback(1)

    def get_mtu_size(self):
        return 72 # XXX

    def get_address(self):
        return address_to_string(self.udp_src)

    # ----- end AbstractLowerLayer interface

    def _actual_init(self):
        self.sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sd.bind(self.udp_src)
        scheduler = self.protocol.get_system().get_scheduler()
        scheduler.add_fd_callback(self.sd.fileno(),
                                  self.event_packet_received, ())

    def event_packet_received(self):
        """Called but the SelectScheduler when an UDP packet is received"""
        packet, address = self.sd.recvfrom(MAX_PACKET_SIZE)
        sender_address = address_to_string(address)
        self.protocol.schc_recv(sender_address, packet)

# --------------------------------------------------

class SelectScheduler:
    def __init__(self):
        self.fd_callback_table = {}
        self.sched = sched.scheduler(delayfunc=self._sleep)

    # ----- AbstractScheduler Interface (see: architecture.py)
         
    def add_event(self, rel_time, callback, args):
        event = self.sched.enter(rel_time, None, callback, args)
        return event

    def cancel_event(self, event):
        return self.sched.cancel(event)

    # ----- Additional methods

    def _sleep(self, delay):
        """Implements a delayfunc for sched.scheduler

        This delayfunc sleeps for `delay` seconds at most (in real-time,
        but if any event appears in the fd_table (e.g. packet arrival),
        the associated callbacks are called and the wait is stop.
        """
        self.wait_one_callback_until(delay)


    def wait_one_callback_until(self, max_delay):
        """Wait at most `max_delay` second, for available input (e.g. packet).

        If so, all associated callbacks are run until there is no input.
        """
        fd_list = list(sorted(self.fd_callback_table.keys()))
        while True:
            rlist, unused, unused = select.select(fd_list, [], [], max_delay)
            if len(rlist) == 0:
                break
            for fd in rlist:
                callback, args = self.fd_callback_table[fd]
                callback(*args)
            # note that sched impl. allows to return before sleeping `delay`

    def add_fd_callback(self, fd, callback, args):
        assert fd not in self.fd_callback_table
        self.fd_callback_table[fd] = (callback, args)

    def run(self):
        long_time = 3600
        while True:
            self.sched.run() # when this returns, there is no event left ...
            self.wait_one_callback_until(long_time) # hence we wait for input

# --------------------------------------------------        

class UdpSystem:
    def __init__(self):
        self.scheduler = SelectScheduler()

    def get_scheduler(self):
        return self.scheduler

    def log(self, name, message):
        print(name, message)

# --------------------------------------------------
