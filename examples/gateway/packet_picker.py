#!/usr/bin/env python

import sys
import pcap
import requests
import argparse

requests.packages.urllib3.disable_warnings()


def dprint(*args, **kw):
    """Debug print"""
    if opt.debug:
        print(*args, **kw)
        sys.stdout.flush()


def cb_debug(ts, pkt, cb_arg):
    dprint(ts, pkt.hex())
    sys.stdout.flush()


def cb_post(ts, pkt, cb_arg, raw_packet=False):
    """
    cb_arg: dict: "url" "headers", "verify"
    if raw_packet is False, pkt is expected as the output of tcpdump.
    """
    url = cb_arg.get("url")
    verify = cb_arg.get("verify")
    headers = cb_arg.get("headers")
    if raw_packet is False:
        # skip the pcap header.
        packet = pkt[4:].hex()
    else:
        packet = pkt.hex()
    if "content-type" not in headers:
        headers["content-type"] = "application/x-rawip-hex"
    requests.post(url, headers=headers, data=packet,
                  verify=verify)


class PcapWrapper():
    def __init__(self, input_device, snaplen=2000, filter_rules=None):
        # check if the devname is an interface or not.
        if input_device in pcap.findalldevs():
            self._pc = pcap.pcap(input_device, snaplen, immediate=True)
        else:
            self._pc = pcap.pcap(input_device, timeout_ms=0)
        # set filter.
        if filter_rules is not None:
            self._pc.setfilter(filter_rules)
        #
        dprint("dloff:", self._pc.dloff)
        dprint("fd:", self._pc.fd)
        dprint("filter:", self._pc.filter)
        dprint("name:", self._pc.name)
        dprint("snaplen:", self._pc.snaplen)
        dprint("nb_blk:", self._pc.getnonblock())

    def run(self, cb=cb_post, cb_arg=None):
        while True:
            self._pc.loop(-1, cb, cb_arg)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
            description="the packet picker for SCHC GW",
            epilog="still in progress.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("url", metavar="URL", action="store",
                    help="""specify the URL to which the data is sent.
                    e.g. https://127.0.0.1:51225/dl""")
    ap.add_argument("-i", action="store", dest="ifname",
                    help="specify the name of the interface to be listen.")
    ap.add_argument("-f", action="store", dest="data_file",
                    help="""specify the file name containing the data
                    to be sent.""")
    ap.add_argument("-F", action="store", dest="filters",
                    help="specify the filters.")
    ap.add_argument("--untrust", action="store_false", dest="trust_server",
                    help="disable to check the server certificate.")
    ap.add_argument("-d", action="store_true", dest="debug",
                    help="enable debug mode.")
    opt = ap.parse_args()
    #
    cb_arg = {
            "url": opt.url,
            "verify": opt.trust_server,
            "headers": {}
            }
    if opt.ifname:
        pc = PcapWrapper(opt.ifname, filter_rules=opt.filters)
        pc.run(cb_arg=cb_arg)
    elif opt.data_file:
        packet = open(opt.data_file, "rb").read()
        cb_post(None, packet, cb_arg, raw_packet=True)
    else:
        ap.print_help()
        exit(1)
