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

from operator import mod
from gen_base_import import *
from copy import deepcopy
from gen_parameters import *
from compr_core import *
from compr_parser import *
import ipaddress
import warnings

import base64
import cbor2 as cbor

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
    T_ICMPV6_UNUSED        : {"FL": 32, "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_PAYLOAD       : {"FL": "var", "TYPE": bytes, "ALGO": "DIRECT"  },
    T_COAP_VERSION         : {"FL": 2,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TYPE            : {"FL": 2,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TKL             : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_CODE            : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_MID             : {"FL": 16,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TOKEN           : {"FL": "tkl",  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_OPT_URI_HOST    : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION" },
    T_COAP_OPT_URI_PATH    : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION" },
    T_COAP_OPT_CONT_FORMAT : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},
    T_COAP_OPT_ACCEPT      : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},
    T_COAP_OPT_URI_QUERY   : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION" },
    T_COAP_OPT_NO_RESP     : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},
    T_COAP_OPT_OBS         : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"}
}



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
        """test if a value is in the dictionary, otherwise return a specific value """
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
            d = {"DeviceID": device, "SoR": []}
            self._ctxt.append(d)

        d[T_META] = {T_LAST_USED: None}
        #print ("@@@@@", d)

        for n_rule in sor:
            if T_RULEID in n_rule:
                n_ruleID = n_rule[T_RULEID]
            elif T_RULEIDVALUE in n_rule:
                n_ruleID = n_rule[T_RULEIDVALUE]
            else:
                raise ValueError("Rule ID Value is missing")
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
                elif T_FRAG_FEC in n_rule :
                    r = self._create_forwarderrorcorrection_rule(n_rule)
                    d["SoR"].append(r)
                elif T_NO_COMP in n_rule:
                    already_exists = self.FindNoCompressionRule(deviceID=device)
                    if already_exists == None:
                        arule = {}
                        arule[T_RULEID] = n_ruleID
                        arule[T_RULEIDLENGTH] = n_rule[T_RULEIDLENGTH]
                        arule[T_NO_COMP] = []
                        d["SoR"].append(arule)
                    else:
                        print ("Warning 'no compression' rule already exists")
                else:
                    raise ValueError ("Rule type undefined")
                #print (n_rule)

    def _create_forwarderrorcorrection_rule(self, nrule):       #creation de nouvelle regle de FEC
        arule = {}
        if T_RULEID in nrule:
            arule[T_RULEID] = nrule[T_RULEID]
        elif T_RULEIDVALUE in nrule:
            arule[T_RULEID] = nrule[T_RULEIDVALUE]
        else:
            raise ValueError("Rule ID missing.")
        
        arule[T_RULEIDLENGTH] = nrule[T_RULEIDLENGTH]

        arule[T_FRAG_FEC] = {}

        fec_params = nrule.get(T_FRAG_FEC, {})
        for required in [T_FRAG_FEC_BOUNDTO_ID, T_FRAG_FEC_BOUNDTO_LENGTH, T_FRAG_FEC_XORFRAGS]:        #paramètres obligatoires pour la FEC
            if required not in fec_params:
                raise ValueError(f"Missing required parameter '{required}' in ForwardErrorCorrection rule.")

        bound_id = fec_params[T_FRAG_FEC_BOUNDTO_ID]
        bound_len = fec_params[T_FRAG_FEC_BOUNDTO_LENGTH]
        
        frag_rule = None
        for dev in self._ctxt:              # on retrouve la règle de frag classique, a laquelle la regle de FEC est attachée
            for rule in dev["SoR"]:
                if rule[T_RULEID] == bound_id and rule[T_RULEIDLENGTH] == bound_len and T_FRAG in rule:
                    frag_rule = rule
                    break
            if frag_rule:
                break
        
        if frag_rule is None:
            raise ValueError(f"Forward error correction rule initialization : the associated fragmentation rule {bound_id}/{bound_len} doesnt exist.")
        
        # On sécurise l'acces a la FEC seulement au mode no-ack pour l'instant, TODO autoriser autres modes plus tard (AoE...)
        if frag_rule[T_FRAG][T_FRAG_MODE] != T_FRAG_NO_ACK:
            raise ValueError(f"You can use Forward Error Correction, only in No-ACK fragmentation mode")

        arule[T_FRAG_FEC][T_FRAG_FEC_BOUNDTO_ID] = bound_id
        arule[T_FRAG_FEC][T_FRAG_FEC_BOUNDTO_LENGTH] = bound_len
        arule[T_FRAG_FEC][T_FRAG_FEC_XORFRAGS] = fec_params[T_FRAG_FEC_XORFRAGS]

        # a partir d'ici, je peux copier des infos de la regle de frag originelle, par exemple comme ca :
        # arule[T_FRAG_FEC]["FRMode"] = frag_rule[T_FRAG][T_FRAG_MODE]
        arule[T_FRAG_FEC]["FRDirection"] = frag_rule[T_FRAG][T_FRAG_DIRECTION]
        # TODO surement necessaire de rajouter des champs, surtout pour d'autre modes que NoACK
        #arule[T_FRAG_FEC]["FRMode"] = frag_rule[T_FRAG][T_FRAG_MODE]

        return arule

    def _create_fragmentation_rule (self, nrule):
        arule = {}
        if T_RULEID in nrule:
            arule[T_RULEID] = nrule[T_RULEID]
        elif T_RULEIDVALUE in nrule:
            arule[T_RULEID] = nrule[T_RULEIDVALUE]
        else:
            raise ValueError("Rule ID missing.")
        arule[T_RULEIDLENGTH] = nrule[T_RULEIDLENGTH]
        arule[T_FRAG] = {}

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
                _default_value (arule, nrule, T_FRAG_DTAG_SIZE, 0)
                _default_value (arule, nrule, T_FRAG_MIC, T_FRAG_RFC8724)

                if nrule[T_FRAG][T_FRAG_MODE] == T_FRAG_NO_ACK:
                    _default_value(arule, nrule, T_FRAG_DTAG_SIZE, 2)
                    _default_value (arule, nrule, T_FRAG_W_SIZE, 0)
                    if T_FRAG in nrule and T_FRAG_FCN in nrule[T_FRAG]:
                        raise ValueError ("Don't specify FCN Size for NoAck Fragmentation rule")
                    else:
                        _default_value (arule, nrule, T_FRAG_FCN, 1)

                    _default_value(arule, nrule, T_FRAG_L2WORDSIZE, 8)
                elif nrule[T_FRAG][T_FRAG_MODE] == T_FRAG_ACK_ALWAYS:
                    _default_value (arule, nrule, T_FRAG_W_SIZE, 1)
                    _default_value(arule, nrule, T_FRAG_L2WORDSIZE, 8)
                    _default_value (arule, nrule, T_FRAG_MAX_RETRY, 4)
                    _default_value (arule, nrule, T_FRAG_TIMEOUT, 600)
                elif  nrule[T_FRAG][T_FRAG_MODE] == T_FRAG_ACK_ON_ERROR:
                    if not T_FRAG_FCN in nrule[T_FRAG][T_FRAG_PROF]:
                        raise ValueError ("FCN Must be specified for Ack On Error")

                    _default_value (arule, nrule, T_FRAG_W_SIZE, 1)
                    _default_value (arule, nrule, T_FRAG_ACK_BEHAVIOR, T_FRAG_AFTER_ALL1)
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

    def get_values(self, values):
        """This function transforms the YANG list indexed with the first element, to a Python list.
        The key do not have to be sorted, unlisted positions are filled with None. Element stays as
        byte array. 
        """
        value_list = []
        for e in values:     
            list_len = len(value_list)
            for i in range(list_len, e[1]+1): # fill with None to the position
                value_list.append(None)

            value_list[e[1]] = e[2]

        return value_list

    def _create_compression_rule (self, nrule, device_id = None):
        """
        parse a rule to verify values and fill defaults
        """
        arule = {}
        if T_RULEID in nrule: # transition for RuleID to RuleIDValue
            arule[T_RULEID] = nrule[T_RULEID]
        elif T_RULEIDVALUE in nrule:
            arule[T_RULEID] = nrule[T_RULEIDVALUE]
        else:
            raise ValueError("RuleID Value is missing")
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
            if not r["FID"].upper() in FIELD__DEFAULT_PROPERTY:
                raise ValueError( "Unkwown field id {} in rule {}/{}".format(
                    r["FID"], arule[T_RULEID],  arule[T_RULEIDLENGTH]
                ))

            entry = {}
            FID = r[T_FID].upper()
            entry[T_FID] = FID
            entry[T_FL] = self._return_default(r, T_FL, FIELD__DEFAULT_PROPERTY[FID][T_FL])
            entry[T_FP] = self._return_default(r, T_FP, 1)
            entry[T_DI] = self._return_default(r, T_DI, T_DIR_BI)
            if entry[T_DI] in [T_DIR_BI, T_DIR_UP]: up_rules += 1
            if entry[T_DI] in [T_DIR_BI, T_DIR_DW]: dw_rules += 1

            MO = r[T_MO].upper()
            if MO in [T_MO_EQUAL, T_MO_MSB, T_MO_IGNORE, T_MO_MATCH_REV_RULE]:
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
                        entry[T_TV_IND] = adapt_value(key,entry[T_FL], FID)
                    else:
                        entry[T_TV] = adapt_value(r[T_TV], entry[T_FL], FID)
                else:
                    entry[T_TV] = None

            elif MO == T_MO_MMAP:
                entry[T_TV] = []
                for e in r[T_TV]:
                    entry[T_TV].append(adapt_value(e, entry[T_FL], FID))

            else:
                raise ValueError("{} MO unknown".format(MO))
            entry[T_MO] = MO

            CDA = r[T_CDA].upper()
            if not CDA in [T_CDA_NOT_SENT, T_CDA_VAL_SENT, T_CDA_MAP_SENT, T_CDA_LSB, T_CDA_COMP_LEN, 
                           T_CDA_COMP_CKSUM, T_CDA_DEVIID, T_CDA_APPIID, T_CDA_REV_COMPRESS]:
                raise ValueError("{} CDA not found".format(CDA))
            entry[T_CDA] = CDA

            arule[T_COMP].append(entry)

        if not T_META in arule:
            arule[T_META] = {}
        arule[T_META][T_UP_RULES] = up_rules
        arule[T_META][T_DW_RULES] = dw_rules
        arule[T_META][T_DEVICEID] = device_id
        arule[T_META][T_LAST_USED] = None

        return arule


    def __init__(self, file=None, log=None):
        #RM database
        self._ctxt = []
        self._log = log
        self._db = []
        self._sid_info = []
        self.sid_key_mapping = {}

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
                        msg2 = None
                        if len(e[T_FID]) < 16:
                            print ("|{:<15s}|{:>3}|{:2}|{:2}|".format(e[T_FID], e[T_FL], e[T_FP], e[T_DI]), end='')
                        else:
                            msg = e[T_FID]
                            if "-" in msg:
                                msg1, msg2 = msg.split('-')
                                msg1 += '-'
                            else:
                                msg1 = msg[:15]
                                msg2 = msg[15:]
                            print ("|{:<15s}|{:>3}|{:2}|{:2}|".format(msg1, e[T_FL], e[T_FP], e[T_DI]), end="")

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

                        if msg2 != None: # FID is too large, wrote it on 2 lignes, this is the second line
                            print ("|{:<15s}|{:>3}|{:2}|{:2}|{:30}|{:13}|{:16}|".format(msg2, "", "", "", "", "", "" ), )

                    print ("\\" + "-"*15 + "+" + "-"*3 + "+" + "-"*2 + "+" + "-"*2 + "+" + "-"*30 + "+" + "-"*13 + "+" + "-"*16 +"/")
                elif T_FRAG in rule:
                    # print (rule)
                    if rule[T_FRAG][T_FRAG_DIRECTION] == T_DIR_UP:
                        dir_c = "^"
                    else:
                        dir_c = "v"

                    print ("!" + "="*25 + "+" + "="*61 +"\\")
                    print ("!{} Fragmentation mode : {:<15} header dtag{:2} Window {:2} FCN {:2} {:13}{:2} {}!"
                        .format(
                            dir_c,
                            rule[T_FRAG][T_FRAG_MODE],
                            rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE],
                            rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE],
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
                        print ("!{0}" + "-"*83 +"{0}!".format(dir_c))
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
                elif T_FRAG_FEC in rule:                               # affiche de regle de FEC par le rule manager           vvv
                    if rule[T_FRAG_FEC][T_FRAG_DIRECTION] == T_DIR_UP: # un peu ecrit en dur, quelques modif a faire pour rendre ca propre
                        dir_c = "^"
                    else:
                        dir_c = "v"

                    print ("!" + "="*25 + "+" + "="*61 +"\\")
                    print ("!{} Forward Error Correction {:<58} {}!"
                        .format(
                            dir_c,
                            "",
                            dir_c
                        ))
                    print ("!{} Bound to the Fragmentation rule : {}/{} {:<45} {}!".format(dir_c, rule[T_FRAG_FEC][T_FRAG_FEC_BOUNDTO_ID],
                            rule[T_FRAG_FEC][T_FRAG_FEC_BOUNDTO_LENGTH], "", dir_c))
                    print ("!{} XorFrags : {} {:<71}{}!".format(dir_c, rule[T_FRAG_FEC][T_FRAG_FEC_XORFRAGS],"", dir_c))
                    print ("\\" + "="*87 +"/")

                elif T_NO_COMP in rule:
                    print ("+"+ "~"*25 + "+")
                    print ("|     NO COMPRESSION      |")
                    print ("\\"+ "~"*25 + "/")

            if T_INDEXES in dev and len(dev[T_INDEXES]) > 0:
                print ("INDEXES:")
                for x, y in dev[T_INDEXES].items():
                    print (x,"-->", y)


# Find rules 

    def MO_IGNORE (self, TV, FV, rlength, flength, arg, direction=None):
        return True

    def MO_EQUAL (self, TV, FV,  rlength, flength, arg, direction=None):
        if type(TV) != type(FV):
            return False

        if TV != FV: return False
        return True

    def MO_MSB (self, TV, FV, rlength, flength, arg, direction=None):
        if rlength == T_FUNCTION_VAR:
            rlength = flength

        nb_bit_to_shift: int = rlength - arg
        
        # Shift both values right by (rlength - arg) bits
        tv_shifted: int = int.from_bytes(bytes=TV, byteorder="big") >> nb_bit_to_shift
        fv_shifted: int = int.from_bytes(bytes=FV, byteorder="big") >> nb_bit_to_shift
        
        return tv_shifted == fv_shifted


    def MO_MMAP (self, TV, FV,  rlength, flength, arg, direction=None):
        for v in TV:
            if self.MO_EQUAL (v, FV, rlength, flength, arg): return True
        return False
    
    def MO_MATCH_REV_RULE (self, TV, FV,  rlength, flength, arg, direction=None):

        if direction == T_DIR_UP:
            direction = T_DIR_DW
        elif direction == T_DIR_DW:
            direction = T_DIR_UP

        P = Parser(None)

        header_d, payload, error = P.parse(FV, direction=direction)
        rule = self.FindRuleFromPacket(header_d, direction=direction)

        if rule == None:
            return False
        
        return True    

    MO_function = {
        T_MO_IGNORE : MO_IGNORE,
        T_MO_EQUAL  : MO_EQUAL,
        T_MO_MSB    : MO_MSB,
        T_MO_MMAP   : MO_MMAP,
        T_MO_MATCH_REV_RULE: MO_MATCH_REV_RULE,
    }

    def FindRuleFromSCHCpacket (self, schc, device=None):
        """ returns the rule corresponding to the id stored at the
        beginning of the SCHC packet.
        """

        if type(schc) is bytes:
            schc = BitBuffer(schc)

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
                        if failed_field:
                            print(r)
                        if r[T_DI] == T_DIR_BI or r[T_DI] == direction:
                            if (r[T_FID], r[T_FP]) in pkt:
                                #print (pkt[(r[T_FID], r[T_FP])][0])

                                if T_MO_VAL in r:
                                    arg = r[T_MO_VAL]
                                else:
                                    arg = None

                                if self.MO_function[r[T_MO]](self,
                                    r[T_TV], pkt[(r[T_FID], r[T_FP])][0],
                                    r[T_FL], pkt[(r[T_FID], r[T_FP])][1],
                                    arg, direction=direction):
                                        matches += 1
                                else:
                                    if failed_field:
                                        if type(r[T_TV]) is bytes:
                                            print("rule {}/{}: field {}  does not match TV={} FV={} rlen={} flen={} arg={}".format(
                                                rule[T_RULEID], rule[T_RULEIDLENGTH],
                                                r[T_FID],
                                                binascii.hexlify(r[T_TV]), 
                                                binascii.hexlify(pkt[(r[T_FID], r[T_FP])][0]),
                                                r[T_FL], pkt[(r[T_FID], r[T_FP])][1],
                                                arg))
                                        elif type(r[T_TV]) is list:
                                            print("rule {}/{}: field {}  FV={} not in matching list rlen={} flen={} arg={}".format(
                                                rule[T_RULEID], rule[T_RULEIDLENGTH],
                                                r[T_FID],
                                                binascii.hexlify(pkt[(r[T_FID], r[T_FP])][0]),
                                                r[T_FL], pkt[(r[T_FID], r[T_FP])][1],
                                                arg))                                           
                                    break # field does not match, rule does not match
                            else:
                                if r[T_FL] == "var":  # entry not found, but variable length => accept
                                    matches += 1      # residue size set to 0
                                    dprint("Suboptimal rule")
                                else:
                                    dprint("field from rule not found in pkt")
                                    break # field from rule not found in pkt, go to next
                            #print ("->", matches)
                    #print("-"*10, "matches:", matches, len(pkt), rule[T_META][T_UP_RULES], rule[T_META][T_DW_RULES])
                    if direction == T_DIR_UP and matches == rule[T_META][T_UP_RULES]: return rule
                    if direction == T_DIR_DW and matches == rule[T_META][T_DW_RULES]: return rule
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

# CORECONF 

    def add_sid_file(self, name):
        with open(name) as sid_file:
            sid_values = json.loads(sid_file.read())

        if 'key-mapping' not in sid_values:
            print ("""{} sid files has not been genreated with the --sid-extention options.\n\
Some conversion capabilities may not works. see http://github.com/ltn22/pyang""".format(name)) 
        else:
            for k, v in sid_values['key-mapping'].items():
                if k in self.sid_key_mapping:
                    print ("key sid", k, "already present, ignoring...")
                else: 
                    self.sid_key_mapping[int(k)] = v
            del(sid_values["key-mapping"])

        self._sid_info.append(sid_values)

    def sid_search_for(self, name, space="data"):

        for s in self._sid_info:
            for e in s["items"]:
                if e["identifier"] == name and e["namespace"]==space:
                    return e["sid"]
        return None 

    def sid_search_sid(self, value, short=False):
        """return YANG ID form a SID, if short is set to true, the module id is not concatenated."""
        for s in self._sid_info:
            name = s["module-name"]
            for e in s["items"]:
                if e["sid"] == value:
                    if e["namespace"] == "identity":
                        if short:
                            return e["identifier"]
                        else: 
                            return name + ":" + e["identifier"]
                    elif e["namespace"] == "data":
                        return e["identifier"]
                    else:
                        raise ValueError("not a good namespace", e["namespace"])

        raise ValueError("Not found", value)
        return None         

    def openschc_id (self, yang_id):
        """return an OpenSCHC ID giving a yang ID stored in .sid files"""
        for i in YANG_ID:
            if YANG_ID[i][1] == yang_id:
                return i

        raise ValueError(yang_id, "not known by openSCHC")

    def get_yang_type (self, yangid):
        for s in self._sid_info:
            module_name = s['module-name']
            for e in s['items']:
                if e['identifier'] == yangid:
                    if "type" in e:
                        if type(e['type']) is str:
                            if e["type"] in  ["int8", "int16", "int32", "uint8", "uint16", "uint32"]:
                                return "int"
                            elif e["type"] in ["string", 'binary']:
                                return e['type']
                            else:
                                return 'identifier'
                        elif type(e['type']) is list: # union, should be extended
                            """In theorie, this function is called when a cbor data for an int is found. 
                            regarding the CORECONF coding, other alternative
                            identifier or enum are tagged, and will be processed directly by other
                            function, so whenan union is found, it should be the array. The only test
                            is to check that int in the array or generate an error. """
                            return 'union'
                    else: 
                        return "node" # this is not a leaf
        return None #yandid not found


    def cbor_header (self, major, value):
        if value < 23:
            return struct.pack ('!B', (major | value))
        elif value < 255:
            return struct.pack ('!BB', (major | 24),  value)

    def from_coreconf(self, device=None, dev_info=None, file=None, compression=True):
        """
        Take a coreconf representation and store it in the rule manager.
        """

        assert (dev_info is not None or file is not None)

        if file != None:
            dev_info = open(file).read() 

        # allows CBOR or Python structure, if CBOR convert it in Python. 
        if type(dev_info) is bytes:
            rule_input = cbor.loads(dev_info) # store CBOR CORECONF
        elif type(dev_info) is dict:
            rule_input = dev_info # coreconf already in python
        else:
            raise ValueError("Unknown rule format")

        SoR = []

        schc_id = self.sid_search_for(name="/ietf-schc:schc", space="data")

        if not schc_id in rule_input:
            print ("This is a not a Set of Rule")
            return None

        entry = rule_input[schc_id]

        sid_ref = self.sid_search_for(name="/ietf-schc:schc/rule", space="data")
        rid_value_sid = self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-value", space="data") - sid_ref
        rid_length_sid = self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-length", space="data") - sid_ref
        rule_nature_sid = self.sid_search_for(name="/ietf-schc:schc/rule/rule-nature", space="data") - sid_ref
        for rule in entry[1]:
            arule = {}
            arule[T_RULEID] = rule[rid_value_sid]
            arule[T_RULEIDLENGTH] =rule[rid_length_sid]
            rule_nature = rule[rule_nature_sid]

            nature = self.sid_search_sid (rule_nature, short=True)
            if nature == "nature-compression":
                entry = []
                entry_ref = self.sid_search_for(name="/ietf-schc:schc/rule/entry", space="data") 
                entry_sid = entry_ref - sid_ref
                fid_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-id", space="data") - entry_ref
                fl_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-length", space="data") - entry_ref
                fpos_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-position", space="data") - entry_ref
                dir_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/direction-indicator", space="data") - entry_ref
                mo_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/matching-operator", space="data") - entry_ref
                mo_val_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/matching-operator-value", space="data") - entry_ref
                cda_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/comp-decomp-action", space="data") - entry_ref
                tv_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry/target-value", space="data") - entry_ref

                up_rules = 0
                dw_rules = 0
                for r in rule[entry_sid]:
                    entry_elm = {}

                    fid_value = r[fid_sid]
                    fid_yang_name = self.sid_search_sid (fid_value, short=True)
                    o_schc_id = self.openschc_id(fid_yang_name)
                    entry_elm[T_FID] = o_schc_id

                    fl_value = r[fl_sid]
                    if type(fl_value) is cbor.CBORTag and fl_value.tag == 45:
                        fl_value = self.sid_search_sid(fl_value.value, short = True)
                        if fl_value == "fl-token-length": # use OPENSCHC ID
                           fl_value =  T_FUNCTION_TKL 
                        elif fl_value == "fl-variable":
                            fl_value = T_FUNCTION_VAR
                    entry_elm[T_FL] = fl_value

                    dir_value = r[dir_sid]
                    dir_yang_name = self.sid_search_sid (dir_value, short=True)
                    o_schc_id = self.openschc_id(dir_yang_name)   
                    entry_elm[T_DI] = o_schc_id

                    if o_schc_id == T_DIR_BI:
                        up_rules += 1
                        dw_rules += 1
                    elif o_schc_id == T_DIR_UP:
                        up_rules += 1
                    elif o_schc_id == T_DIR_DW:
                        dw_rules += 1

                    fpos = r[fpos_sid]
                    entry_elm[T_FP] = fpos

                    mo_value = r[mo_sid]
                    mo_yang_name = self.sid_search_sid (mo_value, short=True)
                    o_schc_id = self.openschc_id(mo_yang_name)
                    entry_elm[T_MO] = o_schc_id

                    if mo_val_sid in r:
                        values = self.get_values(r[mo_val_sid])
                        entry_elm[T_MO_VAL] = int.from_bytes(values[0], byteorder='big') # 1 arg = length

                    cda_value = r[cda_sid]
                    cda_yang_name = self.sid_search_sid (cda_value, short=True)
                    o_schc_id = self.openschc_id(cda_yang_name)
                    entry_elm[T_CDA] = o_schc_id

                    if tv_sid in  r:
                        values = self.get_values(r[tv_sid])
                        #print (values)
                        if len (values) == 1:
                            entry_elm[T_TV] = values[0]
                        else:
                            entry_elm[T_TV] = values

                    #print (entry_elm, up_rules, dw_rules)

                    entry.append(entry_elm)

                arule[T_COMP] = entry
                if not T_META in arule:
                    arule[T_META] = {}
                arule[T_META][T_UP_RULES] = up_rules
                arule[T_META][T_DW_RULES] = dw_rules
                arule[T_META][T_DEVICEID] = device


            elif nature =="nature-fragmentation":
                #print ('fragmentation')
                arule[T_FRAG] = {}
                arule[T_FRAG][T_FRAG_PROF] = {}
                frag_mod_sid = self.sid_search_for(name="/ietf-schc:schc/rule/fragmentation-mode", space="data") - sid_ref
                frag_mod_id = self.sid_search_sid(rule[frag_mod_sid], short=True)

                l2_word_sid = self.sid_search_for(name="/ietf-schc:schc/rule/l2-word-size", space="data") - sid_ref
                if l2_word_sid in rule:
                    l2_word = rule[l2_word_sid]
                    if l2_word != 8:
                        raise ValueError("OpenSCHC only support 8 bit long l2 words")
                    else:
                        #print ("L2 Word set to 8 by default")
                        l2_word = 8

                direction_sid = self.sid_search_for(name="/ietf-schc:schc/rule/direction", space="data") - sid_ref
                direction = self.sid_search_sid(rule[direction_sid], short=True)

                if direction == 'di-up':
                    arule[T_FRAG][T_FRAG_DIRECTION] = T_DIR_UP
                elif direction == 'di-down':
                    arule[T_FRAG][T_FRAG_DIRECTION] = T_DIR_DW
                else:
                    raise ValueError ("Unknown fragmentation rule direction", direction)

                dtag_size_sid = self.sid_search_for(name="/ietf-schc:schc/rule/dtag-size", space="data") - sid_ref
                if dtag_size_sid in rule:
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] = rule[dtag_size_sid]
                else:
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE] = 0

                w_size_sid = self.sid_search_for(name="/ietf-schc:schc/rule/w-size", space="data") - sid_ref
                if w_size_sid in rule:
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] = rule[w_size_sid]
                else:
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE] = 0

                fcn_size_sid = self.sid_search_for(name="/ietf-schc:schc/rule/fcn-size", space="data") - sid_ref
                if fcn_size_sid in rule:
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN] = rule[fcn_size_sid]
                else:
                    raise ValueError("FCN must be specified")

                rcs_algo_sid = self.sid_search_for(name="/ietf-schc:schc/rule/rcs-algorithm", space="data") - sid_ref
                if rcs_algo_sid in rule:
                    rcs_algo = self.sid_search_sid(rule[rcs_algo_sid], short=True)
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_MIC] = self.openschc_id(rcs_algo)
                else:
                   arule[T_FRAG][T_FRAG_PROF][T_FRAG_MIC] = T_FRAG_RFC8724

                max_pkt_size_sid = self.sid_search_for(name="/ietf-schc:schc/rule/maximum-packet-size", space="data") - sid_ref
                if max_pkt_size_sid in rule:
                    arule[T_FRAG][T_FRAG_PROF][T_MAX_PACKET_SIZE] = rule[max_pkt_size_sid]
                else:
                    arule[T_FRAG][T_FRAG_PROF][T_MAX_PACKET_SIZE] = 1280

                window_size_sid = self.sid_search_for(name="/ietf-schc:schc/rule/window-size", space="data") - sid_ref
                if window_size_sid  in rule:
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_WINDOW_SIZE] =  rule[window_size_sid]
                else:
                   arule[T_FRAG][T_FRAG_PROF][T_FRAG_WINDOW_SIZE] = 2**arule[T_FRAG][T_FRAG_PROF][T_FRAG_FCN] - 1
                   if arule[T_FRAG][T_FRAG_PROF][T_FRAG_WINDOW_SIZE] < 1:  #case if W is 0 or 1
                        arule[T_FRAG][T_FRAG_PROF][T_FRAG_WINDOW_SIZE] = 1
 
                max_inter_frame_sid = self.sid_search_for(name="/ietf-schc:schc/rule/max-interleaved-frames", space="data") - sid_ref
                if max_inter_frame_sid in rule:
                    arule[T_FRAG][T_FRAG_PROF][T_MAX_INTER_FRAME] =  rule[max_inter_frame_sid]
                else:
                   arule[T_FRAG][T_FRAG_PROF][T_MAX_INTER_FRAME] = 1

                inac_timer_sid = self.sid_search_for(name="/ietf-schc:schc/rule/inactivity-timer", space="data") - sid_ref
                if inac_timer_sid in rule:
                    inac_timer = rule[inac_timer_sid]
                    tick_duration_sid = self.sid_search_for(name="/ietf-schc:schc/rule/inactivity-timer/ticks-duration", space="data") - inac_timer_sid
                    tick_number_sid = self.sid_search_for(name="/ietf-schc:schc/rule/inactivity-timer/ticks-numbers", space="data") - inac_timer_sid
                
                    if tick_duration_sid in inac_timer:
                        tick_duration = inac_timer[tick_duration_sid]
                    else:
                        tick_duration = 20

                    if tick_number_sid in inac_timer:
                        tick_number = inac_timer[tick_number_sid]
                    else:
                        tick_number = 600 # Value to be checked

                    inactivity_timer = int(tick_number * (2**tick_duration / 10**6))
                else:
                    inactivity_timer = 12 * 60 * 60 # default timer in seconds

                retrans_timer_sid = self.sid_search_for(name="/ietf-schc:schc/rule/retransmission-timer", space="data") - sid_ref
                if retrans_timer_sid in rule:
                    tick_duration_sid = self.sid_search_for(name="/ietf-schc:schc/rule/retransmission-timer/ticks-duration", space="data") - retrans_timer_sid
                    tick_number_sid = self.sid_search_for(name="/ietf-schc:schc/rule/retransmission-timer/ticks-numbers", space="data") - retrans_timer_sid
                
                    if tick_duration_sid in inac_timer:
                        tick_duration = inac_timer[tick_duration_sid]
                    else:
                        tick_duration = 20

                    if tick_number_sid in inac_timer:
                        tick_number = inac_timer[tick_number_sid]
                    else:
                        tick_number = 60 # Value to be checked

                    retransmission_timer = int(tick_number * (2**tick_duration / 10**6))

                else:
                    retransmission_timer = 1 * 60 * 60 # default timer in seconds
                arule[T_FRAG][T_FRAG_PROF][T_FRAG_TIMEOUT] = retransmission_timer

                max_ack_req_sid = self.sid_search_for(name="/ietf-schc:schc/rule/max-ack-requests", space="data") - sid_ref
                if max_ack_req_sid  in rule:
                    arule[T_FRAG][T_FRAG_PROF][T_FRAG_MAX_RETRY] =  rule[max_ack_req_sid]
                else:
                   arule[T_FRAG][T_FRAG_PROF][T_FRAG_MAX_RETRY] = 4 # openSCHC default value

                if frag_mod_id == 'fragmentation-mode-no-ack':
                    arule[T_FRAG][T_FRAG_MODE] = T_FRAG_NO_ACK
                elif frag_mod_id == 'fragmentation-mode-ack-always':
                    arule[T_FRAG][T_FRAG_MODE] = T_FRAG_ACK_ALWAYS
                elif frag_mod_id == 'fragmentation-mode-ack-on-error':
                    arule[T_FRAG][T_FRAG_MODE] = T_FRAG_ACK_ON_ERROR

                    tile_size_sid = self.sid_search_for(name="/ietf-schc:schc/rule/tile-size", space="data") - sid_ref
                    if tile_size_sid  in rule:
                        arule[T_FRAG][T_FRAG_PROF][T_FRAG_TILE] =  rule[max_ack_req_sid]
                    else:
                        arule[T_FRAG][T_FRAG_PROF][T_FRAG_TILE] = 10 # openSCHC default value

                    tile_in_all1_sid = self.sid_search_for(name="/ietf-schc:schc/rule/tile-in-all-1", space="data") - sid_ref
                    if tile_in_all1_sid in rule:
                        tile_in = self.sid_search_sid(rule[max_ack_req_sid], short=True)
                        if tile_in == "all-1-data-no":
                            arule[T_FRAG][T_FRAG_PROF][T_FRAG_LAST_TILE_IN_ALL1] = False
                        if tile_in == "all-1-data-yes":
                            arule[T_FRAG][T_FRAG_PROF][T_FRAG_LAST_TILE_IN_ALL1] = True
                        if tile_in == "all-1-data-sender-choice":
                            arule[T_FRAG][T_FRAG_PROF][T_FRAG_LAST_TILE_IN_ALL1] = None
                    else:
                        arule[T_FRAG][T_FRAG_PROF][T_FRAG_LAST_TILE_IN_ALL1] = False

                    ack_behavior_sid = self.sid_search_for(name="/ietf-schc:schc/rule/tile-in-all-1", space="data") - sid_ref
                    if ack_behavior_sid in rule:
                        ack_behavior = self.sid_search_sid(rule[max_ack_req_sid], short=True)

                        if ack_behavior == "ack-behavior-after-all-0":
                            arule[T_FRAG][T_FRAG_PROF][T_FRAG_ACK_BEHAVIOR] = T_FRAG_AFTER_ALL0
                            print ("Warning not implemented")
                        elif ack_behavior == "ack-behavior-after-all-1":
                            arule[T_FRAG][T_FRAG_PROF][T_FRAG_ACK_BEHAVIOR] = T_FRAG_AFTER_ALL1
                        elif ack_behavior == "ack-behavior-by-layer2":
                            arule[T_FRAG][T_FRAG_PROF][T_FRAG_ACK_BEHAVIOR] = T_FRAG_AFTER_ANY
                            print ("Warning not implemented")
                        else:
                            raise ValueError ("Unknwon Ack Behavior")
                    else:
                        arule[T_FRAG][T_FRAG_PROF][T_FRAG_ACK_BEHAVIOR] = T_FRAG_AFTER_ALL1 # openSCHC default value
                    
                else:
                    raise ValueError("unkwown fragmentation mode", frag_mod_id)

            elif nature == "nature-no-compression":
                arule [T_NO_COMP] = []
            else:
                raise ValueError ("Unknown rule nature SID", nature)

            SoR.append(arule) # add to the set of rules


        #pprint.pprint(SoR)
        
        self.Add(device=device, dev_info=SoR)


    def to_coreconf (self, deviceID="None"):
        """
        Dump the rules in CORECONF format the rules inside the rule manager for a specific device.
        """
        import binascii

        def dictify_cbor (val, ref_id):
            cbor_data = b''
            if type(val) != list:
                val = [val]

            tv_array = b''
            for i in range(len(val)):

                if type(val[i]) == int:
                    x = val[i]
                    r = b''
                    while x != 0:
                        r = struct.pack('!B', x&0xFF) + r
                        x >>= 8
                elif type(val[i]) == bytes:
                    r = val[i]

                tv_array += b'\xA2' + \
                    cbor.dumps(self.sid_search_for(name=ref_id+"/index", space="data") - self.sid_search_for(name=ref_id, space="data")) + \
                    cbor.dumps(i)

                tv_array +=  \
                    cbor.dumps(self.sid_search_for(name=ref_id+"/value", space="data") - self.sid_search_for(name=ref_id, space="data")) + \
                    cbor.dumps(r)


            tv_array = self.cbor_header(0b100_00000, len(val)) + tv_array
            return tv_array
 
        module_sid = self.sid_search_for(name="/ietf-schc:schc", space="data")
        rule_sid = self.sid_search_for(name="/ietf-schc:schc/rule", space="data")


        for dev in self._ctxt:
            #print ("*"*40)
            #print ("Device:", dev["DeviceID"])

            rule_count = 0
            full_rules = b''
            for rule in dev["SoR"]:
                rule_count += 1
                if T_COMP in rule:
                    entry_sid = self.sid_search_for(name="/ietf-schc:schc/rule/entry", space="data")
                
                    nb_entry = 0
                    rule_content = b''
                    for e in rule[T_COMP]:
                        nb_elm = 0
                        nb_entry += 1

                        entry_cbor = \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-id", space="data") - entry_sid) + \
                            cbor.dumps(self.sid_search_for(name=YANG_ID[e[T_FID]][1], space="identity")) 
                        nb_elm += 1

                        l=e[T_FL]
                        if type(l) == int:
                            entry_cbor += \
                                cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-length", space="data") - entry_sid) + \
                                cbor.dumps(l)
                        elif type(l) == str:
                            entry_cbor += \
                                cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/field-length", space="data") - entry_sid) + \
                                struct.pack("!BB", 0xD8, 45) + \
                                cbor.dumps(self.sid_search_for(name=YANG_ID[l][1], space="identity")) 

                            #raise ValueError("Field ID not defined")
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

                        if T_MO_VAL in e:
                            mo_val_cbor = dictify_cbor(e[T_MO_VAL], "/ietf-schc:schc/rule/entry/matching-operator-value")
                            entry_cbor += \
                                cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/matching-operator-value", space="data") - entry_sid) + \
                                mo_val_cbor
                            nb_elm += 1

                        entry_cbor += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/comp-decomp-action", space="data") - entry_sid) + \
                            cbor.dumps(self.sid_search_for(name=YANG_ID[e[T_CDA]][1], space="identity")) 
                        nb_elm += 1

                        if T_TV in e and e[T_TV] != None:
                            tv_cbor = dictify_cbor(e[T_TV], "/ietf-schc:schc/rule/entry/target-value")

                            entry_cbor += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry/target-value", space="data") - entry_sid) + \
                            tv_cbor
                            nb_elm += 1
 
                        entry_cbor = self.cbor_header (0b101_00000, nb_elm) + entry_cbor # header MAP and size
                        rule_content += entry_cbor

                    rule_content = b'\xA4' + \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/entry", space="data") - rule_sid) + \
                        self.cbor_header(0b100_00000, nb_entry) + rule_content + \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-value", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEID]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-length", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEIDLENGTH]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-nature", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name= "nature-compression", space="identity")) 
                elif T_FRAG in rule:
                    nb_elm = 3
                    rule_content = \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-value", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEID]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-length", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEIDLENGTH]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-nature", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name= "nature-fragmentation", space="identity")) 

                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/direction", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name=YANG_ID[rule[T_FRAG][T_FRAG_DIRECTION]][1], space="identity")) 
                    nb_elm += 1
 
                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rcs-algorithm", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name=YANG_ID[rule[T_FRAG][T_FRAG_PROF][T_FRAG_MIC]][1], space="identity")) 
                    nb_elm += 1

                    rule_content += \
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/dtag-size", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_FRAG][T_FRAG_PROF][T_FRAG_DTAG_SIZE])
                    nb_elm += 1

                    if rule[T_FRAG][T_FRAG_MODE] in [T_FRAG_ACK_ALWAYS, T_FRAG_ACK_ON_ERROR]:
                        rule_content += \
                            cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/w-size", space="data") - rule_sid) +\
                            cbor.dumps(rule[T_FRAG][T_FRAG_PROF][T_FRAG_W_SIZE])
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
                    rule_content = rule_content = self.cbor_header(0b101_00000, 3) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-value", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEID]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-id-length", space="data") - rule_sid) +\
                        cbor.dumps(rule[T_RULEIDLENGTH]) +\
                        cbor.dumps(self.sid_search_for(name="/ietf-schc:schc/rule/rule-nature", space="data") - rule_sid) +\
                        cbor.dumps(self.sid_search_for(name= "nature-no-compression", space="identity")) 
                else:
                    raise ValueError("unkwon rule")

                full_rules += rule_content        
            
        coreconf = b'\xA1' + cbor.dumps(module_sid) + b'\xA1' + cbor.dumps(rule_sid - module_sid) 

        array_header = self.cbor_header(0b100_00000, rule_count) # array

        coreconf +=  array_header+full_rules
        return coreconf
        # end of CORECONF

    def convert_to_json(self, jcc, delta=0, name_ref=""):
        if type(jcc) is dict:
            json_dict = {}
            for k, v in jcc.items():
                sid_description = self.sid_search_sid(k+delta)
                value = self.convert_to_json(v, k+delta, sid_description)
                key = sid_description.replace(name_ref+'/', '')

                json_dict[key] = value
            return json_dict
        elif type(jcc) is list:
            json_list = []
            for e in jcc:
                value = self.convert_to_json(e, delta, name_ref )
                json_list.append(value)
            return json_list
        elif type(jcc) is int:
            node_type = self.get_yang_type(name_ref)

            if node_type in ["int", "union"]: #/!\ to be improved, suppose that union contains an int
                return jcc
            elif node_type == "identifier":
                sid_ref = self.sid_search_sid(jcc)
                return sid_ref
            else:
                raise ValueError(name_ref, node_type, "not a leaf")

        elif type(jcc) is bytes:
            return base64.b64encode(jcc).decode()
        elif type(jcc) is cbor.CBORTag: # TAG == 45, an identifier not an int.
            if jcc.tag == 45:
                sid_ref = self.sid_search_sid(jcc.value)
                return sid_ref
            else:
                raise ValueError("CBOR Tag unknown:", jcc.tag)
        else:
            raise ValueError ("Unknown type", type(jcc)) 

    def get_cc (self, sor, sid=None, keys = [], delta=0, ident=1, value=None):
        #print ("-"*ident, sid, keys)

        if sid == delta:
            if value == None:
                return sor
            else:
                sor = value
                return True

        if type(sor) is dict:
            result = None

            if len(keys) == 0 and sid-delta in sor:
                if value == None:
                    return {sid: sor[sid-delta]}
                else: # change the value
                    sor[sid-delta] = value
                    return True

            if len(keys) == 0 and value: # element is not in the object 
                #print ("add the element")
                sor[sid-delta] = value
                return True

            for s, v in sor.items():
                #print ('.'*ident, s, v)

                # if s+delta == sid:
                #     return {s: v}

                if s+delta in self.sid_key_mapping: # A list we have keys, look for specific entry
                    # Raise an err if the number of SID keys are not the same as the number of keys in self.sid_key_mapping
                    if len(self.sid_key_mapping[s+delta]) > len(keys):
                        raise ValueError ("Not enough keys values to locate the SID")

                    key_search = {}
                    for k in self.sid_key_mapping[s+delta]:
                        key_search[k-(s+delta)] = keys.pop(0)

                    #print ("!"*ident, key_search)

                    found_st = None
                    found_index = 0
                    for l in sor[s]:
                        #print ("+"*ident, l)
                        if key_search.items() <= l.items(): # searched items included in leaf
                            found_st = l
                            break
                        found_index += 1
                    if found_st:
                        if sid == s+delta:
                            if value == None:
                                # keys must be adapted to take into account of the delta coding
                                st_delta_adjusted = {}
                                # Adjust the keys by developing the complete SID ( completeSID = s + k + delta )
                                for k, v in found_st.items():
                                    st_delta_adjusted[s+k+delta] = v
                                return st_delta_adjusted
                            else:
                                sor[s][found_index] = value
                                return True
                        return self.get_cc(found_st, delta=s+delta, ident=ident+1, sid=sid, keys=keys, value=value)
                    else:
                        if value != None:
                            print ("add it", key_search)
                            new_struct = key_search.copy()
                            for new_key, new_value in value.items():
                                if new_key in new_struct:
                                    print ("key leaf ", new_key+delta, "already set to key value")
                                else: 
                                    new_struct[new_key] = new_value

                            sor[s].append(new_struct)
                            return True
                
                else: # A set of container, take all elements
                    if result == None:
                        result = self.get_cc (v, sid, keys, delta+s, ident+1, value)

            if result != None:
                return result
        
    def manipulate_coreconf(self, sid, device=None, keys=None, value=None, validate=None):
        cconf = self.to_coreconf(device)

        if type(sid) is str:
            sid = self.sid_search_for (sid, space='data')

        keys_sid = []
        if keys:
            for e in keys:
                if type(e) is str: # if string is YANG ID then change to SID value
                    k_sid = self.sid_search_for(e, space="identity")
                    if k_sid != None:
                        e = k_sid
                keys_sid.append(e)

        if type(value) is str:
            value_sid =  self.sid_search_for(value, space="identity")
            if value_sid:
                value = value_sid

        json_cconf = cbor.loads(cconf)
        result = self.get_cc(sor=json_cconf, sid=sid, keys=keys_sid, value=value)

        if value != None and result == True:
            if validate:
                inst = validate.from_raw(self.convert_to_json(json_cconf))
                inst.validate() # if wrong raise an error

            # remove current rule
            for i in range(len(self._ctxt)):
                dev = self._ctxt[i]
                #print ("Device:", dev["DeviceID"])
                if dev['DeviceID'] == device:
                    self._ctxt.pop(i)
                    break
            # add the modified one
            self.from_coreconf(device=device, dev_info=json_cconf)
        return result
