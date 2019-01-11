pypacket_dissector
==================

Yet another IP packet dissector.

It is going to support a small set of protocols that I need,
such as IPv6, IPv4, UDP, CoAP.

If you want to dissect L2 protocol, use pypcap_dissector instead.

If you want a full set of dissectors, use dpkt, scapy or something like that.

## goal

- python3
- simple, lightweight
- json fiendly
- support only L3 or upper protocol.

## requirement

- python3

## How to use

You can dissect data in the file you specified or stdin.

    % packet_dissector.py test.dat
      "PROTO": "IPV6"
      "HEADER": 
        "IPV6.LEN": "14"
        "IPV6.NXT": "17"
        "IPV6.HOP_LMT": "64"
        "IPV6.SADDR": "fe80:0000:0000:0000:aebc:32ff:feba:1c9f"
        "IPV6.DADDR": "fe80:0000:0000:0000:0201:c0ff:fe06:3e69"
        "IPV6.VER": "6"
        "IPV6.TC": "96"
        "IPV6.FL": "694078"
      "PAYLOAD": 
        "PROTO": "UDP"
        "HEADER": 
          "UDP.SPORT": "50145"
          "UDP.DPORT": "9999"
          "UDP.LEN": "14"
          "UDP.CKSUM": "63356"
          "PAYLOAD": "48656c6c6f0a"
        "EMSG": "unsupported. L5 PORT=(50145, 9999)"

## Usage

    usage: packet_dissector.py [-h] [-v] [-d] TARGET
    
    a packet dissector.
    
    positional arguments:
      TARGET      specify a filename containing packet data.
                  '-' allows the stdin as the input.
    
    optional arguments:
      -h, --help  show this help message and exit
      -v          enable verbose mode.
      -d          enable debug mode.


