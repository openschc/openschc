""""
This module is used to manage rules. A rule is defined in JSON and is uniquely
identified by a rule ID of variable length.

Each rule must contain the following information:

{
  "ruleID" : 2,
  "ruleLength" : 3
}

where ruleID contains the rule ID value aligned on the right and ruleLength gives 
the size in bits of the ruleID. In the previous example, this corresponds to the 
binary value 0b010.

if ruleLength is not specified the value is set to 1 byte.

The rule is either a compression/decompression rule or a fragmentation/reassembly
rule.

For C/D rules, the keyword "compression" must be defined. For F/R rules, the
keyword "fragmentation" must be defined.

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
      "mode" : "noAck" # or "ackAlways", "ackOnError"
      "profile" : {
         "dtagSize" : 1, 
         "windowSize": 3,
         "FCNSize" : 3,
         "maxWindFCN", 6,
         "ackBehavior": "afterAll1"
      }
  }
}

The "fragmentation" keyword is used to give fragmentation mode and profile:
- one fragmentation mode keywork "noAck", "ackAlways" or "ackOnError".
- Profile parameters. Default values are automaticaly added.
- dtagSize, windowSize and FCNSize are used to define the SCHC fragmentation header
- maxWindFCN can be added if not 2^FCNSize - 2 
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

class RuleManager:
    """RuleManager class is used to manage Compression/Decompression and Fragmentation/
    Reassembly rules."""

    def __init__(self):
        self._db = []    #RM database


    def _checkRuleValue(self, rID, rLength):
        """this function looks if bits specified in ruleID are not outside of rLength"""

        if rLength > 32:
            raise ValueError("Rule length should be less than 32")

        r1 = rID

        for k in range (32, rLength, -1):
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

    def _nameRule (r):
        return "Rule {}/{}:".format(r["ruleID"], r["ruleLength"])
        
    def findRuleByID (self, rID, rIDl):
        """ returns a rule identified by its ruleID and ruleLength, returns none otherwise """
        for r in self._db:
            if rIDl == r["ruleLength"] and rID == r["ruleID"]:
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

        if (not "compression" in rule and not "fragmentation" in rule) or \
           ("compression" in rule and "fragmentation" in rule):
            raise ValueError ("{} Invalid rule".format(self._nameRule(rule)))

        # proceed to compression check (TBD)
                              
        # proceed to fragmentation check

        if "fragmentation" in rule:
            fragRule = rule["fragmentation"]

            if not "mode" in fragRule:
                raise ValueError ("{} Fragmentation mode must be specified".format(self._nameRule(rule)))

            mode = fragRule["mode"]

            if not mode in ("noAck", "ackAlways", "ackOnError"):
                raise ValueError ("{} Unknown fragmentation mode".format(self._nameRule(rule)))

            if not "profile" in fragRule:
                fragRule["profile"] = {}

            profile = fragRule["profile"]
                              
            if not "dtagSize" in profile:
                profile["dtagSize"] = 0
                
            if not "windowSize" in profile:
                if  mode == "noAck":
                    profile["windowSize"] = 0
                elif  mode == "ackAlways":
                    profile["windowSize"] = 1
                elif mode == "ackOnError":
                    profile["windowSize"] = 5
                    
            if not "FCNSize" in profile:
                if mode == "noAck":
                    profile["FCNSize"] = 1
                elif mode == "ackAlways":
                    profile["FCNSize"] = 3
                elif mode == "ackOnError":
                    profile["FCNSize"] = 3

            if "maxWindFCN" in profile:
                if profile["maxWindFCN"] > (0x01 << profile["FCNSize"]) - 2 or\
                   profile["maxWindFCN"] < 0:
                    raise ValueError ("{} illegal maxWindFCN".format(self._nameRule(rule)))
            else:
                profile["maxWindFCN"] = (0x01 << profile["FCNSize"]) - 2 
                    
            if mode == "ackOnError":
                if not "ackBehavior" in profile:
                    raise ValueError ("Ack on error behavior must be specified (afterAll1 or afterAll0)")
                if not "tileSize" in profile:
                    profile["tileSize"] = 64
                    
        rID = rule["ruleID"]
        rLength = rule["ruleLength"]

        self._checkRuleValue(rID, rLength)

        for r in self._db:
            if self._ruleIncluded(rID, rLength, r["ruleID"], r["ruleLength"]):
                raise ValueError ("{} in conflict with {}/{}".format(self._nameRule(rule), r["ruleID"], r["ruleLength"]))
            

        self._db.append(rule)

if __name__ == "__main__":
    bogusRule0 = { # bogus rule with no frag or comp
        "ruleID": 3
        }
    rule1 = {
        "ruleID" : 7,
        "fragmentation" : {
            "mode" :"noAck"
        },
    }
    rule2 = {
        "ruleID" : 4,
        "ruleLength" : 3,
        "fragmentation" : {
            "mode": "ackOnError",
            "profile": {
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
    print (RM._db)
    #RM.add(conflictingRule0)
    print(RM.findRuleByID(4, 3))
