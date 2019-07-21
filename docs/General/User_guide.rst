User Guide
**********

Introduction
============

This document explains how to run the openSCHC fragmentation and compression code.

This entails the following steps:

- installing the "context" that will be used for compressing and fragmenting the traffic flows.
- establishing the flows of traffic to be compressed/decompressed and fragmented/reassembled, and potentially setup the channel characteristics (in link simulation mode)

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

In openSCHC, rules are defined through a JSON structure. The common part is the
following: ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 4
    }

The __RuleID__ is a positive integer aligned to the right. So 12 can be writen in
binary 1100. The __ruleIDLength__ gives the number of bits used. So the previous
rule is different from this one: ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 6
    }

which gives this value 001100.

Rule IDs compose a binary tree and can also be noted with the / representation
(as IP prefixes) 12/4 or 12/6.

A rule is either a fragmentation rule or a compression rule. They are differentiated
by the JSON keyword __Fragmentation__ or __Compression__. A rule can contain only one of
these keywords.

For compression, the keyword is followed by an array, containing the field descriptions.
The smallest compression rule is the one where this array is empty. ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 4,
    "Compression" : []
    }

For fragmentation, the keyword is followed by the definition of the fragmentation
parameters, which for example describe the fragmentation mode and the size of the
different fragment SCHC header fields. ::

    {
    "RuleID" : 12,
    "RuleIDLength" : 4,
    "Fragmentation" : {
      "FRMode": "noAck",
      }
    }

See below for the description of the compression and fragmentation parameters.

The following program adds these 2 basic rules into the rule manager and displays them. ::

    from rulemanager import *

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
        "FRMode": "noAck",
      }
    }

    RM.Add(dev_info=rule1100)
    RM.Add(dev_info=rule001100)

    RM.Print()

The first line imports the rule manager module.

__RM__ will be the rule manager instance. If necessary, several rule managers can be instantiated.

The two rules are created as a python dictionary and added to the instance of rule manager.

Finally, rules are displayed as cards on the console output. ::

    ****************************************
    Device: None
    /-------------------------\
    |Rule 12/4          1100  |
    |---------------+---+--+--+------------------------------+-------------+----------------\
    \---------------+---+--+--+------------------------------+-------------+----------------/
    /-------------------------\
    |Rule 12/6        001100  |
    !=========================+=============================================================\
    !! Fragmentation mode : noAck    header dtag 0 Window  0 FCN  1                        !!
    !! No Tile size specified                                                              !!
    !! MIC Algorithm: crc32                                                                !!
    \=======================================================================================/

Compression rules contain the field descriptions (here absent) and the Fragmentation rule contain the
fragmentation parameters. As we will notice in the rest of this chapter, the rule manager may add some default
parameters.

We can notice that, since no device is specified, the rules are associated to the device __None__.

In the add method, we used the __dev_info__ named argument to indicate that the rule is contained in
a python structure. The named argument  __file__ could have been used instead. In that case, a filename
containing the JSON structure is used.

Set of Rules
------------

 A  device will contain a set of rules related to compression and fragmentation. In openSCHC,
 a set of rules is an JSON array. The following program has the same behavior as the previous one.::

     from rulemanager import *

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
         "FRMode": "noAck"
       }
     }

     RM.Add(dev_info=[rule1100, rule001100])

     RM.Print()

Device definition
-----------------

As seen before, when not specified, the device is identified as __None__. This can be appropriate
when SCHC is instantiated on a device, since there is no ambiguity as to which device the rule set
applies to. Conversely,
when the SCHC instance is on the core network side, the set of rules must be associated with
a device ID.

Rules associated with a Device ID can be directly stored into the rule manager through the __Add__ method.
The JSON structure is the following: ::


    {
        "DeviceID": 1234567890,
        "SoR" : [ ..... ]
    }

where the __DeviceID__ keyword represents the device ID in a specific technology, for
instance LoRaWAN DevEUI. Note that this should be viewed as a JSON structure. Therefore,
the DeviceID literal must be expressed in decimal, not hexadecimal.
