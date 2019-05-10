# Introduction

A context is defined as a set of rules shared by both ends. Rules are identical and can be
copy/paste from one end to the other end, if they respect the same format.

This document specify the openschc data model based on JSON. 

# Rule definition

A rule is identified through a ruleID, the size of the ruleID can change from one rule to
another one, therefore a Rulelength has to be also specified to indicate the length in bits.
Both fields are numerical.


 	{
 		"RuleID" : 12,
 		"RuleLength" : 4
    }
 
 ## Compression Rules
 
Compression rules include a list of field description as defined in SCHC specification. 
The rule defines the order in which the compression residues are sent therefore an array is used.
The field description contains elements defined in SCHC specification:
* "FID" : identifies the field ID, the Parser must use the same notation.
* "FL"  : indicates either a size in bit if the value is a number or a function if the 
value is a string. Current functions are:
  * "var" : the field is of variable length and the length in byte is sent in the compression residue.
  * "tkl" : this function is specific for encoding CoAP Token. The token length is given by the CoAP Token length field.
* "FP" : give the position in the header, by default the value is 1, each time the field is repeated in the header, the value is increased by 1. 
* "TV" : specifies the Target Value. The value is either a number, a string or an array of these values. "TV" can be avoided or set to None is there is no value to check, for instance "ignore" MO.In an array the value None indicate that 
the field is not present in a header.  
* "MO" : is pointing on the Matching Operator. It is a string that can take the following values:
  * "ignore" : the field must be present in the header, but the value is not checked.
  * "equal" : type and value must check between the filed value and the target value
  * "MSB": most significant bits of the target value must check with the most significant bits of the field value. The size of the check is given by the "MOa" field.

  
     
 
 
 ## Fragmentation Rules
 
 
 # Context
 
 A context is associated to a specific device which may be identify by a unique LPWAN 
 identifier, for instance a LoRaWAN devEUI.
 

 # RuleManager 
 
 Rule manager manage contexts for a specific device or a set of devices. 
 
 
 ## Class RuleManager
 
 
 
### Add 
 
 Add is used to add a new rule to a context. Add check the validity of the rule:
 * ruleID/RuleLength do not overlap
 * contain either a single fragmentation or compression description. 
 
 Add compute some internal value to help the compression. 
 
 
### Remove
 
 
###FindRuleFromPacket

 this method returns a rule that match with a packet description
 
### FindFragmentationRule (size)

 return a fragmentation rule regarding the packet size.
 
 
### FindRuleFormID

giving the first bits received from the LPWAN return either a fragmentation or compression rule.
