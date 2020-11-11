Sending/ receiving over UDP
===========================

Usage
-----

.. begin-sphynx-doc-do-no-remove

This is an example of an openSCHC sender transmitting over UDP to an openSCHC receiver, on the same host computer.
By default, the example is that of a device sending a single COAP packet processed with one fragmentation rule, but not compressed, to
the core (server).

In order to run the example, move to the examples/udp directory, then

1. In one terminal, run::

    python udp_example.py core-server

  This will start a node playing the role of the SCHC core (network infrastructure server).
  It displays the Rules stored in its context,
  ::
    ****************************************
    Device: None
    /-------------------------\
    |Rule 12/4          1100  |
    |---------------+---+--+--+------------------------------+-------------+----------------\
    \---------------+---+--+--+------------------------------+-------------+----------------/
    /-------------------------\
    |Rule 12/6        001100  |
    {'RuleID': 12, 'RuleIDLength': 6, 'Fragmentation': {'FRDirection': 'UP', 'FRMode': 'noAck', 'FRModeProfile': {'FCNSize': 3, 'dtagSize': 2, 'MICALgorithm': 'crc32', 'WSize': 0, 'L2WordSize': 8, 'windowSize': 7}}}
    !=========================+=============================================================\
    !^ Fragmentation mode : noAck    header dtag 2 Window  0 FCN  3                     UP ^!
    !^ No Tile size specified                                                              ^!
    !^ RCS Algorithm: crc32                                                                ^!
    \=======================================================================================/

  then awaits a SCHC Message on UDP port 33300 on the loopback interface.
  
2. In another terminal, run::

    python udp_example.py device

  This will start a node playing the device role.
  It will display the Rules that are stored in its context,
  ::
    ****************************************
    Device: None
   /-------------------------\
   |Rule 12/4          1100  |
   |---------------+---+--+--+------------------------------+-------------+----------------\
   \---------------+---+--+--+------------------------------+-------------+----------------/
   /-------------------------\
   |Rule 12/6        001100  |
   {'RuleID': 12, 'RuleIDLength': 6, 'Fragmentation': {'FRDirection': 'UP', 'FRMode': 'noAck', 'FRModeProfile': {'FCNSize': 3, 'dtagSize': 2, 'MICALgorithm': 'crc32', 'WSize': 0, 'L2WordSize': 8, 'windowSize': 7}}}
   !=========================+=============================================================\
   !^ Fragmentation mode : noAck    header dtag 2 Window  0 FCN  3                     UP ^!
   !^ No Tile size specified                                                              ^!
   !^ RCS Algorithm: crc32                                                                ^!
   \=======================================================================================/
  
  then send one SCHC-processed COAP packet.
  Since their is no compression Rule (except the mandatory "no-compression" Rule),
  the packet is simply prepended with the 12/4 RuleID and passed to the fragmentation sublayer.
  It is then fragmented into 13 SCHC Fragments, which are sent over UDP.
  Hit Ctrl+C to exit.

In the first terminal,
you can observe the SCHC Fragments being received by the SCHC core (server),
being reassembled into one SCHC Packet with sucessful RCS (previously known as MIC) check.
It is then passed up to the decompression sublayer,
which has nothing to do except strip off the 12/4 RuleID.

.. end-sphynx-doc-do-no-remove

Implementation details
----------------------

`net_udp_core.py` is the full implementation of a "network connector" of openschc to transmit SCHC Messages over UDP.

It implements the API documented in [../../src/abstraction.py](src/abstraction.py) and represented in the
diagram [../../docs/Internals/external-interface.svg](../../docs/Internals/external-interface.svg).

It is thus also an example of connecting openschc to a lower layer, and of implementing openschc external
interfaces.
