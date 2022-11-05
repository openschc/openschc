"""
The Rule Manager manages the context(s) for a specific device or a set of devices.
It maintains the context database and ensures its consistency. The hierarchy is the
following:

+ context_database

  + device_context

    + set_of_rules

      + rule_id/rule_id_length

        + rules

          + Fragmentation
          + Compression

------------
Introduction
------------

The context includes a set of rules shared by both ends.
Identical Rules are used on both ends. They can be simply
copied/pasted from one end to the other end, if both ends use the same format for describing them.

This document specifies the OpenSCHC rule data model, which is based on JSON.

---------------
Rule definition
---------------

A rule is described as a JSON dictionary.

A rule is identified by its RuleID.

The size of the RuleID representation can change from one rule to
the next. Therefore, the rule description includes a RuleIDLength that indicates the length of the RuleID, in bits.

Both fields are integer numbers::

    {
    "RuleID" : 12,
    "RuleIDLength" : 4
    # notice that RuleID 12 represented on 6 bits is different from RuleID 12 on 4 bits!
    }

In SCHC, rules are used either for compression or fragmentation. Therefore, one and only one of the two keywords "fragmentation" or "compression" must be specified, per rule.

Compression Rules
-----------------

As defined in the SCHC specification, compression rules are composed of Field Descriptions.
The order in which the Field Descriptions appear in the rule is significant (e.g. it defines the order in which the compression residues are sent), therefore a compression rule is represented as an array.

The Field Description is a dictionary containing the key+data pairs as defined in the SCHC specification:

* **FID**: a string identifying the field of the protocol header that is being compressed. The value of this string is the one returned by the protocol analyzer when encountering said field. E.g. "IPV6.VER". <<< why is this not IP.VER instead? It seems to me that IPV6.VER will always be 6!>>>
* **FL**: if the value is a number, that value expresses the length of the field, in bits. If the \
value is a string, it designates a function that can compute the field length. The functions currently defined are:

  * *var*: the field is of variable length. It will be determined at run time by the protocol analyzer. The length (expressed in bytes) will be transmitted as part of the compression residue. The encoding is described in the SCHC specification.
  * *tkl*: this function is specific for compressing the CoAP Token field. The length of the Token is determined at run time by the protocol analyzer by looking at the Token Length field of he CoAP header.

* **FP**: an integer specifying the position in the header of the field this Field Description applies to. The default value is 1. For each recurrence of the same field in the header, the value is increased by 1.
* **DI**: tells the direction to which this Field Description applies:

    * *Up*: only to uplink messages (i.e. from device to network)
    * *Dw*: only to downlink messages (i.e. from network to device)
    * *Bi*: to both directions

* **TV**: specifies the Target Value. The value is a number, a string or an array of these types. The "TV" key can be omitted or its value set to null if there is no value to check, for instance together with the "ignore" MO. If the Target Value is an array, then the value null among the array elements indicates that \
the Field Descriptor matches the case where the field is not present in the header being compressed.
* **MO**: specifies the Matching Operator. It is a string that can take the following values:

  * *ignore*: the field must be present in the header, but the value is not checked.
  * *equal*: type and value must check between the field value and the Target Value <<< il y a des champs avec des descriptions explicites de type dans les protocoles considérés ? >>
  * *MSB*: the most significant bits of the Target Value are checked against the most significant bits of the field value. The number of bits to be checked is given by the "MOa" field.
  * *match-mapping*: with this MO, the Target Value must be an array. This MO matches when one element of the Target Value array matches the field, in type and value.

* **MOa**: specifies, if applicable, an argument to the MO. This currently only applies to the "MSB" MO, where the argument specifies the length of the matching, in bits.
* **CDA**: designates the Compression/Decompression Action. It is a string that can take the following values:

   * *not-sent*: the field value is not sent as a residue.
   * *value-sent*: the field value is sent in extenso in the residue.
   * *LSB*: the bits remaining after the MSB comparison are sent in the residue.
   * *mapping-sent*: the index of the matching element in the array is sent.
   * *compute*: the field is not sent in the residue and the receiver knows how to recover the value from other information. This is generally used for length and checksum.

* **CDAa**: represents the argument of the CDA. Currently, no CDAa is defined.

For example::

  {
    "ruleID": 12,
    "ruleLength": 4,
    "compression": [
      {"FID": "IPV6.VER", "FL": 4, "FP": 1, "DI": "Bi", "TV": 6, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.TC",  "FL": 8, "FP": 1, "DI": "Bi", "TV": 0, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.FL",  "FL": 20,"FP": 1, "DI": "Bi", "TV": 0, "MO": "ignore","CDA": "not-sent"},
      {"FID": "IPV6.LEN", "FL": 16,"FP": 1, "DI": "Bi",          "MO": "ignore","CDA": "compute-length"},
      {"FID": "IPV6.NXT", "FL": 8, "FP": 1, "DI": "Bi", "TV": 58, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.HOP_LMT","FL": 8,"FP": 1,"DI": "Bi","TV": 255,"MO": "ignore","CDA": "not-sent"},
      {"FID": "IPV6.DEV_PREFIX","FL": 64,"FP": 1,"DI": "Bi","TV": ["2001:db8::/64",
                                                                   "fe80::/64",
                                                                   "2001:0420:c0dc:1002::/64" ],
                                                                  "MO": "match-mapping","CDA": "mapping-sent","SB": 1},
      {"FID": "IPV6.DEV_IID","FL": 64,"FP": 1,"DI": "Bi","TV": "::79","MO": "equal","CDA": "DEVIID"},
      {"FID": "IPV6.APP_PREFIX","FL": 64,"FP": 1,"DI": "Bi","TV": [ "2001:db8:1::/64",
                                                                    "fe80::/64",
                                                                    "2404:6800:4004:818::/64" ],
                                                                  "MO": "match-mapping","CDA": "mapping-sent", "SB": 2},
      {"FID": "IPV6.APP_IID","FL": 64,"FP": 1,"DI": "Bi","TV": "::2004","MO": "equal","CDA": "not-sent"},
      {"FID": "ICMPV6.TYPE","FL": 8,"FP": 1,"DI": "Bi","TV": 128,"MO": "equal","CDA": "not-sent"},
      {"FID": "ICMPV6.CODE","FL": 8,"FP": 1,"DI": "Bi","TV": 0,  "MO": "equal","CDA": "not-sent"},
      {"FID": "ICMPV6.CKSUM","FL": 16,"FP": 1,"DI": "Bi","TV": 0,"MO": "ignore","CDA": "compute-checksum"},
      {"FID": "ICMPV6.IDENT","FL": 16,"FP": 1,"DI": "Bi","TV": [],"MO": "ignore","CDA": "value-sent"},
      {"FID": "ICMPV6.SEQNB","FL": 16,"FP": 1,"DI": "Bi","TV": [],"MO": "ignore","CDA": "value-sent"}
    ]
  }


Fragmentation Rules
-------------------

Fragmentation rules define how the compression and decompression must be performed.

The keyword  **Fragmentation** is followed by a dictionnary containing the different parameters used.
Inside the keyword **FRMode** indicates which Fragmentation mode is used (**NoAck**, **AckAlways**, **AckOnError**).
**FRDirection** give the direction of the fragmentation rule. **UP** means that data fragments are sent by the device,
**DW** for the opposite direction. This entry is mandatory.
Then the keyword **FRModeProfiler** gives the information needed to create the SCHC fragmentation header and mode profile:

* **dtagSize** gives in bit the size of the dtag field. <<if not present or set to 0, this field is not present \
in the SCHC fragmentation header>>. This keyword can be used by all the fragmentation modes.
* **WSize** gives in bit the size of Window field. If not present, the default value is 0 (no window) in \
NoAck and 1 in AckAlways. In ackOnErr this field must be set to 1 or to an higher value.
* **FCNSize** gives in bit the size of the FCN field. If not present, by default, the value is 1 for NoAck.\
For AckAlways and AckOnError the value must be specified.
* **ackBehavior** this keyword specifies on AckOnError, when the fragmenter except to receive a bitmap from the reassembler:

    * *afterAll1*: the bitmap (or RCS OK) is expected only after the reception of a All-1.
    * *afterAll0*: the bitmap may be expected after the transmission of the window last fragment (All-0 or All-1)

* **lastTileInAll1**: true to append last tile to the All-1 message, false otherwise.
* **tileSize** gives the size in bit of a tile.
* **MICAlgorithm** gives the algorithm used to compute the MIB, by default **RCS_RFC8724** (e.g. crc32),
* **MICWordSize** gives the size of the RCS word.
* **maxRetry** indicates to the sender how many time a fragment or ack request can be sent.
* **timeout** indicated in seconds to the sender how many time between two retransmissions. The receiver can compute the delay before aborting.

For instance::

    {
        "RuleID": 1,
        "RuleLength": 3,
        "Fragmentation" : {
            "FRMode": "AckOnError",
            "FRDirection": "UP",
            "FRModeProfile": {
                "dtagSize": 2,
                "WSize": 5,
                "FCNSize": 3,
                "ackBehavior": "afterAll1",
                "tileSize": 9,
                "MICAlgorithm": "RCS_RFC8724",
                "MICWordSize": 8,
                "maxRetry": 4,
                "timeout": 600,
                "lastTileInAll1": false
            }
        }
    }

-------
Context
-------

A context is associated with a specific device, which may be identified by a unique LPWAN
identifier, for instance a LoRaWAN devEUI.

The context also includes a set of rules. The rule description is defined [above](#rule-definition)::


    [
        {
            "DeviceID": 0x1234567890,
            "SoR" : [ ..... ]
        },
        {
            "DeviceID": 0xDEADBEEF,
            "SoR" : [ ..... ]
        },
        ...
    ]

DeviceID is a numerical value that must be unique in the context. If the context is used on a device, the deviceID may be omitted or set to null. In the core network, the DeviceIDs must be specified.

The set of rules itself expands as shown below::

    [
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
    ]



Remove
------

Suppresses a rule for a specific device <<< only one, or a set of rules? >>>. If no rule is specified, all rules for that device are removed from the context::

      RM.remove ({"DeviceID": 0x1234567, "SoR": {{"ruleID":12, "ruleLength":4}}})
      RM.remove ({"DeviceID": 0x1234567})

FindRuleFromPacket
------------------

This method returns a rule and a DeviceID that match a packet description given by the protocol analyzer.

FindFragmentationRule (size)
----------------------------

Returns a fragmentation rule compatible with the packet size passed as parameter.


FindRuleFromID
--------------

Given the first bits received from the LPWAN, returns either a fragmentation or a compression rule.


"""

#from multiprocessing import Value
from operator import mod
from gen_base_import import *
from copy import deepcopy
from compr_core import *
import ipaddress
import warnings

import base64

import base64

"""
.. module:: gen_rulemanager
   :platform: Python, Micropython
   :synopsis: This module is used to manage rules.
"""

# XXX to be checked whether they are needed.
DEFAULT_FRAGMENT_RID = 1
DEFAULT_L2_SIZE = 8
DEFAULT_RECV_BUFSIZE = 512
DEFAULT_TIMER_T1 = 5
DEFAULT_TIMER_T2 = 10
DEFAULT_TIMER_T3 = 10
DEFAULT_TIMER_T4 = 12
DEFAULT_TIMER_T5 = 14

# CONTAINS DEFAULT AND USEFUL INFORMATION ON FIELDS

class IPv6address:
    addr = b''

FIELD__DEFAULT_PROPERTY = {
    T_IPV6_VER             : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    T_IPV6_TC              : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_FL              : {"FL": 20, "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_NXT             : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_HOP_LMT         : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_LEN             : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_IPV6_DEV_PREFIX      : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"   },
    T_IPV6_DEV_IID         : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"  },
    T_IPV6_APP_PREFIX      : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"   },
    T_IPV6_APP_IID         : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"   },
    T_UDP_DEV_PORT         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_UDP_APP_PORT         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_UDP_LEN              : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_UDP_CKSUM            : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_ICMPV6_TYPE          : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_CODE          : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_CKSUM         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_IDENT         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_SEQNO         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_VERSION         : {"FL": 2,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TYPE            : {"FL": 2,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TKL             : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_CODE            : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_MID             : {"FL": 16,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TOKEN           : {"FL": "tkl",  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_OPT_URI_PATH    : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION" },
    T_COAP_OPT_CONT_FORMAT : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},
    T_COAP_OPT_CONT_FORMAT : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},
    T_COAP_OPT_NO_RESP     : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION"}
}
# XXX T_COAP_OPT_END is not in FIELD__DEFAULT_PROPERTY, but T_COAP_OPT_END is still generated by the parrser

class DictToAttrDeep:

    def __init__(self, **entries):
        self.__update(**entries)

    def __update(self, **entries):
        for k,v in entries.items():
            if isinstance(v, dict):
                setattr(self, k, DictToAttrDeep(**v))
            else:
                setattr(self, k, v)

    def __contains__(self, t):
        """ t in this """
        for k,v in self.__dict__.items():
            if k == t:
                return True
            if isinstance(v, DictToAttrDeep):
                if t in v:
                    return True

    def __getitem__(self, t):
        """ this[k] """
        for k,v in self.__dict__.items():
            if k == t:
                return v
            if isinstance(v, DictToAttrDeep):
                if t in v:
                    return v[t]

    def get(self, k, d=None):
        """ this.get(k) """
        if k not in self:
            return d
        return self.__getitem__(k)

    def __repr__(self):
        return "{{{}}}".format(str(", ".join(
                ['"{}": {}'.format(k,self.__reprx(v))
                 for k,v in self.__dict__.items()])))

    def __reprx(self, t):
        if isinstance(t, str):
            return '"{}"'.format(t)
        elif isinstance(t, dict):
            return "{{{}}}".format(str(", ".join(
                    ['"{}": {}'.format(k,self.__reprx(v))
                     for k,v in t.items()])))
        elif isinstance(t, list):
            return "[{}]".format(str(", ".join(
                    ["{}".format(self.__reprx(i)) for i in t])))
        else:
            return repr(t)

class RuleManager:
    """
    # Class RuleManager

    A RuleManager object is created this way:

          from RuleManager import *

          RM = RuleManager()

          arguments:

          - file: the RuleManager takes a file to upload rule_set
          - log:  display debugging events

    """

    def _return_default(self, elm, idx, val):
        if idx in elm:
            return elm[idx]
        else:
            return val

    def Add(self, device=None, dev_info=None, file=None, compression=True):
        """
        Add is used to add a new rule or a set of rules to a context. Add checks the validity of the rule:

        * ruleID/RuleIDLength do not overlap
        * the rule contains either one of a fragmentation and a compression description.

        If the DeviceID already exists in the context, the new rule is added to that context, providing no conflict on the RuleID is found.

              RM.Add ({"DeviceID": 0x1234567, "sor": {.....}})

        """

        assert (dev_info is not None or file is not None)

        if file != None:
            dev_info = json.loads(open(file).read())

        if type(dev_info) is dict: #Context or Rules
            if T_RULEID in dev_info: # Rules
                sor = [dev_info]
            elif "SoR" in dev_info:
                if "DeviceID" in dev_info:
                    device = dev_info["DeviceID"]
                sor = dev_info["SoR"]
            else:
                raise ValueError("unknown format")
        elif type(dev_info) is list: # a Set of Rule
            sor = dev_info
        else:
            raise ValueError("unknown structure")

        # check nature of the info: if "SoR" => device context, if "RuleID" => rule

        d = None
        for d in self._ctxt:
            if device == d["DeviceID"]:
                break
        else:
            d = {"DeviceID": device, "SoR": [], "Indexes" : {}}
            self._ctxt.append(d)

        for n_rule in sor:
            n_ruleID = n_rule[T_RULEID]
            n_ruleLength = n_rule[T_RULEIDLENGTH]
            left_aligned_n_ruleID = n_ruleID << (32 - n_ruleLength)

            overlap = False
            for e_rule in d["SoR"]: # check no overlaps on RuleID
                left_aligned_e_ruleID = e_rule[T_RULEID] << (32 - e_rule[T_RULEIDLENGTH])
                if left_aligned_e_ruleID == left_aligned_n_ruleID:
                    dprint ("Warning; Rule {}/{} exists not inserted".format(bin(n_ruleID), n_ruleLength) )
                    overlap = True
                    break

            if not overlap:
                if T_COMP in n_rule:
                    r = self._create_compression_rule(n_rule, device)
                    d["SoR"].append(r)
                elif T_FRAG in n_rule:
                    r = self._create_fragmentation_rule(n_rule)
                    d["SoR"].append(r)
                elif T_NO_COMP in n_rule:
                    already_exists = self.FindNoCompressionRule(deviceID=device)
                    if already_exists == None:
                        arule = {}
                        arule[T_RULEID] = n_rule[T_RULEID]
                        arule[T_RULEIDLENGTH] = n_rule[T_RULEIDLENGTH]
                        arule[T_NO_COMP] = []
                        d["SoR"].append(arule)
                    else:
                        print ("Warning 'no compression' rule already exists")
                else:
                    raise ValueError ("Rule type undefined")
                print (n_rule)

        if T_INDEXES in dev_info:
            print ("%",dev_info[T_INDEXES])
            for x, v in dev_info[T_INDEXES].items():
                print (x)
                d["Indexes"] |= {x:v}

    def _adapt_value (self, FID, value, allow_dict=False):
        if FIELD__DEFAULT_PROPERTY[FID]["TYPE"] is int:
            if type(value) != int:
                raise ValueError ("{} TV type not appropriate for field {}".format(value, FID))
            else:
                return value
        if FIELD__DEFAULT_PROPERTY[FID]["TYPE"] is str:
            if type(value) != str:
                raise ValueError ("{} TV type not appropriate for field {}".format(value, FID))
            else:
                return value
        if FIELD__DEFAULT_PROPERTY[FID]["TYPE"] is bytes: # convert string with IPv6 address to bytes
            if type(value) is str:
                slash_pos = value.find("/")
                if slash_pos != -1:
                    # a prefix is given, remove / to be compatible with ip_address
                    value = value[:slash_pos]

                addr = ipaddress.ip_address(value)
                if addr.version != 6: # expect an IPv6 address
                    raise ValueError ("only IPv6 is supported, can not support {}".format(addr.version))

                if FID in [T_IPV6_DEV_PREFIX, T_IPV6_APP_PREFIX]: #prefix top 8
                    return addr.packed[:8]
                elif FID in [T_IPV6_DEV_IID, T_IPV6_APP_IID]: #IID bottom 8
                    return addr.packed[8:]
                else:
                    raise ValueError ("{} Fid not found".format(FID))
            elif type(value) is int:
                return (value).to_bytes(8, byteorder="big")

        if allow_dict: # TV can contain a dict to code functions
            return value

    def _create_fragmentation_rule (self, nrule):
        arule = {}

        arule[T_RULEID] = nrule[T_RULEID]
        arule[T_RULEIDLENGTH] = nrule[T_RULEIDLENGTH]
        arule["Fragmentation"] = {}

        def _default_value (ar, nr, idx, default=None, failed=False):
            if failed and not idx in nr[T_FRAG][T_FRAG_PROF]:
                raise ValueError ("{} not found".format(idx))

            if not T_FRAG_PROF in nr[T_FRAG] or not idx in nr[T_FRAG][T_FRAG_PROF]:
                ar[T_FRAG][T_FRAG_PROF][idx] = default
            else:
                ar[T_FRAG][T_FRAG_PROF][idx] = nr[T_FRAG][T_FRAG_PROF][idx]

        if not T_FRAG_DIRECTION in nrule[T_FRAG]:
            raise ValueError ("Keyword {} must be specified with {} or {}".format(T_FRAG_DIRECTION, T_DIR_UP, T_DIR_DW))

        if not nrule[T_FRAG][T_FRAG_DIRECTION] in [T_DIR_UP, T_DIR_DW]:
            raise ValueError ("Keyword {} must be {} or {}".format(T_FRAG_DIRECTION, T_DIR_UP, T_DIR_DW))

        arule[T_FRAG][T_FRAG_DIRECTION] = nrule[T_FRAG][T_FRAG_DIRECTION] 


        if  T_FRAG_MODE in nrule[T_FRAG]:
            if not T_FRAG_PROF in nrule[T_FRAG]:
                arule[T_FRAG][T_FRAG_MODE] = {}

            if nrule[T_FRAG][T_FRAG_MODE] in [T_FRAG_NO_ACK, T_FRAG_ACK_ALWAYS, T_FRAG_ACK_ON_ERROR]:
                arule[T_FRAG][T_FRAG_MODE] = nrule[T_FRAG][T_FRAG_MODE]
                arule[T_FRAG][T_FRAG_PROF] ={}

                _default_value (arule, nrule, T_FRAG_FCN)
                _default_value (arule, nrule, T_FRAG_DTAG, 0)
                _default_value (arule, nrule, T_FRAG_MIC, T_FRAG_RFC8724)

                if nrule[T_FRAG][T_FRAG_MODE] == T_FRAG_NO_ACK:
                    _default_value(arule, nrule, T_FRAG_DTAG, 2)
                    _default_value (arule, nrule, T_FRAG_W, 0)
                    _default_value (arule, nrule, T_FRAG_FCN, 3)
                    _default_value(arule, nrule, T_FRAG_L2WORDSIZE, 8)
                elif nrule[T_FRAG][T_FRAG_MODE] == T_FRAG_ACK_ALWAYS:
                    _default_value (arule, nrule, T_FRAG_W, 1)
                    _default_value(arule, nrule, T_FRAG_L2WORDSIZE, 8)
                elif  nrule[T_FRAG][T_FRAG_MODE] == T_FRAG_ACK_ON_ERROR:
                    if not T_FRAG_FCN in nrule[T_FRAG][T_FRAG_PROF]:
                        raise ValueError ("FCN Must be specified for Ack On Error")

                    _default_value (arule, nrule, T_FRAG_W, 1)
                    _default_value (arule, nrule, T_FRAG_ACK_BEHAVIOR, "afterAll1")
                    _default_value (arule, nrule, T_FRAG_TILE, None, True)
                    _default_value (arule, nrule, T_FRAG_MAX_RETRY, 4)
                    _default_value (arule, nrule, T_FRAG_TIMEOUT, 600)
                    _default_value (arule, nrule, T_FRAG_L2WORDSIZE, 8)
                    _default_value (arule, nrule, T_FRAG_LAST_TILE_IN_ALL1, None, True)

                    if nrule[T_FRAG][T_FRAG_PROF][T_FRAG_LAST_TILE_IN_ALL1] == True:
                        raise NotImplementedError ("Last tile in All-1 is not implemented yet")

                # the size include All-*, Max_VLAUE is WINDOW_SIZE-1
                _default_value(arule, nrule, T_FRAG_WINDOW_SIZE, (0x01 <<(arule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN]))-1)
            else:
                raise ValueError ("Unknown fragmentation mode", nrule[T_FRAG][T_FRAG_MODE])
        else:
            raise ValueError("No fragmentation mode")

        return arule

    def _create_compression_rule (self, nrule, device_id = None):
        """
        parse a rule to verify values and fill defaults
        """
        arule = {}

        arule[T_RULEID] = nrule[T_RULEID]
        arule[T_RULEIDLENGTH] = nrule[T_RULEIDLENGTH]

        if T_ACTION in nrule:
             print ("Warning: using experimental Action")
             arule[T_ACTION] = nrule[T_ACTION]


        arule[T_COMP] = []

        up_rules = 0
        dw_rules = 0

        for r in nrule[T_COMP]:
            if r["FID"] == T_COAP_OPT_END:
                # XXX: check ignoring is the proper behavior, or what should be done the T_COAP_OPT_END
                # which is still generated by the parser but was not handled by this code.
                warnings.warn("Note: T_COAP_OPT_END is ignored")
                continue
            if not r["FID"] in FIELD__DEFAULT_PROPERTY:
                raise ValueError( "Unkwown field id {} in rule {}/{}".format(
                    r["FID"], arule[T_RULEID],  arule[T_RULEIDLENGTH]
                ))

            entry = {}
            FID = r[T_FID]
            entry[T_FID] = FID
            entry[T_FL] = self._return_default(r, T_FL, FIELD__DEFAULT_PROPERTY[FID][T_FL])
            entry[T_FP] = self._return_default(r, T_FP, 1)
            entry[T_DI] = self._return_default(r, T_DI, T_DIR_BI)
            if entry[T_DI] in [T_DIR_BI, T_DIR_UP]: up_rules += 1
            if entry[T_DI] in [T_DIR_BI, T_DIR_DW]: dw_rules += 1

            MO = r[T_MO].upper()
            if MO in [T_MO_EQUAL, T_MO_MSB, T_MO_IGNORE]:
                if MO == T_MO_MSB:
                    if T_MO_VAL in r:
                        entry[T_MO_VAL] = r[T_MO_VAL]
                    else:
                        raise ValueError ("MO Value missing for {}".format(FID))

                if T_TV in  r:
                    if type(r[T_TV]) is dict:
                        if len(r[T_TV]) != 1:
                            raise ValueError(FID+": Only one command for TV.")

                        if  not list(r[T_TV])[0] in [T_CMD_INDIRECT]:
                            raise ValueError(FID+": Unknown TV command.")

                        dic = r[T_TV] # set value to bytearray
                        key = next(iter(dic))
                        val = list(dic.values())[0]


                        print ("---------> ", key, val)

                    entry[T_TV] = self._adapt_value(FID, r[T_TV], allow_dict=True)
                else:
                    entry[T_TV] = None

            elif MO == T_MO_MMAP:
                entry[T_TV] = []
                for e in r[T_TV]:
                    entry[T_TV].append(self._adapt_value(FID, e))

            else:
                raise ValueError("{} MO unknown".format(MO))
            entry[T_MO] = MO

            CDA = r[T_CDA].upper()
            if not CDA in [T_CDA_NOT_SENT, T_CDA_VAL_SENT, T_CDA_MAP_SENT, T_CDA_LSB, T_CDA_COMP_LEN, T_CDA_COMP_CKSUM, T_CDA_DEVIID, T_CDA_APPIID]:
                raise ValueError("{} CDA not found".format(CDA))
            entry[T_CDA] = CDA

            arule[T_COMP].append(entry)

        if not T_META in arule:
            arule[T_META] = {}
        arule[T_META][T_UP_RULES] = up_rules
        arule[T_META][T_DW_RULES] = dw_rules
        arule[T_META][T_DEVICEID] = device_id

        return arule


    def __init__(self, file=None, log=None):
        #RM database
        self._ctxt = []
        self._log = log
        self._db = []
        self._sid_info = []


    def _smart_print(self, v):
        if type(v) is str:
            v = '"'+v+'"'
            print ('{:<30}'.format(v), end="")
        elif type(v) is int:
            print ('{:>30}'.format(v), end="")
        elif type(v) is bytes:
            print ('{:>30}'.format(v.hex()), end="")

    def printBin(self, v, l):
        txt = ""
        for i in range (7, -1, -1):
            if i >= l: txt += " "
            elif v & (0x01 << i) == 0: txt += "0"
            else: txt += "1"
        return txt

    def Print (self):
        """
        Print a context
        """
        for dev in self._ctxt:
            print ("*"*40)
            print ("Device:", dev["DeviceID"])

            for rule in dev["SoR"]:
                print ("/" + "-"*25 + "\\")
                txt = str(rule[T_RULEID])+"/"+ str(rule[T_RULEIDLENGTH])
                print ("|Rule {:8}  {:10}|".format(txt, self.printBin(rule[T_RULEID], rule[T_RULEIDLENGTH])))

                if T_COMP in rule:
                    print ("|" + "-"*15 + "+" + "-"*3 + "+" + "-"*2 + "+" + "-"*2 + "+" + "-"*30 + "+" + "-"*13 + "+" + "-"*16 +"\\")
                    for e in rule[T_COMP]:
                        print ("|{:<15s}|{:>3}|{:2}|{:2}|".format(e[T_FID], e[T_FL], e[T_FP], e[T_DI]), end='')
                        if 'TV' in e:
                            if type(e[T_TV]) is list:
                                self._smart_print(e[T_TV][0])
                            elif type(e[T_TV]) is dict:
                                self._smart_print(list(e[T_TV])[0]+'('+list(e[T_TV].values())[0]+')' )
                            else:
                                self._smart_print(e[T_TV])
                        if not T_TV in e or e[T_TV] == None:
                            print ("-"*30, end="")

                        txt = e[T_MO]
                        if T_MO_VAL in e:
                            txt = txt+ '(' + str(e[T_MO_VAL])+')'

                        print ("|{:13}|{:16}|".format(txt, e[T_CDA]))

                        if (T_TV in e) and (type (e[T_TV]) is list):
                            for i in range (1, len(e[T_TV])):
                                print (":{:^15s}:{:^3}:{:^2}:{:^2}:".format(".", ".", ".","."), end='')
                                self._smart_print(e[T_TV][i])
                                print (":{:^13}:{:^16}:".format(".", "."))


                    print ("\\" + "-"*15 + "+" + "-"*3 + "+" + "-"*2 + "+" + "-"*2 + "+" + "-"*30 + "+" + "-"*13 + "+" + "-"*16 +"/")
                elif T_FRAG in rule:
                    # print (rule)
                    if rule[T_FRAG][T_FRAG_DIRECTION] == T_DIR_UP:
                        dir_c = "^"
                    else:
                        dir_c = "v"

                    print ("!" + "="*25 + "+" + "="*61 +"\\")
                    print ("!{} Fragmentation mode : {:<8} header dtag{:2} Window {:2} FCN {:2} {:20}{:2} {}!"
                        .format(
                            dir_c,
                            rule[T_FRAG][T_FRAG_MODE],
                            rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG],
                            rule[T_FRAG][T_FRAG_PROF][T_FRAG_W],
                            rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                            "",
                            rule[T_FRAG][T_FRAG_DIRECTION],
                            dir_c
                        ))

                    if T_FRAG_TILE in rule[T_FRAG][T_FRAG_PROF]:
                        txt = "Tile size: "+ str(rule[T_FRAG][T_FRAG_PROF][T_FRAG_TILE])
                    else:
                        txt = "No Tile size specified"
                    print ("!{} {:<84}{}!".format(dir_c, txt, dir_c))


                    print ("!{} RCS Algorithm: {:<69}{}!".format(dir_c,rule[T_FRAG][T_FRAG_PROF][T_FRAG_MIC], dir_c))

                    if rule[T_FRAG][T_FRAG_MODE] != T_FRAG_NO_ACK:
                        print ("!{0}" + "-"*85 +"{0}!".format(dir_c))
                        if  rule[T_FRAG][T_FRAG_MODE] == T_FRAG_ACK_ON_ERROR:
                            txt = "Ack behavior: "+ rule[T_FRAG][T_FRAG_PROF][T_FRAG_ACK_BEHAVIOR]
                            print ("!{} {:<84}{}!".format(dir_c, txt, dir_c))

                        print ("!{} Max Retry : {:4}   Timeout {:5} seconds {:42} {}!".format(
                            dir_c,
                            rule[T_FRAG][T_FRAG_PROF][T_FRAG_MAX_RETRY],
                            rule[T_FRAG][T_FRAG_PROF][T_FRAG_TIMEOUT], "",
                            dir_c
                        ))

                    print ("\\" + "="*87 +"/")
                elif T_NO_COMP in rule:
                    print ("NO COMPRESSION RULE")
            if T_INDEXES in dev and len(dev[T_INDEXES]) > 0:
                print ("INDEXES:")
                for x, y in dev[T_INDEXES].items():
                    print (x,"-->", y)

    def to_yang (self, format="json"):
        """
        Print a context
        """

        for dev in self._ctxt:
            print ("*"*40)
            print ("Device:", dev["DeviceID"])

            yang_rules = []
            for rule in dev["SoR"]:
                #txt = str(rule[T_RULEID])+"/"+ str(rule[T_RULEIDLENGTH])
                if T_COMP in rule:
                    yang_comp = []
                    for e in rule[T_COMP]:

                        l = e[T_FL]
                        if type(l) == int:
                            yang_length = str(l)
                        else: # function
                            yang_length = YANG_ID[l][1]

                        yang_entry = {
                            "field-id" : YANG_ID[e[T_FID]][1],
                            "field-length" : yang_length,
                            "field-position" : e[T_FP],
                            "direction-indicator" : YANG_ID[e[T_DI]][1],
                            "matching-operator" : YANG_ID[e[T_MO]][1],
                            "comp-decomp-action" : YANG_ID[e[T_CDA]][1]
                        }

                        def dictify (val):
                            dictio = []
                            if type(val) != list:
                                val =[val]

                            for i in range(len(val)):
                                if type(val[i]) == int:
                                    # find length in byte
                                    x = val[i]
                                    size = 1
                                    while x !=0:
                                        x >>= 8
                                        size +=1

                                    b_a = val[i].to_bytes(size, byteorder="big")
                                    v = base64.b64encode(b_a).decode()
                                    dictio.append ({"index" : i, "value": v})
                                elif type(val[i]) == bytes:
                                    v = base64.b64encode(val[i]).decode()
                                    dictio.append ({"index" : i, "value": v})                                    

                                else: 
                                    print ("unkown type", type(val[i]))
                                    v = ""

                            print ("#####", dictio)
                            return dictio

                        if T_TV in e and e[T_TV] != None:
                            yang_entry["target-value"] = dictify(e[T_TV])

                        if T_MO_VAL in e and e[T_MO_VAL] != None:
                            yang_entry["matching-operator-value"] = dictify(e[T_MO_VAL])

                        # if T_CDA_VAL in e and e[T_CDA_VAL] != None:
                        #     yang_entry.append({"comp-decomp-action-value": dictify(e[T_CDA_VAL])})
                        
                        print (yang_entry)
                        yang_comp.append(yang_entry)
                    yang_rules.append({
                        "rule-id-value": rule[T_RULEID],
                        "rule-id-length": rule[T_RULEIDLENGTH],
                        "rule-nature" : "nature-compression",
                        "entry" : yang_comp
                    })

                elif T_FRAG in rule:
                    frag_rule = {
                        "rule-id-value": rule[T_RULEID],
                        "rule-id-length": rule[T_RULEIDLENGTH],     
                        "rule-nature" : "nature-fragmentation",                   
                        "direction" : YANG_ID[rule[T_FRAG][T_FRAG_DIRECTION]][1],
                        "rcs-algorithm" : YANG_ID[rule[T_FRAG][T_FRAG_PROF][T_FRAG_MIC]][1],
                        "dtag-size" : rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG],
                        "fcn-size" : rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN],
                        "fragmentation-mode" : YANG_ID[rule[T_FRAG][T_FRAG_MODE]][1]
                    }
                    if rule[T_FRAG][T_FRAG_MODE] in [T_FRAG_ACK_ALWAYS, T_FRAG_ACK_ON_ERROR]:
                        frag_rule.append({"w-size" : rule[T_FRAG][T_FRAG_PROF][T_FRAG_W]})


                    yang_rules.append(frag_rule)

                   
                elif T_NO_COMP in rule:
                    print ("NO COMPRESSION RULE")
                    yang_rules.append({
                        "rule-id-value": rule[T_RULEID],
                        "rule-id-length": rule[T_RULEIDLENGTH],
                        "rule-nature" : "nature-no-compression"
                    })
 
            print ("#", yang_rules)
        
        return {"ietf-schc:schc" : {"rule" : yang_rules}}

    def add_sid_file(self, name):
        with open(name) as sid_file:
            sid_values = json.loads(sid_file.read())

        self._sid_info.append(sid_values)

    def sid_search_for(self, name, space="data"):

        for s in self._sid_info:
            for e in s["items"]:
                if e["identifier"] == name and e["namespace"]==space:
                    return e["sid"]

        return None 

    def cbor_header (self, major, value):
        if value < 23:
            return struct.pack ('!B', (major | value))
        elif value < 255:
            return struct.pack ('!BB', (major | 24),  value)

 

    def to_yang_coreconf (self, format="json"):
        import cbor2 as cbor
        import binascii
        """
        Print a context
        """
        module_sid = self.sid_search_for(name="/ietf-schc:schc", space="data")
        print (module_sid)
        rule_sid = self.sid_search_for(name="/ietf-schc:schc/rule", space="data")
        print (rule_sid, rule_sid-module_sid)


        for dev in self._ctxt:
            print ("*"*40)
            print ("Device:", dev["DeviceID"])

            rule_count = 0
            full_rules = b''
            for rule in dev["SoR"]:
                rule_count += 1
                if T_COMP in rule:
                    print ("comp")
                    entry_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry", space="data")
                
                    nb_entry = 0
                    rule_content = b''
                    for e in rule[T_COMP]:
                        print ('>>>', e)
                        nb_elm = 0
                        nb_entry += 1

                        entry_cbor = \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-id", space="data") - entry_sid) + \
                            cbor.dumps(self.sid_search_for(name=YANG_ID[e[T_FID]][1], space="identity")) 
                        nb_elm += 1

                        l=e[T_FL]
                        print (l, type(l))
                        if type(l) == int:
                            entry_cbor += \
                                cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-length", space="data") - entry_sid) + \
                                cbor.dumps(l)
                        elif type(l) == str:
                            raise ValueError("Field ID not defined")
                        else:
                            raise ValueError("unknown field length value")
                        nb_elm += 1

                        entry_cbor += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-position", space="data") - entry_sid) + \
                            struct.pack('!B', e[T_FP])
                        nb_elm += 1
  
                        entry_cbor += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/direction-indicator", space="data") - entry_sid) + \
                            cbor.dumps(self.sid_search_for(name=YANG_ID[e[T_DI]][1], space="identity")) 
                        nb_elm += 1

                        entry_cbor += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/matching-operator", space="data") - entry_sid) + \
                            cbor.dumps(self.sid_search_for(name=YANG_ID[e[T_MO]][1], space="identity")) 
                        nb_elm += 1

                        entry_cbor += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/comp-decomp-action", space="data") - entry_sid) + \
                            cbor.dumps(self.sid_search_for(name=YANG_ID[e[T_CDA]][1], space="identity")) 
                        nb_elm += 1

                        def dictify_cbor (val, ref_id):
                                cbor_data = b''
                                if type(val) != list:
                                    val = [val]

                                tv_array = b''
                                for i in range(len(val)):

                                    if type(val[i]) is int:
                                        x = val[i]
                                        r = b''
                                        while x != 0:
                                            r = struct.pack('!B', x&0xFF) + r
                                            x >>= 8
                                    elif type(val[i]) is bytes:
                                        r = val[i]
                                    elif type(val[i]) is dict:
                                        print ("List")
                                        r = val[i]
                                    else:
                                        raise ValueError("TV type is not covered")

                                    if type(r) is bytes:
                                        tv_array += b'\xA2' + \
                                            cbor.dumps(self.sid_search_for(name=ref_id+"/index", space="data") - self.sid_search_for(name=ref_id, space="data")) + \
                                            struct.pack('!B', i)

                                        tv_array +=  \
                                            cbor.dumps(self.sid_search_for(name=ref_id+"/value", space="data") - self.sid_search_for(name=ref_id, space="data")) + \
                                            cbor.dumps(r)
                                    elif type(r) is dict:
                                        tv_array += b'\xA3' + \
                                            cbor.dumps(self.sid_search_for(name=ref_id+"/index", space="data") - self.sid_search_for(name=ref_id, space="data")) + \
                                            struct.pack('!B', i)

                                        tv_array +=  \
                                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/target-value/ietf-schc-indirect-values:operator", space="data") - \
                                                        self.sid_search_for(name=ref_id, space="data")) + \
                                            cbor.dumps(self.sid_search_for(name=YANG_ID[next(iter(r))][1], space="identity"))

                                        op_val = list(r.values())[0]

                                        tv_array +=  \
                                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/target-value/ietf-schc-indirect-values:operator-index", space="data") - \
                                                        self.sid_search_for(name=ref_id, space="data")) + \
                                            cbor.dumps(op_val)
                                    else:
                                        raise ValueError("TV type is unknown")


                                tv_array = self.cbor_header(0b100_00000, len(val)) + tv_array
                                return tv_array


                        if T_TV in e and e[T_TV] != None:
                            tv_cbor = dictify_cbor(e[T_TV], "/ietf-schc:schc/rule/entry/target-value")

                            entry_cbor += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/target-value", space="data") - entry_sid) + \
                            tv_cbor
                            nb_elm += 1
 
                        entry_cbor = self.cbor_header (0b101_00000, nb_elm) + entry_cbor # header MAP and size
                        print (binascii.hexlify(entry_cbor))
                        rule_content += entry_cbor

                    rule_content = b'\xA4' + \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry", space="data") - rule_sid) + \
                        self.cbor_header(0b100_00000, nb_entry) + rule_content + \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-value", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEID]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-length", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEIDLENGTH])+\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-nature", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name="nature-compression", space="identity"))                                               

                elif T_FRAG in rule:
                    print ("frag")
                    nb_elm = 3
                    rule_content = \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-value", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEID]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-length", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEIDLENGTH])+\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-nature", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name="nature-fragmentation", space="identity"))                                               


                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/direction", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name=YANG_ID[rule[T_FRAG][T_FRAG_DIRECTION]][1], space="identity")) 
                    nb_elm += 1
 

                    #/!\ since there is a defult value should be skipped when value is rcs-crc32
                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rcs-algorithm", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name=YANG_ID[rule[T_FRAG][T_FRAG_PROF][T_FRAG_MIC]][1], space="identity")) 
                    nb_elm += 1

                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/dtag-size", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG])
                    nb_elm += 1

                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/fcn-size", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN])
                    nb_elm += 1

                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/fragmentation-mode", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name= YANG_ID[rule[T_FRAG][T_FRAG_MODE]][1], space="identity")) 
                    nb_elm += 1



                    
                    rule_content = self.cbor_header(0b101_00000, nb_elm) + rule_content
                elif T_NO_COMP in rule:
                        rule_content = b'\xA3' + \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-value", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEID]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-length", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEIDLENGTH])+\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-nature", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name="nature-no-compression", space="identity"))                     
                        print ("no comp")
                else:
                    raise ValueError("unkwon rule")

                print ("####", binascii.hexlify(rule_content))

                full_rules += rule_content

        print ("#####", binascii.hexlify(full_rules))
        print ("!!!!", rule_count)    
        
            
        coreconf = b'\xA1' + cbor.dumps(module_sid) + b'\xA1' + cbor.dumps(rule_sid - module_sid) 

        array_header = self.cbor_header(0b100_00000, rule_count) # array

        coreconf +=  array_header+full_rules

        print ("=", binascii.hexlify(coreconf))
        return coreconf
        # end of CORECONF

    def MO_IGNORE (self, TV, FV, rlength, flength, arg):
        return True

    def MO_EQUAL (self, TV, FV,  rlength, flength, arg):
        if type(TV) != type(FV):
            return False

        if TV != FV: return False
        return True

    def MO_MSB (self, TV, FV, rlength, flength, arg):
        dprint ("MSB")
        dprint (TV, FV, rlength, flength, arg)

        if type (TV) != type (FV):
            return False

        if type(TV) == int:
            if type(arg) != int:
                raise ValueError ("MO Arg should be integer")

            shift = rlength-arg
            return self.MO_EQUAL(TV >> shift, FV >> shift, rlength-shift, flength-shift, 0)

        if type(TV) == str:
            if type (arg) != int and arg % 8 != 0:
                raise ValueError("MO arg should be an Interget multiple of 8")

            for i in range(0, arg // 8):
                dprint ("=", TV[i], FV[i], TV[i] == FV[i])
                if TV[i] != FV[i]:
                    return False

            return True

    def MO_MMAP (self, TV, FV,  rlength, flength, arg):
        for v in TV:
            if self.MO_EQUAL (v, FV, rlength, flength, arg): return True
        return False

    MO_function = {
        T_MO_IGNORE : MO_IGNORE,
        T_MO_EQUAL  : MO_EQUAL,
        T_MO_MSB    : MO_MSB,
        T_MO_MMAP   : MO_MMAP,
    }

    def FindRuleFromSCHCpacket (self, schc, device=None):
        """ returns the rule corresponding to the id stored at the
        beginning of the SCHC packet.
        """

        for d in self._ctxt:
            dprint (d["DeviceID"])
            if d["DeviceID"] == device: #look for a specific device
                for r in d["SoR"]:
                    ruleID = r[T_RULEID]
                    ruleLength = r[T_RULEIDLENGTH]

                    tested_rule = schc.get_bits(ruleLength, position=0)

                    dprint (tested_rule, ruleID)
                    if tested_rule == ruleID:
                        return r

        return None


    def FindRuleFromPacket(self, pkt, direction=T_DIR_BI, failed_field=False):
        """ Takes a parsed packet and returns the matching rule.
        """
        for dev in self._ctxt:
            for rule in dev["SoR"]:
                if "Compression" in rule:
                    matches = 0
                    for r in rule["Compression"]:
                        dprint(r)
                        if r[T_DI] == T_DIR_BI or r[T_DI] == direction:
                            if (r[T_FID], r[T_FP]) in pkt:
                                if T_MO_VAL in r:
                                    arg = r[T_MO_VAL]
                                else:
                                    arg = None

                                if self.MO_function[r[T_MO]](self,
                                    r[T_TV], pkt[(r[T_FID], r[T_FP])][0],
                                    r[T_FL], pkt[(r[T_FID], r[T_FP])][1],
                                    arg):
                                        matches += 1
                                else:
                                    if failed_field:
                                        print("rule {}/{}: field {}  does not match TV={} FV={} rlen={} flen={} arg={}".format(
                                            rule[T_RULEID], rule[T_RULEIDLENGTH],
                                            r[T_FID],
                                            r[T_TV], pkt[(r[T_FID], r[T_FP])][0],
                                            r[T_FL], pkt[(r[T_FID], r[T_FP])][1],
                                            arg))
                                    break # field does not match, rule does not match
                            else:
                                if r[T_FL] == "var":  #entry not found, but variable length => accept
                                    matches += 1      # residue size set to 0
                                    dprint("Suboptimal rule")
                                else:
                                    dprint("field from rule not found in pkt")
                                    break # field from rule not found in pkt, go to next
                            dprint ("->", matches)
                    dprint("-"*10, "matches:", matches, len(pkt), rule[T_META][T_UP_RULES], rule[T_META][T_DW_RULES])
                    if direction == T_DIR_UP and matches == rule[T_META][T_UP_RULES]: return rule
                    if direction == T_DIR_DW and matches == rule[T_META][T_DW_RULES]: return rule
        print("here")
        return None

    def FindNoCompressionRule(self, deviceID=None):
        for d in self._ctxt:
            if d["DeviceID"] == deviceID:
                for r in d["SoR"]:
                    if T_NO_COMP in r:
                        return r

        return None        

    def FindFragmentationRule(self, deviceID=None, originalSize=None,
                              reliability=T_FRAG_NO_ACK, direction=T_DIR_UP,
                              packet=None):
        """Lookup a fragmentation rule.

        Find a fragmentation rule regarding parameters:
        * original SCHC packet size
        * reliability NoAck, AckOnError, AckAlways
        * direction (UP or DOWN)
        NOTE: Not yet implemented, returns the first fragmentation rule.  

        XXX please check whether the following strategy is okey.
        - if direction is specified, and deviceID is None, it is assumed that
          the request is for a device. Return the 1st rule matched with the
          direction regardless of the deviceID.  A deviceID for a device is
          not configured typically.
        - if raw_packet is not None, it compares the rule_id with the packet.
        - if the direction and the deviceID is matched.
        """
        dprint("FindFragmentationRule", deviceID, direction)

        if direction is not None and deviceID is not None:
            for d in self._ctxt:
                if d["DeviceID"] == deviceID:
                    for r in d["SoR"]:
                        if T_FRAG in r and r[T_FRAG][T_FRAG_DIRECTION] == direction:
                            return r

        elif direction is not None and deviceID is None:
            for d in self._ctxt:
                for r in d["SoR"]:
                    if T_FRAG in r and r[T_FRAG][T_FRAG_DIRECTION] == direction:
                        # return the 1st one.
                        return r
        elif packet is not None:
            print("packet dev-id", deviceID)
            for d in self._ctxt:
                for r in d["SoR"]:
                    print("rule dev-id", d["DeviceID"])
                    if T_FRAG in r:
                        rule_id = packet.get_bits(r[T_RULEIDLENGTH], position=0)
                        if r[T_RULEID] == rule_id:
                            return r
        else:
            for d in self._ctxt:
                if d["DeviceID"] == deviceID:
                    for r in d["SoR"]:
                        if T_FRAG in r:
                            return r
        return None

    def _checkRuleValue(self, rule_id, rule_id_length):
        """this function looks if bits specified in ruleID are not outside of
        rule_id_length"""

        if rule_id_length > 32:
            raise ValueError("Rule length should be less than 32")

        r1 = rule_id

        for k in range (32, rule_id_length, -1):
            if (0x01 << k) & r1 !=0:
                raise ValueError("rule ID too long")

    def _ruleIncluded(self, r1ID, r1l, r2ID, r2l):
        """check if a conflict exists between to ruleID (i.e. same first bits equals) """
        r1 = r1ID << (32-r1l)
        r2 = r2ID << (32-r2l)
        l  = min(r1l, r2l)

        for k in range (32-l, 32):
            if ((r1 & (0x01 << k)) != (r2 & (0x01 << k))):
                return False

        return True

    def _nameRule (self, r):
        return "Rule {}/{}:".format(r[T_RULEID], r[T_RULEIDLENGTH])

    def find_rule_bypacket(self, context, packet_bbuf):
        """ returns a compression rule or an fragmentation rule
        in the context matching with the field value of rule id in the packet.
        """
        for k in ["fragSender", "fragReceiver", "comp"]:
            r = context.get(k)
            if r is not None:
                rule_id = packet_bbuf.get_bits(r[T_RULEIDLENGTH], position=0)
                if r[T_RULEID] == rule_id:
                    return k, r
        return None, None

    def find_context_bydstiid(self, dst_iid):
        """ find a context with dst_iid, which can be a wild card. """
        # XXX needs to implement wildcard search or something like that.
        for c in self._db:
            if c["dstIID"] == dst_iid:
                return c
            if c["dstIID"] == "*":
                return c
        return None

    def find_context_exact(self, dev_L2addr, dst_iid):
        """ find a context by both devL2Addr and dstIID.
        This is mainly for internal use. """
        for c in self._db:
            if c["devL2Addr"] == dev_L2addr and c["dstIID"] == dst_iid:
                return c
        return None

    def add_context(self, context, comp=None, fragSender=None, fragReceiver=None):
        """ add context into the db. """
        if self.find_context_exact(context["devL2Addr"],
                                   context["dstIID"]) is not None:
            raise ValueError("the context {}/{} exist.".format(
                context["devL2Addr"], context["dstIID"]))
        # add context
        c = deepcopy(context)
        self._db.append(c)
        self.add_rules(c, comp, fragSender, fragReceiver)

    def add_rules(self, context, comp=None, fragSender=None, fragReceiver=None):
        """ add rules into the context specified. """
        if comp is not None:
            self.add_rule(context, "comp", comp)
        if fragSender is not None:
            self.add_rule(context, "fragSender", fragSender)
        if fragReceiver is not None:
            self.add_rule(context, "fragReceiver", fragReceiver)

    def add_rule(self, context, key, rule):
        """ Check rule integrity and uniqueless and add it to the db """

        if not T_RULEID in rule:
           raise ValueError ("Rule ID not defined in {}.".format(self._nameRule(rule)))

        if not T_RULEIDLENGTH in rule:
            if rule[T_RULEID] < 255:
                rule[T_RULEIDLENGTH] = 8
            else:
                raise ValueError ("RuleID too large for default size on a byte")

        # proceed to compression check (TBD)
        if key == "comp":
            self.check_rule_compression(rule)
        elif key in ["fragSender", "fragReceiver", "comp"]:
            self.check_rule_fragmentation(rule)
        else:
            raise ValueError ("key must be either comp, fragSender, fragReceiver")

        rule_id = rule[T_RULEID]
        rule_id_length = rule[T_RULEIDLENGTH]

        self._checkRuleValue(rule_id, rule_id_length)

        for k in ["fragSender", "fragReceiver", "comp"]:
            r = context.get(k)
            if r is not None:
                if rule_id_length == r.RuleIDLength and rule_id == r.RuleID:
                    raise ValueError ("Rule {}/{} exists".format(
                            rule_id, rule_id_length))

        context[key] = DictToAttrDeep(**rule)

    def check_rule_compression(self, rule):
        """ compression rule check """
        # XXX need more work.
        if (not "Compression" in rule or "Fragmentation" in rule):
            raise ValueError ("{} Invalid rule".format(self._nameRule(rule)))

        canon_rule_set = []
        #if "rule_set" not in rule["compression"]:
        #    raise ValueError ("compression must have a rule_set.")
        for r in rule["Compression"]:
            canon_r = {}
            for k,v in r.items():
                if isinstance(v, str):
                    canon_r[k.upper()] = v.upper()
                else:
                    canon_r[k.upper()] = v
            canon_rule_set.append(canon_r)
        rule["Compression"] = canon_rule_set

    def check_rule_fragmentation(self, rule):
        """ fragmentation rule check """
        if (not "Fragmentation" in rule or "Compression" in rule):
            raise ValueError ("{} Invalid rule".format(self._nameRule(rule)))

        if "Fragmentation" in rule:
            fragRule = rule["Fragmentation"]

            if not "FRMode" in fragRule:
                raise ValueError ("{} Fragmentation mode must be specified".format(self._nameRule(rule)))

            mode = fragRule["FRMode"]

            if not mode in (T_FRAG_NO_ACK, T_FRAG_ACK_ALWAYS, T_FRAG_ACK_ON_ERROR):
                raise ValueError ("{} Unknown fragmentation mode".format(self._nameRule(rule)))

            if not "FRModeProfile" in fragRule:
                fragRule["FRModeProfile"] = {}

            profile = fragRule["FRModeProfile"]

            if not "dtagSize" in profile:
                profile["dtagSize"] = 0

            if not "WSize" in profile:
                if  mode == T_FRAG_NO_ACK:
                    profile["WSize"] = 0
                elif  mode == T_FRAG_ACK_ALWAYS:
                    profile["WSize"] = 1
                elif mode == T_FRAG_ACK_ON_ERROR:
                    profile["WSize"] = 5

            if not "FCNSize" in profile:
                if mode == T_FRAG_NO_ACK:
                    profile["FCNSize"] = 1
                elif mode == T_FRAG_ACK_ALWAYS:
                    profile["FCNSize"] = 3
                elif mode == T_FRAG_ACK_ON_ERROR:
                    profile["FCNSize"] = 3

            if "windowSize" in profile:
                if profile["windowSize"] > (0x01 << profile["FCNSize"]) - 1 or\
                   profile["windowSize"] < 0:
                    raise ValueError ("{} illegal windowSize".format(self._nameRule(rule)))
            else:
                profile["windowSize"] = (0x01 << profile["FCNSize"]) - 1

            if mode == T_FRAG_ACK_ON_ERROR:
                if not "ackBehavior" in profile:
                    raise ValueError ("Ack on error behavior must be specified (afterAll1 or afterAll0)")
                if not "tileSize" in profile:
                    profile["tileSize"] = 64

    def get_init_info(self):
        result = {
            "context": self._ctxt.copy(),
            "database": self._db.copy()
        }
        return result
