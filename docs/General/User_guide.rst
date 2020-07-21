User Guide
**********

Introduction
============

This document explains how to run the openSCHC fragmentation and compression code.

This entails the following steps:

- installing the "context" that will be used for compressing and fragmenting the traffic flows.
- establishing the flows of traffic to be compressed/decompressed and fragmented/reassembled,
  and potentially setup the channel characteristics (in link simulation mode)

Rule Manager
============

SCHC is based on rules, each of them identified through a Rule ID. A Rule ID designates a rule that is
common between a SCHC instance in a device and a SCHC instance in the core network.
Conversely, a same Rule ID can be used to designate different rules in different devices.

The Rule ID has a variable length, which allows allocating shorter values
to more frequent rules, if desired.

Rule definition
---------------

The rule manager is used to manage rules in the SCHC instances in the device and
in the core network. On the device side, the rules that are installed are likely to be only the ones
used by the applications running on that particular device. Conversely, on the core network side, the
rule manager has to maintain a copy of the rules of each associated device.

The rule semantics is defined in the the `SCHC context data model <https://datatracker.ietf.org/doc/draft-ietf-lpwan-schc-yang-data-model/?include_text=1>`_.
However, in openSCHC, rules are written as JSON structures. The common part is the
following: ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 4
    }

The **RuleID** is a positive integer, right-aligned on the number of bits specified by **ruleIDLength**.
In this first exemple, the RuleID is binary 1100.
This rule is different from that one: ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 6
    }

which yields the binary value 001100.

Rule IDs compose a binary tree and can also be noted with the / representation
(as IP prefixes) 12/4 or 12/6.

A rule is either a fragmentation rule or a compression rule. They are differentiated
by the JSON keyword **Fragmentation** or **Compression**. A rule can contain only one of
these keywords.

For compression, the keyword is followed by an array, containing the field descriptions.
A trivial compression rule is one where this array is empty. ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 4,
    "Compression" : []
    }

For fragmentation, the keyword is followed by the definition of the fragmentation
parameters, which for example describe the fragmentation mode, the direction of the flow the
rule applies to and optionnally the size of the different fragment SCHC header fields. ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 4,
    "Fragmentation" : {
      "FRMode" : "noAck",
      "FRDirection" : "UP"
      }
    }

See below for the description of the compression and fragmentation parameters.

The following Python code adds these 2 basic rules into the OpenSCHC rule manager and displays them. ::

    from gen_rulemanager import *

    RM = RuleManager()

    rule1100 =   {
      "RuleID" : 12,
      "RuleIDLength" : 4,
      "Compression" : []
    }

    rule001100 =   {
      "RuleID" : 12,
      "RuleIDLength" : 6,
      "Fragmentation" :  {
        "FRMode" : "noAck",
        "FRDirection" : "UP"
      }
    }

    RM.Add(dev_info=rule1100)
    RM.Add(dev_info=rule001100)

    RM.Print()

The first line imports the rule manager module.

**RM** will be the rule manager instance. If necessary, several rule managers can be instantiated.

The two rules are created as Python dictionaries and added to the instance of the rule manager.

Finally, the rules are displayed as cards on the console output. ::

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

Compression rules contain the field descriptions (here absent) and Fragmentation rules contain the
fragmentation parameters. As we will notice in the rest of this chapter, the rule manager may add some default
parameters.

We can notice that, since no device is specified, the rules are associated to the device **None**.

In the Add() method, we used the **dev_info** named argument to indicate that the rule is contained in
a Python structure. The named argument  **file** could have been used instead, with the name of the file
containing the JSON structure.

Set of Rules
------------

A device should contain a set of rules related to compression and fragmentation. In OpenSCHC,
the SoR (set of rules) is a JSON array. The following program has the same behavior as the previous one.::

  from gen_rulemanager import *

  RM = RuleManager()

  rule1100 =   {
   "RuleID" : 12,
   "RuleIDLength" : 4,
   "Compression" : []
  }

  rule001100 =   {
   "RuleID" : 12,
   "RuleIDLength" : 6,
   "Fragmentation" : {
     "FRMode": "noAck",
     "FRDirection" : "UP"
   }
  }

  RM.Add(dev_info=[rule1100, rule001100])

  RM.Print()

Device definition
-----------------

As seen before, when not specified, the device is identified as **None**. This can be appropriate
when SCHC is instantiated on a device, since there is no ambiguity as to which device the rule set
applies to. Conversely,
when the SCHC instance is on the core network side, the set of rules must be associated with
a device ID.

Rules associated with a Device ID can be directly stored into the rule manager through the **Add()** method
as follows: ::

    RM.Add(device="1234567890", dev_info=[rule1100, rule001100])

Alternately, the JSON structure would be the following: ::

    {
        "DeviceID": 1234567890,
        "SoR" : [ ..... ]
    }

where the **DeviceID** keyword represents the device ID in a specific LPWAN technology, for
instance the LoRaWAN DevEUI. Note that this should be viewed as a JSON structure. Therefore,
the DeviceID literal must be expressed in decimal, not hexadecimal.

Fragmenter/Reassembler
======================

Using the client-server simulation, it is possible to observe some important details about noAck mode and
fragmenter/reassembler. First of all, it is necessary to create a file with any name (e.g. rule1.json)
into the **examples/configs** folder, which will contain our rules as follows: ::

    [{
       "RuleID" : 12,
       "RuleIDLength" : 4,
       "Compression" : []
     },{
      "RuleID" : 12,
      "RuleIDLength" : 6,
      "Fragmentation" :  {
        "FRMode": "noAck",
        "FRDirection" : "UP"
      }
    }]

Then, it is possible to define the message that will be sent from client to server. The **examples/tcp/payload** folder
contains some examples that can be used.  

Go to the **examples/tcp** directory.

Add the SCHC directory to your PYHTONPATH. On sh, this would be:

    $ export PYTHONPATH=<YOUR_PATH_TO_SCHC>

On csh:

    $ setenv PYTHONPATH <YOUR_PATH_TO_SCHC>

From the examples/tcp directory, we can execute the code as follows:

Run Server on terminal 1 ::

    python3 ClientServerSimul.py --role server --compression false --rule ../configs/rule1.json

Run Client on terminal 2 ::

    python3 ClientServerSimul.py --role client --compression false --rule ../configs/rule1.json --time 20 --payload payload/testfile_small.txt

TODO: fix this

If the sending was successful, the sent RCS will be equal to the RCS calculated by the server at the end of the
transmission of the message and we will obtain the following result on the server side: ::

    Recv MIC 804779011, base = bytearray(b'2018-11-20 11:00:16 - daemon.py (162) - INFO : Stopping daemon...\n2018-11-20 11:00:42 - daemon.py (125) - INFO : Starting daemon...\n2018-11-20 11:00:42 - daemon.py (107) - INFO : Daemon started\x00'), lenght = 194
    SUCCESS: MIC matched. packet bytearray(b'/\xf7\xf4\x03') == result b'/\xf7\xf4\x03'

where, on the first line we have the value of the RCS sent, the message received by the server which is the same as the
one sent by the client, and the length of the message in bytes. On the second line, whe have a confirmation of successful
matching between both RCS Values.

Next, to simulate packet loss during transmission, we can use the **--loss true** argument in the client
and server terminal. With this parameter we can observe the result obtained when the transmission is not successful
since the RCS sent by the client is not the same as the RCS calculated by the server: ::

    Recv MIC 907239817, base = bytearray(b'2018-11-20 11:00:16 - daemon.py (162) - INFO : Stopping daemon...\n2018-11-20 11:00:42 - daemon.py (125) - INFO : Starting daemon...\n2018-11-20 11:00:42 - daemon.py (1062\xb2\x00'), lenght = 171
    ERROR: MIC mismatched. packet bytearray(b'/\xf7\xf4\x03') != result b'6\x13a\x89'

Unlike the successful result, we can notice that the message was not completely received by the server. Besides, the RCS
sent by the client is not equal to the RCS calculated by the server.

Client-server Simulation
========================

Introduction
------------

Client-server Simulation implements the Socket library to perform the communication between a client and a server,
using the localhost address 127.0.0.1, port 1234, TCP protocol and threads on the server to allow communication
**from several clients to a server**.

At the end of a successful communication, the simulation records the time in seconds at that instant in the text file
**client_server_simulation.txt**, and restarts sending the same message from the client to the server.

How to run this simulation
--------------------------

Run Client on terminal 1 ::

    python3 ClientServerSimul.py --role client

Run Server on terminal 2 ::

    python3 ClientServerSimul.py --role server


Option List
-----------
We can find some option to modify our client-server simulation: ::

    usage: ClientServerSimul.py [-h] [--role ROLE] [--payload PAYLOAD_NAME_FILE]
                                [--rule RULE_NAME_FILE]
                                [--time TIME_BETWEEN_ITERATION]
                                [--loss [PACKET_LOSS_SIMULATION]]
                                [--compression [MODE_WITH_COMPRESSION]]

    a SCHC simulator.

    optional arguments:
      -h, --help            show this help message and exit
      --role ROLE           specify a role: client or server. (default: client)
      --payload PAYLOAD_NAME_FILE
                            Specify a payload file name. e.g.
                            payload/testfile_small.txt. (default: )
      --rule RULE_NAME_FILE
                            Specify a rule file name. e.g. examples/comp-
                            rule-100.json. (default: examples/comp-rule-100.json)
      --time TIME_BETWEEN_ITERATION
                            Specify a time in seconds between each sending message
                            . (default: 10)
      --loss [PACKET_LOSS_SIMULATION]
                            Simulation using packet loss: True or False. (default:
                            False)
      --compression [MODE_WITH_COMPRESSION]
                            Simulation using compression: True or False. (default:
                            True)

Some options are defined to be used by both client and server devices, while there are other options that are only
useful for the client: ::

    Options for Client and Server:
    --role
    --rule
    --compression
    --loss

    Options only for Client:
    --time
    --payload
