Sending/ receiving over UDP
===========================

Usage
-----

.. include:: UDP_implementation_usage.rst

..
  This is an example of openSCHC sending over UDP to an openSCHC receiver, on the same machine.
  By default, the example is that of a device sending a single COAP packet with a fragmentation rule, but no compression, to
  the core (server).
  
  How to run:
  
  1. In one terminal, run::
  
      python udp_example.py core-server
  
    This will start a node playing the role of the SCHC core (network infrastructure server),
    awaiting a SCHC Message on a UDP port.
    
  2. In another terminal, run::
  
      python udp_example.py device
  
    This will start a node playing the device role, sending one SCHC-processed COAP packet. Hit Ctrl+C to exit.
  

Implementation details
----------------------

`net_udp_core.py` is the full implementation of a "network connector" of openschc to transmit SCHC Messages over UDP.

It implements the API documented in [../../src/abstraction.py](src/abstraction.py) and represented in the
diagram [../../docs/Internals/external-interface.svg](../../docs/Internals/external-interface.svg).

It is thus also an example of connecting openschc to a lower layer, and of implementing openschc external
interfaces.
