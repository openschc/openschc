# UDP sender / receiver

## Overview

In this directory, you can find an example of openschc sender and receiver based on UDP (schc) packet transmission.
By default, the example is a device sending a single (COAP) packet with a fragmentation rule, but no compression, to
the core (server).

How to run:
1) In one terminal, on command line, run: `python udp_example.py core` 
  A node assuming the role of core (network infrastructure server) will start (waiting SCHC packet on one UDP Port)
  
2) In another terminal, on command line, run: `python udp_example.py device`
  A node assuming the role of device will start, sending a COAP packet, with

## Implementation details

`net_udp_core.py` is the full implementation of a "network connector" of openschc to transmit packets over UDP.

It implements the API documented in [../../src/abstraction.py](src/abstraction.py) and represented in the
diagram [../../docs/Internals/external-interface.svg](../../docs/Internals/external-interface.svg).

It is thus also an example of connecting openschc to a given lower-layer, and of implementing openschc external
interfaces.
