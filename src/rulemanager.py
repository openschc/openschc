"""
This module is used to manage rules.

## Base format

Context is define in JSON.
Rule is as well.

Each key must be unique through a rule.
For example, below the keys of "profile" are not allowed.

    {
        "profile": { ... },
        "compression": { "profile": ... }
    }

One Context is uniquely identified by the set of devL2Addr and dstIID.
devL2Addr specify the L2 address of the device.
dstIID specify the IPv6 address of the communication peer.
It's the address of the application node in the configuration at the device,
and the address of the device in the configuration at the CD/FR middle box.
"*" and "/" can be used for a wild-card match.

    {
        "devL2Addr": "aabbccdd"
        "dstIID": "2001:0db8:85a3:0000::/64"
    }

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
For C/D rules, the keyword "compression" must be defined. For F/R rules, the
keyword "fragmentation" must be defined.
In other words, either "compression" or "fragmentation" must exist in a rule.
Both keys must not exists.

For instance:

    {
      "ruleID" : 14,
      "ruleLength" : 4   # rule 0b1110
      "compression": <<<rule>>>
    }

where <<<rule>>> will be defined later.

    {
      "ruleID" : 15,
      "ruleLength" : 4   # rule 0b1110
      "fragmentation": {
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
"""

try:
    import struct
except ImportError:
    import ustruct as struct

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
        self._db = []    #RM database

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

    def findRuleByID (self, rule_id, rule_id_length):
        """ returns a rule identified by its ruleID and ruleLength, returns none otherwise """
        for r in self._db:
            if rule_id_length == r.ruleLength and rule_id == r.ruleID:
                return r
        return None

    def findRuleByRemoteID (self, remote_id):
        """ returns a rule identified by the identifier of the communication
        end, returns none otherwise """
        # XXX needs to implement wildcard search or something like that.
        for r in self._db:
            id_db = r.get("remoteID")
            if id_db is None:
                continue
            if id_db == "*":
                return r
            if remote_id == id_db:
                return r
        return None

    def findRuleByPacket (self, remote_id, packet_bbuf):
        """ returns a rule identified by the identifier of the communication
        end AND the rule id in the packet, returns none otherwise """
        # XXX needs to implement wildcard search or something like that.
        for r in self._db:
            id_db = r.get("remoteID")
            if id_db is None:
                continue
            if id_db == "*":
                rule_id = packet_bbuf.get_bits(r["ruleLength"], position=0)
                if r["ruleID"] == rule_id:
                    return r
            if remote_id == id_db:
                rule_id = packet_bbuf.get_bits(r["ruleLength"], position=0)
                if r["ruleID"] == rule_id:
                    return r
        return None

    def add (self, rule):
        """ Check rule integrity and uniqueless and add it to the db """

        if not "ruleID" in rule:
           raise ValueError ("Rule ID  not defined.")

        if not "ruleLength" in rule:
            if rule["ruleID"] < 255:
                rule["ruleLength"] = 8
            else:
                raise ValueError ("RuleID too large for default size on a byte")

        # XXX localID, remoteID processing

        if (not "compression" in rule and not "fragmentation" in rule) or \
           ("compression" in rule and "fragmentation" in rule):
            raise ValueError ("{} Invalid rule".format(self._nameRule(rule)))

        # proceed to compression check (TBD)

        # proceed to fragmentation check

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

        rule_id = rule["ruleID"]
        rule_id_length = rule["ruleLength"]

        self._checkRuleValue(rule_id, rule_id_length)

        for r in self._db:
            if self._ruleIncluded(rule_id, rule_id_length, r.ruleID, r.ruleLength):
                raise ValueError ("{} in conflict with {}/{}".format(
                        self._nameRule(rule), r.ruleID, rruleLength))

        self._db.append(DictToAttrDeep(**rule))

if __name__ == "__main__":
    bogusRule0 = { # bogus rule with no frag or comp
        "ruleID": 3
        }
    rule1 = {
        "ruleID" : 7,
        #"remoteID": "e2:92:00:01",
        "remoteID": bytearray(b"\xe2\x92\x00\x01"),
        "fragmentation" : {
            "FRMode" :"noAck"
        },
    }
    rule2 = {
        "ruleID" : 4,
        "ruleLength" : 3,
        "remoteID": "*",
        "profile": {
            "MICAlgorithm": "crc32",
            "MICWordSize": 8,
            "L2WordSize": 8
        },
        "fragmentation" : {
            "FRMode": "ackOnError",
            "FRModeProfile": {
                "dtagSize" : 2,
                "FCNSize": 3,
                "ackBehavior" : "afterAll1"
            }
        },
    }
    conflictingRule0 = {
        "ruleID" : 15,
        "ruleLength" : 4,
        "compression" : {},
        }

    RM = RuleManager()
    RM.add(rule1)
    RM.add(rule2)
    print(RM._db)
    RM.add(conflictingRule0)
    print(RM.findRuleByID(4, 3))
    print(RM.findRuleByRemoteID(bytearray(b"\xe2\x92\x00\x01")))
    from bitarray import BitBuffer
    print(RM.findRuleByPacket(bytearray(b"\x00\x01\x02\x03"),
                              BitBuffer(int("10000111",2).to_bytes(1, "big"))))
