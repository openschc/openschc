#!/usr/bin/env python3

# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

"""This is a usage example of aiocoap that demonstrates how to implement a
simple server. See the "Usage Examples" section in the aiocoap documentation
for some more information."""

""" This program receives POST from devices, direclty from Wi-Fi and through
generic_coap_relay.py for LPWAN devices.

It takes a CBOR coded Time Series and trandform it on a JSON structure for
beebotte to display graphs. beebotte credentials are stored un config_bbt.py 
file.
"""

import logging
import binascii
import asyncio

import aiocoap.resource as resource
import aiocoap

import cbor2 as cbor


# Class to process data posted on /temperature.
        
class sensor_reading(resource.Resource):
    async def render_post(self, request):

        print (request)
        print ("Request URI:", request.get_request_uri())
        print ("Content-format:", request.opt.content_format)
 

        return aiocoap.Message(code=aiocoap.CHANGED)
  

class pressure(resource.Resource):
    async def render_post(self, request):

        print (">>>>", binascii.hexlify(request.payload))

        ct = request.opt.content_format or \
                aiocoap.numbers.media_types_rev['text/plain']

        if ct == aiocoap.numbers.media_types_rev['text/plain']:
            print ("text:", request.payload)
        elif ct == aiocoap.numbers.media_types_rev['application/cbor']:
            print ("cbor:", cbor.loads(request.payload))
        else:
            print ("Unknown format")
            return aiocoap.Message(code=aiocoap.UNSUPPORTED_MEDIA_TYPE)
        return aiocoap.Message(code=aiocoap.CHANGED)

class humidity(resource.Resource):
    async def render_post(self, request):

        ct = request.opt.content_format or \
                aiocoap.numbers.media_types_rev['text/plain']

        if ct == aiocoap.numbers.media_types_rev['text/plain']:
            print ("text:", request.payload)
        elif ct == aiocoap.numbers.media_types_rev['application/cbor']:
            print ("cbor:", cbor.loads(request.payload))

        else:
            print ("Unknown format")
            return aiocoap.Message(code=aiocoap.UNSUPPORTED_MEDIA_TYPE)
        return aiocoap.Message(code=aiocoap.CHANGED)

# logging setup

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main():
    # Resource tree creation
    root = resource.Site()

    # add resource processing, /proxy is not used here, see comments in generic_sensor()
    root.add_resource(['temp'], sensor_reading())
    root.add_resource(['pres'], sensor_reading())
    root.add_resource(['humi'], sensor_reading())
    
    # associate resource tree and socket
    asyncio.Task(aiocoap.Context.create_server_context(root))

    # let's go forever
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
