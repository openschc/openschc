""""
This module is used to manage rules. A rule is defined in JSON and is uniquely
identified by a rule ID of variable length.

Each rule must contains the following informations:

{
  "ruleID" : 2,
  "ruleLenght" : 3
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
  "ruleLenght" : 4   # rule 0b1110
  "fragmentation": <<<rule>>>
}

where <<<rule>>> will be defined later.

{
  "ruleID" : 15,
  "ruleLenght" : 4   # rule 0b1110
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




""""
