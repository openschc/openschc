# Introduction

The context includes a set of rules (sor) shared by both ends.
Identical Rules are used on both ends. They can be simply
copied/pasted from one end to the other end, if both ends use the same format for describing them.

This document specifies the OpenSCHC rule data model, which is based on JSON.

# Rule definition

A rule is described as a JSON dictionary.

A rule is identified by its RuleID.

The size of the RuleID representation can change from one rule to
the next. Therefore, the rule description includes a RuleIDLength that indicates the length of the RuleID, in bits.

Both fields are integer numbers.


    {
    "RuleID" : 12,
    "RuleIDLength" : 4
    # notice that RuleID 12 represented on 6 bits is different from RuleID 12 on 4 bits!
    }

In SCHC, rules are used either for compression or fragmentation. Therefore, one and only one of the two keywords "fragmentation" or "compression" must be specified, per rule.

## Compression Rules

As defined in the SCHC specification, compression rules are composed of Field Descriptions.
The order in which the Field Descriptions appear in the rule is significant (e.g. it defines the order in which the compression residues are sent), therefore a compression rule is represented as an array.

The Field Description is a dictionary containing the key+data pairs as defined in the SCHC specification:
* "**FID**": a string identifying the field of the protocol header that is being compressed. The value of this string is the one returned by the protocol analyzer when encountering said field. E.g. "IPV6.VER". <<< why is this not IP.VER instead? It seems to me that IPV6.VER will always be 6!>>>
* "**FL**": if the value is a number, that value expresses the length of the field, in bits. If the
value is a string, it designates a function that can compute the field length. The functions currently defined are:
  * "_**var**_": the field is of variable length. It will be determined at run time by the protocol analyzer. The length (expressed in bytes) will be transmitted as part of the compression residue. The encoding is described in the SCHC specification.
  * "_**tkl**_" <<<"_coaptkl_"?>>>: this function is specific for compressing the CoAP Token field. The length of the Token is determined at run time by the protocol analyzer by looking at the Token Length field of he CoAP header.
* "**FP**": an integer specifying the position in the header of the field this Field Description applies to. The default value is 1. For each recurrence of the same field in the header, the value is increased by 1.
* "**DI**": tells the direction to which this Field Description applies:
    * "_**Up**_": only to uplink messages (i.e. from device to network)
    * "_**Dw**_": only to downlink messages (i.e. from network to device)
    * "_**Bi**_": to both directions

* "**TV**": specifies the Target Value. The value is a number, a string or an array of these types. The "TV" key can be omitted or its value set to null if there is no value to check, for instance together with the "ignore" MO. If the Target Value is an array, then the value null among the array elements indicates that
the Field Descriptor matches the case where the field is not present in the header being compressed.
* "**MO**": specifies the Matching Operator. It is a string that can take the following values:
  * "_**ignore**_": the field must be present in the header, but the value is not checked.
  * "_**equal**_": type and value must check between the field value and the Target Value <<< il y a des champs avec des descriptions explicites de type dans les protocoles considérés ? >>
  * "_**MSB**_": the most significant bits of the Target Value are checked against the most significant bits of the field value. The number of bits to be checked is given by the "MOa" field.
  * "_**match-mapping**_": with this MO, the Target Value must be an array. This MO matches when one element of the Target Value array matches the field, in type and value.
* "**MOa**": specifies, if applicable, an argument to the MO. This currently only applies to the "MSB" MO, where the argument specifies the length of the matching, in bits.
* "**CDA**": designates the Compression/Decompression Action. It is a string that can take the following values:
   * "_**not-sent**_": the field value is not sent as a residue.
   * "_**value-sent**_": the field value is sent in extenso in the residue.
   * "_**LSB**_": the bits remaining after the MSB comparison are sent in the residue.
   * "_**mapping-sent**_": the index of the matching element in the array is sent.
   * "_**compute**_": the field is not sent in the residue and the receiver knows how to recover the value from other information. This is generally used for length and checksum.
* "**CDAa**": represents the argument of the CDA. Currently, no CDAa is defined.

For example:


    {
    "RuleID" : 12,
    "RuleIDLength" : 4,
    "compression": [
        {
        "FID": "IPV6.VER",
        "FL": 4,
        "FP": 1,
        "DI": "Bi",
        "TV": 6,
        "MO": "equal",
        "CDA": "not-sent"
        },
        {
        "FID": "IPV6.DEV_PREFIX",
        "FL": 64,
        "FP": 1,
        "DI": "Bi",
        "TV": [ "2001:db8::/64", "fe80::/64", "2001:0420:c0dc:1002::/64" ],
        "MO": "match-mapping",
        "CDA": "mapping-sent",
        },
        ]
    }


## Fragmentation Rules
<<< to be written >>>.

# Context

A context is associated with a specific device, which may be identified by a unique LPWAN
identifier, for instance a LoRaWAN devEUI.

The context also includes a set of rules. The rule description is defined [above](#rule-definition).


    {
        "DeviceID": 0x1234567890,
        "sor" : { ..... }
    }

DeviceID is a numerical value that must be unique in the context. If the context is used on a device, the deviceID may be omitted or set to null. In the core network, the DeviceIDs must be specified.

The set of rules itself expands as shown below.

    {
        {
        "RuleID" : 12,
        "RuleIDLength" : 4,
        "compression": [
            {
            "FID": "IPV6.VER",
            "FL": 4,
            "FP": 1,
            "DI": "Bi",
            "TV": 6,
            "MO": "equal",
            "CDA": "not-sent"
            },
            {
            "FID": "IPV6.DEV_PREFIX",
            "FL": 64,
            "FP": 1,
            "DI": "Bi",
            "TV": [ "2001:db8::/64", "fe80::/64", "2001:0420:c0dc:1002::/64" ],
            "MO": "match-mapping",
            "CDA": "mapping-sent",
            },
          ]
        },
        {
        "RuleID" : 13,
        "RuleIDLength" : 4,
        "fragmentation" : ....
        },
        .....
    }



# RuleManager

The Rule Manager manages the context(s) for a specific device or a set of devices. It maintains the context database and ensures its consistency.


## Class RuleManager

A RuleManager object is created this way:

      from RuleManager import *
      RM = RuleManager()

### Add

Add is used to add a new rule to a context <<< only one, or a set of rules? >>>. Add checks the validity of the rule:
* ruleID/RuleIDLength do not overlap
* the rule contains either one of a fragmentation and a compression description.

If the DeviceID already exists in the context, the new rule is added to that context, providing no conflict on the RuleID is found.

      RM.add ({"DeviceID": 0x1234567, "sor": {.....}})

### Remove

Suppresses a rule for a specific device <<< only one, or a set of rules? >>>. If no rule is specified, all rules for that device are removed from the context.

      RM.remove ({"deviceID": 0x1234567, "sor": {{"ruleID":12, "ruleLength":4}}})
      RM.remove ({"deviceID": 0x1234567})

### FindRuleFromPacket

This method returns a rule and a DeviceID that match a packet description given by the protocol analyzer.

### FindFragmentationRule (size)

Returns a fragmentation rule compatible with the packet size passed as parameter.


### FindRuleFromID

Given the first bits received from the LPWAN, returns either a fragmentation or a compression rule.
