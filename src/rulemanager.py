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

The rule is either a compression/decompression rule or a fragmentation/reassembly
rule.

For C/D rules, the keyword "compression" must be defined. For F/R rules, the
keyword "fragmentation" must be defined.

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
  "fragmentation": {
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

The "fragmentation" keyword is used to give fragmentation parameters and profile:
- dtagSize, windowSize and FCNSize are used to define the SCHC fragmentation header
- one and only one fragmentation mode keywork "noAck", "ackAlways" or "ackOnError".
  These keywords are used to define some specific parameters for this mode. 
  For "ackOnError" the following parameter is defined:
  - "ackBehavior" defined the ack behavior, i.e. when the Ack must be spontaneously sent
    by the receiver and therefore when the sender must listen for Ack.
    - "afterAll0" means that the sender waits for ack after sending an All-0
    - "afterAll1" means that the sender waits only after sending the last fragment
    - other behaviors may be defined in the future.     




""""
