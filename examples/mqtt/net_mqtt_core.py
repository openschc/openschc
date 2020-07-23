#!/usr/bin/env python
# coding: utf-8

import argparse
import sched
import sys
import select
import socket
import os

import base64
import paho.mqtt.client as mqtt
import queue

from pprint import pformat
from scapy.all import *
import binascii

# --------------------------------------------------

sys.path.extend(["../../src"])  # XXX: temporary

import gen_rulemanager
import protocol

# --------------------------------------------------
def address_to_string(address):
    host, port = address
    return "{}|{}".format(host, port)


def string_to_address(string_address):
    str_host, str_port = string_address.split("|")
    return (str_host, int(str_port))


class UdpUpperLayer:
    def __init__(self):
        self.protocol = None

    # ----- AbstractUpperLayer interface (see: architecture.py)

    def _set_protocol(self, protocol):
        self.protocol = protocol

    def recv_packet(self, address, raw_packet):
        print(f"recv_packet. address: {address} - raw: {pformat(raw_packet)}")
        # IPv6 creation
        ip_header = IPv6(version=6)
        ipv6_dest = (
            raw_packet[("IPV6.APP_PREFIX", 1)][0] + raw_packet[("IPV6.APP_IID", 1)][0]
        ).hex()
        ipv6_dest = [(ipv6_dest[i : i + 4]) for i in range(0, len(ipv6_dest), 4)]
        ipv6_dest = ":".join(ipv6_dest)
        ip_header.src = ipv6_dest
        ipv6_src = (
            raw_packet[("IPV6.DEV_PREFIX", 1)][0] + raw_packet[("IPV6.DEV_IID", 1)][0]
        ).hex()
        ipv6_src = [(ipv6_src[i : i + 4]) for i in range(0, len(ipv6_src), 4)]
        ipv6_src = ":".join(ipv6_src)
        ip_header.dst = ipv6_src
        ip_header.fl = raw_packet[("IPV6.FL", 1)][0]
        ip_header.hlim = raw_packet[("IPV6.HOP_LMT", 1)][0]
        ip_header.tc = raw_packet[("IPV6.TC", 1)][0]

        # UDP Creation
        udp_header = UDP()
        udp_header.sport = raw_packet[("UDP.DEV_PORT", 1)][0]
        udp_header.dport = raw_packet[("UDP.APP_PORT", 1)][0]

        # Payload
        data = Raw(load=raw_packet[("PAYLOAD", 1)])
        packet = ip_header / udp_header / data
        print(pformat(packet.show()))
        print("IPv6 packet:\n", hexdump(packet, True), sep="")

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


class MqttLowerLayer:
    def __init__(self, device_id, lns):
        self.protocol = None
        self.sd = None
        self.lns = lns
        self.device_id = device_id
        self.port = 10

    # ----- AbstractLowerLayer interface (see: architecture.py)

    def _set_protocol(self, protocol):
        self.protocol = protocol
        self._actual_init()

    def send_packet(self, packet, dst_str_address, transmit_callback=None):
        # mqtt_send()
        print("Send packet to device", packet, dst_str_address)
        if transmit_callback is not None:
            transmit_callback(1)

    def get_mtu_size(self):
        return 51  # TBC

    def get_address(self):
        return self.device_id

    # ----- end AbstractLowerLayer interface

    def _actual_init(self):
        # MQTT init
        scheduler = self.protocol.get_system().get_scheduler()
        self.queue = queue.Queue(maxsize=0)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(
            self.lns.mqtt_username, self.lns.mqtt_password
        )
        if self.lns.mqtt_secured == True:
            self.mqtt_client.tls_set()
        self.mqtt_client.user_data_set(
            {"queue": self.queue, "device_id": self.device_id, "port": self.port, "lns": self.lns}
        )
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        self.mqtt_client.on_message = self.on_mqtt_uplink
        print("Connect to MQTT")
        self.mqtt_client.connect(self.lns.mqtt_url, self.lns.mqtt_port, 60)
        self.mqtt_client.loop_start()
        scheduler.configure(self.event_packet_received, self.queue)

    @staticmethod
    def on_mqtt_connect(client, context, flags, rc):
        print("Connected with result code " + str(rc))
        if rc == 0:
            print("Subscribed to", context["device_id"])
            client.subscribe(context["lns"]["mqtt_topic_uplink"])

    def on_mqtt_disconnect(self):
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()

    @staticmethod
    def on_mqtt_uplink(client, context, msg):
        context["lns"].get_payload(context["queue"], msg.payload, context["port"])

    def event_packet_received(self, packet):
        """Called by the SelectScheduler when an MQTT packet is received"""
        self.protocol.schc_recv(self.device_id, packet)


# --------------------------------------------------


class SelectSchedulerMqtt:
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
        try:
            payload = self.queue.get(block=True, timeout=max_delay)
            self.rx_callback(payload)
        except queue.Empty:
            # Delay over, return
            pass

    def configure(self, rx_callback, queue):
        self.rx_callback = rx_callback
        self.queue = queue

    def run(self):
        long_time = 3600
        while True:
            self.sched.run()  # when this returns, there is no event left ...
            self.wait_one_callback_until(long_time)  # hence we wait for input


# --------------------------------------------------


class MqttSystem:
    def __init__(self):
        self.scheduler = SelectSchedulerMqtt()

    def get_scheduler(self):
        return self.scheduler

    def log(self, name, message):
        print(name, message)


# --------------------------------------------------
