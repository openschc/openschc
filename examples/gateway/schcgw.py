#!/usr/bin/env python

import argparse
import json
import requests
from aiohttp import web
import ssl
import logging
import pcap
import os
import ipaddress

from net_aio_core import *
from gen_rulemanager import *
import protocol

PROG_NAME = "GW"

config_default = {
    "debug_level": 0,
    "enable_sim_lpwa": False,
    "bind_addr": "::",
    "bind_port": 51225,
    "ifname": "eth0",
    "eth_dst": None,
    "eth_src": None,
    "downlink_url": None,
    "ssl_verify": True,
    "my_cert": None,
    "rule_file": None,
    "route": {},
    "interface": {},
    }


def find_file(file_name):

    if os.path.exists(file_name) is False:
        file_path = f'{os.environ.get("OPENSCHCDIR","..")}/{file_name}'
        if os.path.exists(file_path) is False:
            raise ValueError("No such file {}".format(file_name))
        return file_path
    else:
        return file_name


def get_value(json_body, key_list):
    """Finding a value with one of keys in json_body.
    
    It searches each key in key_list with json_body.
    It returns the first value if a key is found.
    """
    for k in key_list:
        if k in json_body:
            return json_body[k]
    else:
        logger.debug("no data for {}".format(key_list))
        return None

async def app_downlink(request):
    """ downlink """
    packet = None
    if request.content_type == "application/x-rawip-hex":
        if request.can_read_body:
            packet_hex = await request.text()
            logger.debug(f"application/x-rawip-hex: {packet_hex}")
        else:
            logger.debug("http request body is not ready.")
            return web.json_response({"Status": "Error"}, status=503)
    elif request.content_type == "text/json":
        if request.can_read_body:
            body = await request.json()
            logger.debug(f"text/json: {body}")
            packet_hex = get_value(body, ["hex_payload", "hexIPData",
                                          "Data", "data"])
            if packet_hex is None:
                logger.debug("no IP data found.")
                return
        else:
            logger.debug("http request body is not ready.")
            return web.json_response({"Status": "Error"}, status=503)
    else:
        logger.debug("content-type must be json or x-raw, but {}"
                     .format(request.content_type))
        return web.json_response({"Status": "Error"}, status=405)
    #
    packet = bytearray.fromhex(packet_hex)
    dst_l3_addr = packet[24:40]
    route_info = lookup_route(dst_l3_addr, config)
    if route_info is None:
        logger.debug(f"route for {dst_l3_addr} wasn't found.")
        return web.json_response({"Status": "NG"}, status=402)
    else:
        protocol.schc_send(route_info["dst"], dst_l3_addr, packet)
        return web.json_response({"Status": "OK"}, status=202)

async def app_uplink(request):
    """ check the message posted. process it as a uplink message.
    """
    if request.content_type == "text/json":
        if request.can_read_body:
            body = await request.json()
            logger.debug(body)
            src_l2_addr = get_value(body, ["devL2Addr", "L2Addr", "DevAddr"])
            if src_l2_addr is None:
                return
            app_data = get_value(body, ["hex_payload", "hexSCHCData",
                                        "Data", "data"])
            if app_data is None:
                return
            app_data = bytearray.fromhex(app_data)
            protocol.schc_recv(src_l2_addr, app_data)
            return web.json_response({"Status": "OK"}, status=202)
        else:
            logger.debug("http request body is not ready.")
            return web.json_response({"Status": "Error"}, status=503)
    else:
        logger.debug(f"content-type must be text/json, but {request.content_type}")
        return web.json_response("Error", status=405)


def set_logger(logging, config):
    LOG_FMT = "%(asctime)s.%(msecs)d %(message)s"
    LOG_DATE_FMT = "%Y-%m-%dT%H:%M:%S"
    logging.basicConfig(format=LOG_FMT, datefmt=LOG_DATE_FMT)
    logger = logging.getLogger(PROG_NAME)

    if config.debug_level:
        logger.setLevel(logging.DEBUG)
        logger_urllib3 = logging.getLogger("requests.packages.urllib3")
        logger_urllib3.setLevel(logging.DEBUG)
        logger_urllib3.propagate = True
    else:
        logger.setLevel(logging.INFO)

    return logger


def update_config():
    """
    priority order:
        1. arguments.
        2. config file.
        3. default.
    """
    if config.config_file is not None:
        config_from_file = json.loads(open(config.config_file).read())
    else:
        config_from_file = None
    # update l3 info
    if "route" in config_from_file:
        tmp = config_from_file["route"].copy()
        for l3a,info in tmp.items():
            if not (info["ifname"] == "lpwan" or
                    info["ifname"].startswith("lo")):
                info.update({"dst_raw": bytes([ int(_,16) for _
                                            in info["dst"].split(":") ]) })
            config_from_file["route"].update(
                    { ipaddress.ip_address(l3a).packed : info })
    # update l2 info
    if "interface" in config_from_file:
        for ifname,info in config_from_file["interface"].items():
            if ifname.startswith("lo"):
                eth_type = bytearray.fromhex("1e000000")
                addr_raw = b""
            else:
                eth_type = bytearray.fromhex("86dd")
                addr_raw = bytes([ int(_,16) for _ in
                                  info["addr"].split(":") ])
            pcap_handle = pcap.pcap(ifname, immediate=True)
            pcap_handle.setdirection(pcap.PCAP_D_OUT)
            config_from_file["interface"][ifname].update({
                    "type": eth_type, "pcap": pcap_handle,
                    "addr_raw": addr_raw })
    # set default if needed.
    for k, v in config_default.items():
        if getattr(config, k, None) is None:
            if config_from_file is not None:
                setattr(config, k, config_from_file.get(k, None))
            if getattr(config, k, None) is None:
                setattr(config, k, v)


#  main
ap = argparse.ArgumentParser(
        description="""a SCHC GW implementation""",
        epilog="still in progress.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("-c", action="store", dest="config_file",
                help="specify the config file.")
ap.add_argument("--downlink-url", action="store", dest="downlink_url",
                help="specify the URL of the NS agent for downlink.")
ap.add_argument("--bind-addr", action="store", dest="bind_addr",
                help="specify the address to be bound.")
ap.add_argument("--bind-port", action="store", dest="bind_port",
                type=int, default=None,
                help="specify the port number to be bound.")
ap.add_argument("--my-cert", action="store", dest="my_cert",
                help="specify the certificate of mine.")
ap.add_argument("--untrust", action="store_false", dest="ssl_verify",
                default=None,
                help="disable to check the server certificate.")
ap.add_argument("-d", action="store_true", dest="debug_level", default=None,
                help="specify debug level.")
config = ap.parse_args()
update_config()

# set the logger object.
logger = set_logger(logging, config)
if not config.debug_level:
    set_debug_output(True)
    requests.packages.urllib3.disable_warnings()

# create the schc protocol object.
rule_manager = RuleManager()
rule_manager.Add(device="A2345678", file=find_file(config.rule_file))
#
system = AioSystem(logger=logger, config=config)
layer2 = AioLowerLayer(system, config=config)
layer3 = AioLowerLayer(system, config=config)
protocol = protocol.SCHCProtocol(config, system, layer2, layer3,
                                 role="core-server", unique_peer=False)
protocol.set_rulemanager(rule_manager)
#
ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ctx.load_cert_chain(find_file(config.my_cert))
app = web.Application(logger=logger)
app.router.add_route("POST", "/ul", app_uplink)
app.router.add_route("POST", "/dl", app_downlink)
#
logger.info("Starting GW listening on https://{}:{}/".format(
        config.bind_addr if config.bind_addr else "*",
        config.bind_port))
web.run_app(app, host=config.bind_addr, port=config.bind_port,
            ssl_context=ctx, print=None)
