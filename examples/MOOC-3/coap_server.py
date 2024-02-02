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

import datetime
import time
import logging
import binascii
import pprint
import asyncio

import aiocoap.resource as resource
import aiocoap

import cbor2 as cbor
import config_bbt #secret keys 
import beebotte


# establish the context with beebotte.
bbt = beebotte.BBT(config_bbt.API_KEY, config_bbt.SECRET_KEY) 


def to_bbt(channel, res_name, msg, factor=1, period=10, epoch=None):
    """This function takes a python array representing a time serie 
    and transform it into a JSON structure expected by beebotte. 
    - channel and res_name are names defined in the Beebotte account 
    in the channel page
    - msg is the data sent by the devices
    - factor is the precision on the measure. for instance .01 divide
    by 100 the value
    - period is the interval between 2 measurement on the device.
    - epoch can be set at the function call, but bu default the 
    reception time is considered as the time of the last sample.
     """
    global bbt

    prev_value = 0
    data_list = []
    if epoch:
        back_time = epoch
    else: # get current time as epoch
        back_time = time.mktime(datetime.datetime.now().timetuple())
    
    back_time -= len(msg)*period # go back in time to get the epoch of the 
                                 # first sample

    for e in msg: # create the beebotte array
        prev_value += e
        
        back_time += period

        data_list.append({"resource": res_name,
                          "data" : prev_value*factor,
                          "ts": back_time*1000} )

    pprint.pprint (data_list)
    
    bbt.writeBulk(channel, data_list) # send it


#


class generic_sensor(resource.PathCapable):
    """  this class is not used in this progamm, but kept because it is
    hard to find this in the documentation of aiocoap. The goal of
    PathCapable object is to process the rest of an URI.
    for example, we can have something like:
        /proxy/devEUI/humidity 
    where devEUI is the sensor devEUI and can be viewed as a channel
    by beebotte. the method add_resource has been setup with /proxy.
    render method will not see the /proxy but will have the remaining
    element in uri_path. Not that iit a render and the method should
    be tested.
    """

    async def render(self, request):
        print ("render", request.opt.uri_path)
        devEUI = request.opt.uri_path[0]
        measurement = request.opt.uri_path[1]

        print (devEUI, measurement)

        ct = request.opt.content_format or \
                aiocoap.numbers.media_types_rev['text/plain']

        if ct == aiocoap.numbers.media_types_rev['text/plain']:
            print ("text:", request.payload)
        elif ct == aiocoap.numbers.media_types_rev['application/cbor']:
            print ("cbor:", cbor.loads(request.payload))
            to_bbt(devEUI, measurement, cbor.loads(request.payload), period=60, factor=0.01)
        else:
            print ("Unknown format")
            return aiocoap.Message(code=aiocoap.UNSUPPORTED_MEDIA_TYPE)
        return aiocoap.Message(code=aiocoap.CHANGED)


    async def needs_blockwise_assembly(self, request):
        return False


# Class to process data posted on /temperature.
        
class temperature(resource.Resource):
    async def render_post(self, request):

        # if no content_format option set the default value
        ct = request.opt.content_format or \
                aiocoap.numbers.media_types_rev['text/plain']

        # text will just display the value
        if ct == aiocoap.numbers.media_types_rev['text/plain']:
            print ("text:", request.payload)
        # cbor will be displayed and processed.
        elif ct == aiocoap.numbers.media_types_rev['application/cbor']:
            print ("cbor:", cbor.loads(request.payload))
            to_bbt("capteurs", "temperature", cbor.loads(request.payload), period=60, factor=0.01)
        else:
            print ("Unknown format")
            return aiocoap.Message(code=aiocoap.UNSUPPORTED_MEDIA_TYPE)
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
            to_bbt("capteurs", "pressure", cbor.loads(request.payload), period=1, factor=0.01)
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
            to_bbt("capteurs", "humidity", cbor.loads(request.payload), period=60, factor=1)

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
    root.add_resource(['temperature'], temperature())
    root.add_resource(['pressure'], pressure())
    root.add_resource(['humidity'], humidity())
    root.add_resource(['proxy'], generic_sensor())
    
    # associate resource tree and socket
    asyncio.Task(aiocoap.Context.create_server_context(root))

    # let's go forever
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
