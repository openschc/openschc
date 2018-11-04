""""
This module is used to manage rules. A rule is defined in JSON and is uniquely
identified by a rule ID of variable length.

Each rule must contains the following informations:

{
  "ruleID" : 2,
  "ruleLength" : 3
}

where ruleID contains the rule ID value aligned on the right and ruleLength gives 
the size in bits of the ruleID. In the previous example, this correspond to the 
binary value 0b010.

The rule is either a compression/decompression rule or a fragmentation/reassembly
rule.

This C/D rules, the keyword "fragmentation" must be defined. For F/R rules, the
keyword "compression" must be used.

For instance:
{
  "ruleID" : 14,
  "ruleLength" : 4   # rule 0b1110
  "fragmentation": <<<rule>>>
}

where <<<rule>>> will be defined later.

{
  "ruleID" : 15,
  "ruleLength" : 4   # rule 0b1110
  "compression": {
      "dtagSize" : 1,
      "windowSize": 3,
      "FCNSize" : 3,
      "noAck" : {},
      "ackAlways": {},
      "ackOnError" : {
         "ackBehavior": "afterAll1"
      }
  }
}

The "compression" keyword is used to gives compression paramters and profile:
- dtagSize, windowSize and FCNSize are used to define the SCHC fragmentation header
- one and only one fragmentation mode keywork "noAck", "ackAlways" or "ackOnError".
  These keywords are used to define some specific paramters for this mode. 
  For "ackOnError" the following parameter is defined:
  - "ackBehavior" defined the ack behavior, i.e. when the Ack must be spontaneously sent
    by the receiver and therefore when the sender must listen for Ack.
    - "afterAll0" means that the sender waits for ack after sending an All-0
    - "afterAll1" means that the sender waits only after sending the last fragment
    - other behaviors may be defined in the future.     
"""

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
        r1 = r1ID << (32-r1l)
        r2 = r2ID << (32-r2l)
        l  = min(r1l, r2l)

#        print ("{0:33b}".format(r1))
 #       print ("{0:33b}".format(r2))
        
        for k in range (32-l, 32):
            if ((r1 & (0x01 << k)) != (r2 & (0x01 << k))):
                return False

        return True

        
    def findRuleByID (self, rID, rIDl):
        for r in self._db:
            print("->", r)
            if rIDl == r["ruleLenght"] and rID == r["ruleID"]:
                return r
            
        return None
    
    def add (self, rule):
        """ Check rule integrity and uniqueless and add it to the db """

        if not "ruleID" in rule or not "ruleLength" in rule:
           raise ValueError ("ruleID not defined")

        if (not "compression" in rule and not "fragmentation" in rule) or \
           ("compression" in rule and "fragmentation" in rule):
            raise ValueError ("Invalid rule")

        # proceed to compression check (TBD)

        # proceed to fragmentation check

        if "fragmentation" in rule:
            fragRule = rule["fragmentation"]

        rID = rule["ruleID"]
        rLength = rule["ruleLength"]

        self._checkRuleValue(rID, rLength)

        for r in self._db:
            if self._ruleIncluded(rID, rLength, r["ruleID"], r["ruleLength"]):
                raise ValueError ("Rule {}/{} in conflict with {}/{}".format(rID, rLength, r["ruleID"], r["ruleLength"]))
            

        self._db.append(rule)

if __name__ == "__main__":
    bogusRule0 = { # bogus rule with no ruleLength
        "ruleID": 3
        }
    rule1 = {
        "ruleID" : 7,
        "ruleLength" : 3,
        "compression" : {},
        }
    rule2 = {
        "ruleID" : 4,
        "ruleLength" : 3,
        "compression" : {},
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
    RM.add(conflictingRule0)
    
