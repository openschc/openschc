"""
This module is used to manage rules.

## Base format

A context and rule is written in JSON.

A context contains an identifier, AND one or three rules.
One of rules must specify the SCHC Compression/Decompression (CD).
Two specify SCHC Fragmentation/Reassembly (FR) if needed.

Therefore, a context has to be formed to either below structures.

    {
        "devL2Addr": ...,
        "dstIID": ...,
        "comp": { ... },
        "fragSender": { ... },
        "fragReceiver": { ... }
    }

    "comp": compression rule.
    "fragSender": fragmentation rule for inbound.
    "fragReceiver": fragmentation rule for outbound.

Or,

    {
        "devL2Addr": ...,
        "dstIID": ...,
        "profile": { ... },
        "comp": { ... }
    }

XXX Q. "profile" should be in the context ?

## Context

A context is uniquely identified by devL2Addr
specifying the L2 address of a SCHC device.

dstIID matches the IP address assigned
to the interface of the communication peer.
In the context of the SCHC device, dstIID indicates the IP address of
the interface at the SCHC Translator,
which is dedicated between the device and
the application.
In the context of the other side, dstIID indicates the IP address of
the SCHC device.

    +--------+                       +------------+         +-----+
    |  SCHC  |                       |    SCHC    |---------| App |
    | Device |                       | Translator |         |     |
    +--------+                       +------------+         +-----+
         | D (IP addr)                     | T (IP addr)
         | L (L2 addr)                     |
         |                                 |
         +--// LPWAN //--| GW |------------+

In the above example, the context of each side is like below:

    at the device:

    {
        "devL2Addr": "L",
        "dstIID": "M"
    }

    at the translator:

    {
        "devL2Addr": "L",
        "dstIID": "D"
    }

"*" and "/" can be used for a wild-card match. (XXX should be implemented.)

## Rule

XXX is it true that both ruleID and ruleLength is unique key ?
XXX is the deivce L2 address the real key ?

A rule is uniquely identified by the rule ID of variable length.
Each rule must contain the following information:

    {
      "ruleID" : 2,
      "ruleLength" : 3
    }

where ruleID contains the rule ID value aligned on the right and ruleLength
gives
the size in bits of the ruleID. In the previous example, this corresponds to
the binary value 0b010.
if ruleLength is not specified the value is set to 1 byte.

The rule is either a compression/decompression rule
or a fragmentation/reassembly rule.
For C/D rules, the keyword "compression" must be defined.
For F/R rules, the keyword "fragmentation" and "fragmentation"
must be defined.

## Compression Rule

A compression rule is bidirectionnal.

## Fragmentation Rule

A fragmentation rule is uni directionnal.

The "fragmentation" keyword is used to give fragmentation mode and profile:
- one fragmentation mode keywork "noAck", "ackAlways" or "ackOnError".
- FRModeProfile parameters. Default values are automaticaly added.
- dtagSize, WSize and FCNSize are used to define the SCHC fragmentation header
- windowSize can be added if not 2^FCNSize - 1
  For "ackOnError" the following parameter is defined:
  - "ackBehavior" defined the ack behavior, i.e. when the Ack must be spontaneously sent
    by the receiver and therefore when the sender must listen for Ack.
    - "afterAll0" means that the sender waits for ack after sending an All-0
    - "afterAll1" means that the sender waits only after sending the last fragment
    - other behaviors may be defined in the future.

## data model of DB

    db = [
        {
            "devL2Addr": ..,
            "dstIID": ..,
            "comp": {
                    "ruleID": ..,
                    "ruleLength": ..,
                    "compression": { ...}
                },
            "fragSender": {
                    "ruleID": ..,
                    "ruleLength": ..,
                    "fragmentation": { ...}
                }
            "fragReceiver": {
                    "ruleID": ..,
                    "ruleLength": ..,
                    "fragmentation": { ...}
                }
        }, ...
    ]

## method

- add_context(context, comp=None, fragSender=None, fragReceiver=None)

    It adds the context.  If it exists, raise ValueError.

- add_rules(context, comp=None, fragSender=None, fragReceiver=None)

    It adds the list of rules into the context specified.
    If it exists, raise ValueError.
    If context is not specified, the rule will be added into the default
    context.

## Rule to add a new key

Each key must be unique through a rule.
For example, below the keys of "profile" are not allowed.

    {
        "profile": { ... },
        "compression": { "profile": ... }
    }

## Examples

Example 1:

    {
      "ruleID" : 14,
      "ruleLength" : 4   # rule 0b1110
      "compression": { ... }
    }

Example 2:

    {
      "ruleID" : 15,
      "ruleLength" : 4   # rule 0b1110
      "fragmentationOut": {
          "FRMode" : "noAck" # or "ackAlways", "ackOnError"
          "FRModeProfile" : {
             "dtagSize" : 1,
             "WSize": 3,
             "FCNSize" : 3,
             "windowSize", 7,
             "ackBehavior": "afterAll1"
          }
      }
    }

"""

try:
    import struct
except ImportError:
    import ustruct as struct

from copy import deepcopy

# XXX to be checked whether they are needed.
DEFAULT_FRAGMENT_RID = 1
DEFAULT_L2_SIZE = 8
DEFAULT_RECV_BUFSIZE = 512
DEFAULT_TIMER_T1 = 5
DEFAULT_TIMER_T2 = 10
DEFAULT_TIMER_T3 = 10
DEFAULT_TIMER_T4 = 12
DEFAULT_TIMER_T5 = 14

class DictToAttrDeep:

    def __init__(self, **entries):
        self.__update(**entries)

    def __update(self, **entries):
        for k,v in entries.items():
            if isinstance(v, dict):
                self.__dict__[k] = DictToAttrDeep(**v)
            else:
                self.__dict__.update(entries)

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
    """RuleManager class is used to manage Compression/Decompression and Fragmentation/
    Reassembly rules."""

    def __init__(self):
        #RM database
        self._db = []

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
        for k in ["fragSender", "fragReceiver","fragSender2", "fragReceiver2", "comp"]:
            r = context.get(k)
            if r is not None:
                rule_id = packet_bbuf.get_bits(r["ruleLength"],position=0)
                if r["ruleID"] == rule_id:
                    print("--------------------RuleManage------------------")
                    print("ruleID ",rule_id)
                    print()
                    print("--------------------------------------------------")
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

    def add_context(self, context, comp=None, fragSender=None, fragReceiver=None, fragSender2=None, fragReceiver2=None):
        
        """ add context into the db. """
        if self.find_context_exact(context["devL2Addr"],context["dstIID"]) is not None:
            raise ValueError("the context {}/{} exist.".format(
                context["devL2Addr"], context["dstIID"]))
        # add context
        c = deepcopy(context)
        self._db.append(c)
        self.add_rules(c, comp, fragSender, fragReceiver, fragSender2, fragReceiver2)

    def add_rules(self, context, comp=None, fragSender=None, fragReceiver=None, fragSender2=None, fragReceiver2=None):
        """ add rules into the context specified. """
        if comp is not None:
            self.add_rule(context, "comp", comp)
        if fragSender is not None:
            self.add_rule(context, "fragSender", fragSender)
        if fragReceiver is not None:
            self.add_rule(context, "fragReceiver", fragReceiver)
        if fragSender2 is not None:
            self.add_rule(context, "fragSender2", fragSender2)
        if fragReceiver2 is not None:
            self.add_rule(context, "fragReceiver2", fragReceiver2)

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
        elif key in ["fragSender", "fragReceiver","fragSender2", "fragReceiver2", "comp"]:
            self.check_rule_fragmentation(rule)
        else:
            raise ValueError ("key must be either comp, fragSender, fragReceiver, fragSender2, fragReceiver2")

        rule_id = rule["ruleID"]
        rule_id_length = rule["ruleLength"]

        self._checkRuleValue(rule_id, rule_id_length)

        for k in ["fragSender", "fragReceiver","fragSender2", "fragReceiver2", "comp"]:
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

