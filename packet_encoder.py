#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from pypacket_dissector import encoder as en
except:
    import encoder as en

jo = en.load_json_packet('''
{
    "PROTO": "IPV6",
    "HEADER": {
        "IPV6.VER": 6,
        "IPV6.TC": 0,
        "IPV6.FL": 590768,
        "IPV6.LEN": 16,
        "IPV6.NXT": 58,
        "IPV6.HOP_LMT": 64,
        "IPV6.SADDR": "2001:420:5e40:1254:5ce9:5a3b:8433:600c",
        "IPV6.DADDR": "2607:f8b0:4004:80c::2004"
    },
    "PAYLOAD": {
        "PROTO": "ICMPV6",
        "HEADER": {
            "ICMPV6.TYPE": 128,
            "ICMPV6.CODE": 0,
            "ICMPV6.CKSUM": 53657,
            "ICMPV6.IDENT": 30320,
            "ICMPV6.SEQNO": 0
        },
        "PAYLOAD": "5ab9c619000d5fe4"
    }
}
''')
ret = en.encoder(jo)
sys.stdout.buffer.write(ret)

'''
{
    "PROTO":"IPV6",
    "HEADER": {
        "IPV6.SADDR": "::1",
        "IPV6.DADDR": "::1"
    },
    "PAYLOAD": {
        "PROTO": "ICMPV6",
        "HEADER": {
            "ICMPV6.TYPE": 128
        },
        "PAYLOAD": "Hello World"
    }
}
'''
