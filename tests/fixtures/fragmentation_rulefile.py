import sys
sys.path.append('../src')

import pytest
import logging
import tempfile


#============================ fixtures ========================================
RuleId= {
    "TWELVE": "12",
    "HUNDRED": "100",
    "DOUBLENINE": "99",
    "LETTERS": "M",
    "SYMBOL": "$",
    "NONE": ""
}
RuleIdLength= {
    "SIX": "6",
    "TWELVE": "12",
    "HUNDRED": "100",
    "LETTERS": "M",
    "SYMBOL": "$",
    "NONE": ""
}
FragmentationMode= {
    "NOACK": "NoAck",
    "ACKALWAYS": "AckAlways",
    "ACKONERROR": "AckOnError",
    "NONE": ""
}
FragmentationDirection= {
    "UP": "UP",
    "DOWN": "DW",
    "BOTH": "BT",
    "NONE": ""
}

def generateFragmentationSection(FRMode="NOACK", FRDir="DOWN"):
    frag_gen =  f"""            "FRMode":{FragmentationMode.get(FRMode)},
            "FRDirection" : {FragmentationDirection.get(FRDir)}"""
    if FRMode=="ACKONERROR":
        frag_gen = frag_gen+""",
            "FRModeProfile":{
                "dtagSize":2,
                "WSize":3,
                "FCNSize":3,
                "ackBehavior":"afterAll1",
                "tileSize":392,
                "MICAlgorithm":"RCS_RFC8724",
                "MICWordSize":8,
                "lastTileInAll1":false
            }
            """
    return frag_gen

@pytest.fixture(scope="session")
def generateFile(ruleId="TWELVE",ruleIdLength="SIX",frMode="NOACK",frDir="DOWN"):
    file_rules = tempfile.NamedTemporaryFile()
    stringa = ("""
{
    "DeviceID" : "lorawan:0000000000000001",
    "SoR" : [
    {
        "RuleID": 11,
	    "RuleIDLength": 6,
	    "NoCompression": []
    },
    {
        "RuleID": """ + RuleId.get(ruleId, "TWELVE") +""",
        "RuleIDLength": """ + RuleIdLength.get(ruleIdLength, "SIX") +""",
        "Fragmentation":{
"""+generateFragmentationSection(frMode, frDir)+"""
        }
    }
    ]
}
    """)
    #logging.info(stringa)
    #return stringa
    file_rules.write(stringa.encode("utf-8"))
    file_rules.seek(0)
    #for line in file_rules:
    #    print(line)

    #file_rules.seek(0)
    #Use yield instead of return so the temp file survives
    yield file_rules.name
