import asyncio
import aiohttp

from gen_base_import import *  # used for now for differing modules in py/upy
from gen_utils import dprint

# --------------------------------------------------

class AiohttpUpperLayer:

    def __init__(self, system, config=None):
        self.system = system
        self.config = config

    def lookup_route(self, dst_ipaddr):
        """
        tricky. the IP address in the config is hex string.
        the IP address in bytes has been added by config_update().
        """
        for l3a_raw,info in self.config["route"].items():
            if l3a_raw == dst_ipaddr:
                return info
        else:
            return None

    def lookup_interface(self, ifname):
        for config_ifname,info in self.config["interface"].items():
            if ifname == config_ifname:
                return info
        else:
            return None

    def _set_protocol(self, protocol):
        self.protocol = protocol

    async def async_pcap_send(self, data):
        self.system.scheduler.loop.run_in_executor(
                None, self.pcap.sendpacket, data)

    def recv_packet(self, dst_l2_addr, raw_packet):
        """Processing a packet from the SCHC layer to northbound."""
        self.system.log("L3", "recv packet from devaddr={} packet={}".format(
                dst_l2_addr, raw_packet.hex()))
        route_info = self.lookup_route(raw_packet[24:40])
        if route_info is None:
            self.system.log("L3", "no route for {}".format(
                    raw_packet[24:40].hex()))
            return
        l2_info = self.lookup_interface(route_info["ifname"])
        asyncio.ensure_future(self.async_pcap_send(l2_info["pcap"],
                route_info["dst_raw"] + l2_info["addr_raw"] + l2_info["type"] + 
                raw_packet))

    async def send_packet(self, packet):
        dst_l3_addr = packet[24:40]
        route_info = self.lookup_route(dst_l3_addr)
        if route_info is None:
            self.system.log(f"L3", "route for {dst_l3_addr} wasn't found.")
            return False
        # XXX need to check for asyncio
        self.protocol.schc_send(route_info["dst"], dst_l3_addr, packet)
        return True


# --------------------------------------------------        

class AiohttpLowerLayer():

    def __init__(self, system, config=None):
        self.system = system
        self.config = config
        self.last_clock = 0

    def _set_protocol(self, protocol):
        self.protocol = protocol

    async def recv_packet(self, data_hex, dst_l2_addr=None):
        """Processing a packet from the southbound to the SCHC layer"""
        # XXX need to check for asyncio
        self.protocol.schc_recv(dst_l2_addr, data_hex)

    def send_packet(self, data, dst_l2_addr=None, callback=None,
                    callback_args=tuple()):
        """Processing a packet from the SCHC layer to southbound"""
        dprint("L2: sending a packet", data.hex())
        self.system.log("L2", "send packet to devaddr={} packet={}".format(
                dst_l2_addr, data.hex()))
        body = json.dumps({"hexSCHCData": data.hex(),
                            "devL2Addr": dst_l2_addr})
        """
        self.system.scheduler.loop.run_in_executor(
                None, self._post_data, self.config["downlink_url"], body,
                self.config["ssl_verify"])
        """
        current_clock = self.system.scheduler.get_clock()
        diff = current_clock - self.last_clock
        if diff > self.config["tx_interval"]:
            delay = self.config["tx_interval"]
        else:
            delay = self.config["tx_interval"] - diff
        self.last_clock = current_clock
        self.system.scheduler.add_event(delay,
                                        self._post_data,
                                        (self.config["downlink_url"],
                                        body, self.config["ssl_verify"]))
        status = 0
        #
        if callback is not None:
            # XXX status should be taken from the run_in_executor().
            args = callback_args + (status,)
            callback(*args)

    def get_mtu_size(self):
        # XXX how to know the MTU of the LPWA link beyond the NS.
        return 56

    def _post_data(self, *args):
        t = asyncio.ensure_future(self._do_post_data(*args))

    async def _do_post_data(self, url, data, verify):
        #headers = {"content-type": "application/json"}
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=data, ssl=verify)

# --------------------------------------------------

#class Scheduler(SimulScheduler):
# net_aio_sched.py
class AiohttpScheduler():

    def __init__(self, loop):
        self.loop = loop
        #super().__init__()

    def get_clock(self):
        return self.loop.time()

    def add_event(self, time_in_sec, event_function, event_args):
        dprint(f"Add event: "
               f"call in {time_in_sec} sec: "
               f"{event_function.__name__} {event_args}")
        assert time_in_sec >= 0
        if event_args is None:
            evnet_id = self.loop.call_later(time_in_sec, event_function)
        else:
            evnet_id = self.loop.call_later(time_in_sec, event_function,
                                            *event_args)
        return evnet_id

    def cancel_event(self, event_handle):
        event_handle.cancel()

# --------------------------------------------------        

class AiohttpSystem:
    """
    self.get_scheduler(): provide the handler of the scheduler.
    self.log(): show the messages.  It is called by all modules.
    """
    def __init__(self, logger=None, config=None):
        loop = asyncio.get_event_loop()
        if config["debug_level"] > 1:
            loop.set_debug(True)
        self.scheduler = AiohttpScheduler(loop)
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

