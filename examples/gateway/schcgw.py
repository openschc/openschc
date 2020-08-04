#!/usr/bin/env python

import argparse
import json
from aiohttp import web
import ssl
import logging
import pcap
import os
import ipaddress

from net_aio_core import *
from gen_rulemanager import *
import protocol
from gen_utils import dprint, dpprint, set_debug_output

#----

config_default = {
    "debug_level": 0,
    "enable_sim_device": False,
    "bind_addr": "::",
    "bind_port": 51225,
    "downlink_url": None,
    "ssl_verify": True,
    "my_cert": None,
    "rule_config": None,
    "route": {},
    "interface": {},
    }


def set_logger(config):
    LOG_FMT = "%(asctime)s.%(msecs)d %(message)s"
    LOG_DATE_FMT = "%Y-%m-%dT%H:%M:%S"
    logging.basicConfig(format=LOG_FMT, datefmt=LOG_DATE_FMT)
    logger = logging.getLogger(config.prog_name)

    if config.debug_level:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger

#----

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
    elif request.content_type == "application/json":
        if request.can_read_body:
            body = await request.json()
            logger.debug(f"application/json: {body}")
            body = json.loads(body)
            packet_hex = body.get("hexIPData")
            if packet_hex is None:
                logger.debug("no payload found.")
                return web.json_response({"Status": "Error"}, status=400)
            else:
                # successful to take a packet from the request.
                pass
        else:
            logger.debug("http request body is not ready.")
            return web.json_response({"Status": "Error"}, status=503)
    else:
        logger.debug("content-type must be json or x-raw, "
                     "but {request.content_type}")
        return web.json_response({"Status": "Error"}, status=405)
    #
    await protocol.layer3.send_packet(bytearray.fromhex(packet_hex))
    return web.json_response({"Status": "OK"}, status=202)

async def app_uplink(request):
    """ check the message posted. process it as a uplink message.
    """
    if request.content_type == "application/json":
        if request.can_read_body:
            body = await request.json()
            logger.debug(body)
            body = json.loads(body)
            src_l2_addr = body.get("devL2Addr")
            if src_l2_addr is None:
                logger.debug("no IP addr found.")
                return web.json_response({"Status": "Error"}, status=400)
            else:
                data_hex = body.get("hexSCHCData")
                if data_hex is None:
                    logger.debug("no SCHC data found.")
                    return web.json_response({"Status": "Error"}, status=400)
                else:
                    # successful to take a packet from the request.
                    await protocol.layer2.recv_packet(
                            bytearray.fromhex(data_hex), src_l2_addr)
                    return web.json_response({"Status": "OK"}, status=202)
        else:
            logger.debug("http request body is not ready.")
            return web.json_response({"Status": "Error"}, status=503)
    else:
        logger.debug("content-type must be application/json, "
                     f"but {request.content_type}")
        return web.json_response("Error", status=405)


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
    if config_from_file is not None:
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
ap.add_argument("--prog-name", action="store", dest="prog_name",
                default="GW",
                help="specify the name of this program.")
ap.add_argument("-d", action="store_true", dest="debug_level", default=None,
                help="specify debug level.")
config = ap.parse_args()
update_config()

# set the logger object.
logger = set_logger(config)
if not config.debug_level:
    set_debug_output(True)

# create the schc protocol object.
rule_manager = RuleManager()
for x in config.rule_config:
    rule_manager.Add(device=x.get("devL2Addr"), file=x["rule_file"])
if config.debug_level:
    rule_manager.Print()
#
system = AioSystem(logger=logger, config=config)
layer2 = AioLowerLayer(system, config=config)
layer3 = AioUpperLayer(system, config=config)
protocol = protocol.SCHCProtocol(config, system, layer2, layer3,
                                 role="core-server", unique_peer=False)
protocol.set_rulemanager(rule_manager)
#
ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ctx.load_cert_chain(config.my_cert)
app = web.Application(logger=logger)
if config.enable_sim_device:
    app.router.add_route("POST", "/ul", app_downlink)
    app.router.add_route("POST", "/dl", app_uplink)
else:
    app.router.add_route("POST", "/ul", app_uplink)
    app.router.add_route("POST", "/dl", app_downlink)
#
logger.info("Starting {} listening on https://{}:{}/".format(
        config.prog_name,
        config.bind_addr if config.bind_addr else "*",
        config.bind_port))
web.run_app(app, host=config.bind_addr, port=config.bind_port,
            ssl_context=ctx, print=None)
