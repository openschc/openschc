# Introduction

A context is defined as a set of rules shared by both ends. Rules are identical and can be
copy/paste from one end to the other end, if they respect the same format.

This document specifies the openschc rule data model based on JSON. 

# Rule definition

A rule is identified through a ruleID, the size of the ruleID can change from one rule to
another one, therefore a Rulelength has to be also specified to indicate the length in bits.

Both fields are numerical.


 	{
 		"RuleID" : 12,
 		"RuleLength" : 4
    }
    
A rule can  either  be for compression or fragmentation. One these two keywords "fragmentation" or "compression" must be specified.
 
 ## Compression Rules
 
Compression rules include a list of field description as defined in SCHC specification. 
The rule defines the order in which the compression residues are sent therefore an array is used.
The field description contains elements defined in SCHC specification:
* "**FID**" : identifies the field ID, the Parser must use the same notation.
* "**FL**"  : indicates either a size in bit if the value is a number or a function if the 
value is a string. Current functions are:
  * "_**var**_" : the field is of variable length and the length in byte is sent in the compression residue.
  * "_**tkl**_" : this function is specific for encoding CoAP Token. The token length is given by the CoAP Token length field.
* "**FP**" : gives the position in the header, by default the value is 1, each time the field is repeated in the header, the value is increased by 1. 
* "**DI**" : tells the expected direction:
    * "_**Bi**_" for bidrectional field
    * "_**Up**_" for field sent only on uplink messages (from device to network)
    * "_**Dw**_" for field sent only on downlink messages (from network to device)
    
* "**TV**" : specifies the Target Value. The value is either a number, a string or an array of these types. "TV" can be avoided or set to None is there is no value to check, for instance "ignore" MO.In an array the value None indicate that 
the field is not present in a header.  
* "**MO**" : is pointing on the Matching Operator. It is a string that can take the following keyword:
  * "_**ignore**_" : the field must be present in the header, but the value is not checked.
  * "_**equal**_" : type and value must check between the filed value and the target value
  * "_**MSB**_": most significant bits of the target value are checked with the most significant bits of the field value. The size of the check is given by the "MOa" field.
  * "_**match-mapping**_": the target value must be an array and one element in type and value match with the field value.
* "**MOa**" : contains, if necessary, the MO argument. This currently apply to "MSB" where the argument specifies in bits the length of the matching.
* "**CDA**" : designates the Compression/Decompression Action. It is a string containing the following keywords:
   * "_**not-sent**_" : the field value is not sent as a residue.
   * "_**value-sent**_" : the field value is integrally sent on the residue. 
   * "_**LSB**_" : the remaining bits of the MSB comparison are sent as residues.
   * "_**mapping-sent**_" : the index of the array is sent.
   * "_**compute**_" : field is not sent in residue and receiver can recover the value from existing parameters. This is generally used for length and checksum.
* "**CDAa**" : represents the argument of the CDA. Currently no CDAa are defined.
  
For example: 

	
  	{
 		"RuleID" : 12,
 		"RuleLength" : 4, 
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
	}
			
			
## Fragmentation Rules
 
 
 # Context
 
 A context is associated to a specific device which may be identify by a unique LPWAN 
 identifier, for instance a LoRaWAN devEUI. 
 
 Two each devices is associated a set of rules, the rule structure is defined previously. 
 
      [
       	{
 	    	"RuleID" : 12,
 	     	"RuleLength" : 4, 
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
 		    "RuleLength" : 4, 
 	     	"framentation ": ....
	    },
	    .....
   ]
 
 The context consists on the association of this set of rule to a device ID. 
 
      [
          { 
            "deviceID": 0x1234567890,
            "sor" : [ ..... ]
          }
      ]
 
deviceID is a numerical value that must be unique in the context. If the context is used on a device, the deviceID may be omitted and set ton None. In the core network, the deviceIDs must be specified. 
 

 # RuleManager 
 
 Rule manager manage contexts for a specific device or a set of devices. It maintains the context database and its consistency. 
 
 
 ## Class RuleManager
 
 A RuleManager object is created this way:
 
      from RuleManager import *
      RM = RuleManager() 
 
### Add 
 
 Add is used to add a new rule to a context. Add check the validity of the rule:
 * ruleID/RuleLength do not overlap
 * contain either a single fragmentation or compression description. 
 
 if the deviceID already exists in the context, the new set of rules is added if no conflict on the rule ID is found.
 
      RM.add ({"deviceID": 0x1234567, "sor": [.....]}) 
 
### Remove

Suppress a rule for a specific device, if no rule is specified, the device is removed from the context.

      RM.add ({"deviceID": 0x1234567, "sor": [{"ruleID":12, "ruleLength":4}]}) 
      RM.add ({"deviceID": 0x1234567}) 
 
### FindRuleFromPacket

This method returns a rule and a deviceID that match with a packet description given by the Parser. 
 
### FindFragmentationRule (size)

 return a fragmentation rule regarding the packet size.
 
 
### FindRuleFormID

giving the first bits received from the LPWAN return either a fragmentation or compression rule.
