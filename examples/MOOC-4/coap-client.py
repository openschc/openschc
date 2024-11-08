#!/usr/bin/env python3

# SPDX-FileCopyrightText: Christian Amsüss and the aiocoap contributors
#
# SPDX-License-Identifier: MIT

"""This is a usage example of aiocoap that demonstrates how to implement a
simple client. See the "Usage Examples" section in the aiocoap documentation
for some more information."""

import logging
import asyncio
import random

import time

from aiocoap import *

logging.basicConfig(level=logging.INFO)

async def main():
    protocol = await Context.create_client_context()

    if random.randint(0, 10) % 3 == 0: # wrong URI
        request = Message(code=GET, uri='coap://[aaaa::1]]/humi')
    else: #right URI
         request = Message(code=GET, uri='coap://[aaaa::1]]/temp')
       
    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    while True:
        asyncio.run(main())
        time.sleep(3)