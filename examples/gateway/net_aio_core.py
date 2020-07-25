import requests
import asyncio

from gen_base_import import *  # used for now for differing modules in py/upy
from compr_parser import Parser
from gen_utils import dprint, sanitize_value

# --------------------------------------------------

def lookup_route(dst_ipaddr, config):
    """
    tricky. the IP address in the config is hex string.
    the IP address in bytes has been added by config_update().
    """
    for l3a_raw,info in config.route.items():
        if l3a_raw == dst_ipaddr:
            return info
    else:
        return None

def lookup_interface(ifname, config):
    for config_ifname,info in config.interface.items():
        if ifname == config_ifname:
            return info
    else:
        return None

# --------------------------------------------------

class AioUpperLayer:

    def __init__(self, system, config=None):
        self.system = system
        self.config = config

    def _set_protocol(self, protocol):
        self.protocol = protocol

    async def async_pcap_send(self, data):
        self.system.scheduler.loop.run_in_executor(
                None, self.pcap.sendpacket, data)

    def recv_packet(self, dev_L2addr, raw_packet):
        self.system.log("L3: recv packet Devaddr={} Packet={}".format(
                dev_L2addr, raw_packet.get_content().hex()))
        route_info = lookup_route(raw_packet[24:40])
        l2_info = lookup_l2info(route_info["ifname"])
        asyncio.ensure_future(self.async_pcap_send(l2_info["pcap"],
                route_info["dst_raw"] + l2_info["addr_raw"] + l2_info["type"] + 
                raw_packet.get_content()))

# --------------------------------------------------        

class AioLowerLayer():

    def __init__(self, system, config=None):
        self.system = system
        self.config = config

    def _set_protocol(self, protocol):
        self.protocol = protocol

    def send_packet(self, data, dev_L2addr=None, callback=None,
                    callback_args=tuple()):
        self.system.log("L2", "send data for {}".format(dev_L2addr))
        if self.config.enable_sim_lpwa is True:
            body = json.dumps({"hexSCHCData": data.hex(),
                               "devL2Addr": dev_L2addr})
        else:
            body = data
        self.system.scheduler.loop.run_in_executor(
                None, self._post_data, self.config.downlink_url, body,
                self.config.ssl_verify)
        status = 0
        #
        if callback is not None:
            # XXX status should be taken from the run_in_executor().
            args = callback_args + (status,)
            callback(*args)

    def get_mtu_size(self):
        # XXX how to know the MTU of the LPWA link beyond the NS.
        return 56

    def get_address(self):
        return b"<L2 addr>"

    def _post_data(self, url, data, verify):
        headers = {"content-type": "text/json"}
        requests.post(url, headers=headers, data=data, verify=verify)

# --------------------------------------------------

#class Scheduler(SimulScheduler):
# net_aio_sched.py
class AioScheduler():

    def __init__(self, loop):
        self.loop = loop
        #super().__init__()

    def get_clock(self):
        return self.loop.time()

    def add_event(self, time_in_sec, event_function, event_args):
        dprint(f"Add event {time_in_sec} {event_args}")
        dprint(f"callback set -> {event_function.__name__}")
        assert time_in_sec >= 0
        evnet_id = self.loop.call_later(time_in_sec, event_function,
                                        *event_args)
        return evnet_id

    def cancel_event(self, event_handle):
        event_handle.cancel()

# --------------------------------------------------        

class AioSystem:
    """
    self.get_scheduler(): provide the handler of the scheduler.
    self.log(): show the messages.  It is called by all modules.
    """
    def __init__(self, logger=None, config=None):
        loop = asyncio.get_event_loop()
        if config.debug_level > 1:
            loop.set_debug(True)
        self.scheduler = AioScheduler(loop)
        self.config = config
        if logger is None:
            self.logger = logging.getLogger(PROG_NAME)
        else:
            self.logger = logger

    def get_scheduler(self):
        return self.scheduler

    def log(self, name, message):
        # XXX should set a logging level.
        self.logger.debug(f"{name} {message}")

