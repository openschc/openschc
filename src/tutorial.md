# Introduction

This document explain how to implement fragmentation and compression using openSCHC.

SCHC is based on rules, each of them identified through a rule ID. A rule ID is
common between an SCHC instance in a device and a SCHC instance in the core network.
In other worlds a same value can be used differently by two devices.

The rule ID has also a variable length, which is helpful to allocate shorter values
to more frequent rules.

# Rule Manager

## Rule definition

The rule manager is used to manage rules in the SCHC instances in the device and
in the core network. In a device side, the rules are often limited to the rules
used by the applications running on the device. On the core network side, the
rule manager has to maintain a copy of the all the devices.

In openSCHC rules are defined though a JSON structure. The common part is the
following:

    {
    "RuleID" : 12,
    "RuleIDLength" : 4
    }

The __RuleID__ is an positive integer aligned on the right. So 12 can be writen in
binary 1100. The __ruleIDLength__ gives the number of bits used. So the previous
rule is different of this one:

    {
    "RuleID" : 12,
    "RuleIDLength" : 6
    }

which gives this value 001100.

Rules are representing a binary tree and can also be noted with the / representation
(as IP prefixes) 12/4 or 12/6.

A rule is either a fragmentation rule or a compression rule. They are differentiated
by the JSON keyword __Fragmentation__ or __Compression__. A rule can contain only one of
these keywords.

For compression, the keyword is followed by an array, containing the field description.
The smallest compression rule is when this field is empty.

    {
    "RuleID" : 12,
    "RuleIDLength" : 4,
    "Compression" : []
    }

For fragmentation, the keyword is followed by the definition of the fragmentation
parameters, giving the mode and the size of the different fragment SCHC header fields.

    {
    "RuleID" : 12,
    "RuleIDLength" : 4,
    "Fragmentation" : {
      "FRMode": "noAck",
      }
    }

We will describe the compression and fragmentation parameters in following chapters.

The following program adds these 2 basic rules in the rule manager and display them.

    from rulemanager import *

    RM = RuleManager()

    rule1100 =   {
      "RuleID" : 12,
      "RuleIDLength" : 4,
      "Compression" : []
      }

    rule001100 =     {
        "RuleID" : 12,
        "RuleIDLength" : 6,
        "Fragmentation" : {
          "FRMode": "noAck",
          }
        }

    RM.Add(dev_info=rule1100)
    RM.Add(dev_info=rule001100)

    RM.Print()

The first line import the rule manager module.

__RM__ will be the rule manager. If necessary, several rule manager can be created.

The two rules are created as a python dictionary and added to the instance of rule manager.

Finally rules are displayed as cards.

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

Compression rule contains the field description (here empty) and the Fragmentation rule CONTAINS
fragmentation parameters. As we will notice in the rest of this chapter, the rule manager, manyadd some default
parameters.

We can notice that since no device are specified, the rules are associated the the device None.

In the add method, we used the __dev_info__ named argument to indicate that the rule is contained in
a python structure. The named argument  __file__ could has be used instead. In that case a filename
containing the JSON structure as to be used.

 ## Set of Rules

 A specific device will contain a set of rules related to compression and fragmentation. In openSCHC
 a set of rule is an JSON array. The following program has the same behavior as the previous one.

     from rulemanager import *

     RM = RuleManager()

     rule1100 =   {
       "RuleID" : 12,
       "RuleIDLength" : 4,
       "Compression" : []
       }

     rule001100 =     {
         "RuleID" : 12,
         "RuleIDLength" : 6,
         "Fragmentation" : {
           "FRMode": "noAck",
           }
         }

     RM.Add(dev_info=[rule1100, rule001100])

     RM.Print()

## device definition
