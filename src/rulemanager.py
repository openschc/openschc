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

# Introduction

The context includes a set of rules shared by both ends.
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
  * "_**coaptkl**_": this function is specific for compressing the CoAP Token field. The length of the Token is determined at run time by the protocol analyzer by looking at the Token Length field of he CoAP header.
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
      {"FID": "ICMPV6.SEQNO","FL": 16,"FP": 1,"DI": "Bi","TV": [],"MO": "ignore","CDA": "value-sent"}
    ]
}


## Fragmentation Rules
<<< to be written >>>.

# Context

A context is associated with a specific device, which may be identified by a unique LPWAN
identifier, for instance a LoRaWAN devEUI.

The context also includes a set of rules. The rule description is defined [above](#rule-definition).


    [
        {
            "DeviceID": 0x1234567890,
            "SoR" : { ..... }
        },
        {
            "DeviceID": 0xDEADBEEF,
            "SoR" : { ..... }
        },
        ...
    ]

DeviceID is a numerical value that must be unique in the context. If the context is used on a device, the deviceID may be omitted or set to null. In the core network, the DeviceIDs must be specified.

The set of rules itself expands as shown below.

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



### Remove

Suppresses a rule for a specific device <<< only one, or a set of rules? >>>. If no rule is specified, all rules for that device are removed from the context.

      RM.remove ({"DeviceID": 0x1234567, "SoR": {{"ruleID":12, "ruleLength":4}}})
      RM.remove ({"DeviceID": 0x1234567})

### FindRuleFromPacket

This method returns a rule and a DeviceID that match a packet description given by the protocol analyzer.

### FindFragmentationRule (size)

Returns a fragmentation rule compatible with the packet size passed as parameter.


### FindRuleFromID

Given the first bits received from the LPWAN, returns either a fragmentation or a compression rule.


"""

from base_import import *
from copy import deepcopy
from schccomp import *
import binascii
import ipaddress
import pprint

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
    T_IPV6_VER         : {"FL": 4,  "TYPE": int },
    T_IPV6_TC          : {"FL": 8,  "TYPE": int  },
    T_IPV6_FL          : {"FL": 20, "TYPE": int  },
    T_IPV6_NXT         : {"FL": 8,  "TYPE": int  },
    T_IPV6_HOP_LMT     : {"FL": 8,  "TYPE": int  },
    T_IPV6_LEN         : {"FL": 16, "TYPE": int },
    T_IPV6_DEV_PREFIX  : {"FL": 64, "TYPE": bytes  },
    T_IPV6_DEV_IID     : {"FL": 64, "TYPE": bytes },
    T_IPV6_APP_PREFIX  : {"FL": 64, "TYPE": bytes  },
    T_IPV6_APP_IID     : {"FL": 64, "TYPE": bytes  },
    T_UDP_DEV_PORT     : {"FL": 16, "TYPE": int  },
    T_UDP_APP_PORT     : {"FL": 16, "TYPE": int  },
    T_UDP_LEN          : {"FL": 16, "TYPE": int  },
    T_UDP_CKSUM        : {"FL": 16, "TYPE": int  },
    T_ICMPV6_TYPE      : {"FL": 8,  "TYPE": int },
    T_ICMPV6_CODE      : {"FL": 8,  "TYPE": int },
    T_ICMPV6_CKSUM     : {"FL": 16, "TYPE": int },
    T_ICMPV6_IDENT     : {"FL": 16, "TYPE": int },
    T_ICMPV6_SEQNO     : {"FL": 16, "TYPE": int },
    T_COAP_OPT_URI_PATH: {"FL": "var", "TYPE": str}
}

print (FIELD__DEFAULT_PROPERTY)
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

    def Add(self, device= None, dev_info=None, file=None):
        """
        Add is used to add a new rule or a set of rules to a context. Add checks the validity of the rule:
        * ruleID/RuleIDLength do not overlap
        * the rule contains either one of a fragmentation and a compression description.

        If the DeviceID already exists in the context, the new rule is added to that context, providing no conflict on the RuleID is found.

              RM.Add ({"DeviceID": 0x1234567, "sor": {.....}})

        """

        assert (dev_info == None or file == None)

        if file != None:
            dev_info = json.loads(open(file).read())

        if type(dev_info) is dict: #Context or Rules
            if "RuleID" in dev_info: # Rules
                sor = [dev_info]
            elif "SoR" in dev_info:
                if "DeviceID" in dev_info:
                    device = dev_info["DeviceID"]
                sor    = dev_info["SoR"]
            else:
                ValueError("unknown format")
        elif type(dev_info) is list: # a Set of Rule
            sor = dev_info
        else:
            ValueError("unknown structure")


        # check nature of the info: if "SoR" => device context, if "RuleID" => rule

        d = None
        for d in self._ctxt:
            if device == d["DeviceID"]:
                break

        if d == None:
            d = {"DeviceID": device, "SoR": []}
            self._ctxt.append(d)

        for n_rule in sor:
            n_ruleID = n_rule["RuleID"]
            n_ruleLength = n_rule["RuleLength"]
            left_aligned_n_ruleID = n_ruleID << (32 - n_ruleLength)

            overlap = False
            for e_rule in d["SoR"]: # check no overlaps on RuleID
                left_aligned_e_ruleID = e_rule["RuleID"] << (32 - e_rule["RuleLength"])
                if left_aligned_e_ruleID == left_aligned_n_ruleID:
                    print ("Warning; Rule {}/{} exists not inserted".format(bin(n_ruleID), n_ruleLength) )
                    overlap = True
                    break

            if not overlap:
                r = self._create_rule(n_rule)
                d["SoR"].append(r)

    def _adapt_value (self, FID, value):
        if FIELD__DEFAULT_PROPERTY[FID]["TYPE"] == int:
            if type(value) != int:
                ValueError ("{} TV type not appropriate")
            else:
                return value
        if FIELD__DEFAULT_PROPERTY[FID]["TYPE"] == str:
            if type(value) != str:
                ValueError ("{} TV type not appropriate")
            else:
                return value
        if FIELD__DEFAULT_PROPERTY[FID]["TYPE"] == bytes: # convert string with IPv6 address to bytes
            if type(value) is str:
                slash_pos = value.find("/")
                if slash_pos != -1:
                    # a prefix is given, remove / to be compatible with ip_address
                    value = value[:slash_pos]

                addr = ipaddress.ip_address(value)
                if addr.version != 6: # expect an IPv6 address
                    ValueError ("{} only IPv6 is supported")

                if FID in [T_IPV6_DEV_PREFIX, T_IPV6_APP_PREFIX]: #prefix top 8
                    return addr.packed[:8]
                elif FID in [T_IPV6_DEV_IID, T_IPV6_APP_IID]: #IID bottom 8
                    return addr.packed[8:]
                else:
                    ValueError ("{} Fid not found".format(FID))
            elif type(value) is int:
                return (value).to_bytes(8, byteorder="big")

    def _create_rule (self, nrule):
        """
        parse a rule to verify values and fill defaults
        """
        arule = {}

        arule["RuleID"] = nrule["RuleID"]
        arule["RuleLength"] = nrule["RuleLength"]
        arule["Compression"] = []

        for r in nrule["Compression"]:
            assert(r["FID"] in FIELD__DEFAULT_PROPERTY)

            entry = {}
            FID = r[T_FID].upper()
            entry[T_FID] = FID
            entry[T_FL] = self._return_default(r, T_FL, FIELD__DEFAULT_PROPERTY[FID][T_FL])
            entry[T_FP] = self._return_default(r, T_FP, 1)
            entry[T_DI] = self._return_default(r, T_DI, T_DIR_BI)

            MO = r[T_MO].upper()
            if MO in [T_MO_EQUAL, T_MO_MSB, T_MO_IGNORE]:
                if MO == T_MO_MSB:
                    if T_MO_VAL in r:
                        entry[T_MO_VAL] = r[T_MO_VAL]
                    else:
                        ValueError ("MO Value missing for {}".format(FID))

                if T_TV in  r:
                    entry[T_TV] = self._adapt_value(FID, r[T_TV])

            elif MO == T_MO_MMAP:
                entry[T_TV] = []
                for e in r[T_TV]:
                    entry[T_TV].append(self._adapt_value(FID, e))

            else:
                ValueError("{} MO unknown".format(MO))
            entry[T_MO] = MO

            CDA = r[T_CDA].upper()
            if not CDA in [T_CDA_NOT_SENT, T_CDA_VAL_SENT, T_CDA_MAP_SENT, T_CDA_LSB, T_CDA_COMP_LEN, T_CDA_COMP_CKSUM]:
                ValueError("{} CDA not found".format(CDA))
            entry[T_CDA] = CDA

            arule["Compression"].append(entry)

        return arule


    def __init__(self, file=None, log=None):
        #RM database
        self._ctxt = []
        self._log = log


    def _smart_print(self, v):
        if type(v) is str:
            v = '"'+v+'"'
            print ('{:<30}'.format(v), end="")
        elif type(v) is int:
            print ('{:>30}'.format(v), end="")
        elif type(v) is bytes:
            print ('{:>30}'.format(v.hex()), end="")

    def Print (self):
        """
        Print a context
        """
        for dev in self._ctxt:
            print ("*"*40)
            print ("Device:", dev["DeviceID"])

            for rule in dev["SoR"]:
                print ("/" + "-"*25 + "\\")
                txt = str(rule["RuleID"])+"/"+ str(rule["RuleLength"])
                print ("|Rule {:8}  {:10}|".format(txt, bin(rule["RuleID"])))
                if "Compression" in rule:

                    print ("|" + "-"*15 + "+" + "-"*3 + "+" + "-"*2 + "+" + "-"*2 + "+" + "-"*30 + "+" + "-"*13 + "+" + "-"*16 +"\\")
                    for e in rule["Compression"]:
                        print ("|{:<15s}|{:>3}|{:2}|{:2}|".format(e[T_FID], e[T_FL], e[T_FP], e[T_DI]), end='')
                        if 'TV' in e:
                            if type(e[T_TV]) is list:
                                self._smart_print(e[T_TV][0])
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
        return "Rule {}/{}:".format(r["ruleID"], r["ruleLength"])

    def find_rule_bypacket(self, context, packet_bbuf):
        """ returns a compression rule or an fragmentation rule
        in the context matching with the field value of rule id in the packet.
        """
        for k in ["fragSender", "fragReceiver", "comp"]:
            r = context.get(k)
            if r is not None:
                rule_id = packet_bbuf.get_bits(r["ruleLength"], position=0)
                if r["ruleID"] == rule_id:
                    return k, r
        return None, None

    def find_context_bydevL2addr(self, dev_L2addr):
        """ find a context with dev_L2addr. """
        # XXX needs to implement wildcard search or something like that.
        for c in self._db:
            if c["devL2Addr"] == dev_L2addr:
                return c
            if c["devL2Addr"] == "*":
                return c
        return None

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

        if not "ruleID" in rule:
           raise ValueError ("Rule ID not defined.")

        if not "ruleLength" in rule:
            if rule["ruleID"] < 255:
                rule["ruleLength"] = 8
            else:
                raise ValueError ("RuleID too large for default size on a byte")

        # proceed to compression check (TBD)
        if key == "comp":
            self.check_rule_compression(rule)
        elif key in ["fragSender", "fragReceiver", "comp"]:
            self.check_rule_fragmentation(rule)
        else:
            raise ValueError ("key must be either comp, fragSender, fragReceiver")

        rule_id = rule["ruleID"]
        rule_id_length = rule["ruleLength"]

        self._checkRuleValue(rule_id, rule_id_length)

        for k in ["fragSender", "fragReceiver", "comp"]:
            r = context.get(k)
            if r is not None:
                if rule_id_length == r.ruleLength and rule_id == r.ruleID:
                    raise ValueError ("Rule {}/{} exists".format(
                            rule_id, rule_id_length))

        context[key] = DictToAttrDeep(**rule)

    def check_rule_compression(self, rule):
        """ compression rule check """
        # XXX need more work.
        if (not "compression" in rule or "fragmentation" in rule):
            raise ValueError ("{} Invalid rule".format(self._nameRule(rule)))

        canon_rule_set = []
        if "rule_set" not in rule["compression"]:
            raise ValueError ("compression must have a rule_set.")
        for r in rule["compression"]["rule_set"]:
            canon_r = {}
            for k,v in r.items():
                if isinstance(v, str):
                    canon_r[k.upper()] = v.upper()
                else:
                    canon_r[k.upper()] = v
            canon_rule_set.append(canon_r)
        rule["compression"]["rule_set"] = canon_rule_set

    def check_rule_fragmentation(self, rule):
        """ fragmentation rule check """
        if (not "fragmentation" in rule or "compression" in rule):
            raise ValueError ("{} Invalid rule".format(self._nameRule(rule)))

        if "fragmentation" in rule:
            fragRule = rule["fragmentation"]

            if not "FRMode" in fragRule:
                raise ValueError ("{} Fragmentation mode must be specified".format(self._nameRule(rule)))

            mode = fragRule["FRMode"]

            if not mode in ("noAck", "ackAlways", "ackOnError"):
                raise ValueError ("{} Unknown fragmentation mode".format(self._nameRule(rule)))

            if not "FRModeProfile" in fragRule:
                fragRule["FRModeProfile"] = {}

            profile = fragRule["FRModeProfile"]

            if not "dtagSize" in profile:
                profile["dtagSize"] = 0

            if not "WSize" in profile:
                if  mode == "noAck":
                    profile["WSize"] = 0
                elif  mode == "ackAlways":
                    profile["WSize"] = 1
                elif mode == "ackOnError":
                    profile["WSize"] = 5

            if not "FCNSize" in profile:
                if mode == "noAck":
                    profile["FCNSize"] = 1
                elif mode == "ackAlways":
                    profile["FCNSize"] = 3
                elif mode == "ackOnError":
                    profile["FCNSize"] = 3

            if "windowSize" in profile:
                if profile["windowSize"] > (0x01 << profile["FCNSize"]) - 1 or\
                   profile["windowSize"] < 0:
                    raise ValueError ("{} illegal windowSize".format(self._nameRule(rule)))
            else:
                profile["windowSize"] = (0x01 << profile["FCNSize"]) - 1

            if mode == "ackOnError":
                if not "ackBehavior" in profile:
                    raise ValueError ("Ack on error behavior must be specified (afterAll1 or afterAll0)")
                if not "tileSize" in profile:
                    profile["tileSize"] = 64
