#!/usr/bin/env python

import sys
import pcap
import requests
import argparse

requests.packages.urllib3.disable_warnings()


def cb_debug(ts, pkt, cb_arg):
    print(ts, pkt.hex())
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
        l3_header_offset = 4
    else:
        l3_header_offset = 0
    if "content-type" not in headers:
        headers["content-type"] = "application/x-rawip"
    requests.post(url, headers=headers, data=pkt[l3_header_offset:],
                  verify=verify)


class PcapWrapper():
    def __init__(self, input_device, snaplen=2000, filter_rules=None):
        # check if the devname is an interface or not.
        if input_device in pcap.findalldevs():
            self._pc = pcap.pcap(input_device, snaplen, immediate=True)
        else:
            self._pc = pcap.pcap(input_device, timeout_ms=0)
        # set filter.
        self._pc.setfilter(filter_rules)
        print("dloff:", self._pc.dloff)
        print("fd:", self._pc.fd)
        print("filter:", self._pc.filter)
        print("name:", self._pc.name)
        print("snaplen:", self._pc.snaplen)
        print("nb_blk:", self._pc.getnonblock())

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
        opt.print_help()
        exit(1)
