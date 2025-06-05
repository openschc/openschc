# Common Field descriptions removed from gen_rulemanager
from gen_parameters import *
from math import log, ceil

FIELD__DEFAULT_PROPERTY = {
    T_IPV6_VER             : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    T_IPV6_TC              : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_FL              : {"FL": 20, "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_NXT             : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_HOP_LMT         : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"   },
    T_IPV6_LEN             : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_IPV6_DEV_PREFIX      : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"   },
    T_IPV6_DEV_IID         : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"  },
    T_IPV6_APP_PREFIX      : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"   },
    T_IPV6_APP_IID         : {"FL": 64, "TYPE": bytes, "ALGO": "DIRECT"   },
    T_UDP_DEV_PORT         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_UDP_APP_PORT         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_UDP_LEN              : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_UDP_CKSUM            : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"   },
    T_ICMPV6_TYPE          : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_CODE          : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_CKSUM         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_IDENT         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_SEQNO         : {"FL": 16, "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_UNUSED        : {"FL": 32, "TYPE": int, "ALGO": "DIRECT"  },
    T_ICMPV6_PAYLOAD       : {"FL": "var", "TYPE": bytes, "ALGO": "DIRECT"  },
    T_COAP_VERSION         : {"FL": 2,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TYPE            : {"FL": 2,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TKL             : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_CODE            : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_MID             : {"FL": 16,  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_TOKEN           : {"FL": "tkl",  "TYPE": int, "ALGO": "DIRECT"  },
    T_COAP_OPT_URI_HOST    : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION" },
    T_COAP_OPT_URI_PATH    : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION" },
    T_COAP_OPT_CONT_FORMAT : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},
    T_COAP_OPT_ACCEPT      : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},
    T_COAP_OPT_URI_QUERY   : {"FL": "var", "TYPE": str, "ALGO": "COAP_OPTION" },
    T_COAP_OPT_NO_RESP     : {"FL": "var", "TYPE": int, "ALGO": "COAP_OPTION"},

    T_GEONW_VER: {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    # Generate similar entries for the other fields from line 36 to line 59 of gen_parameters.py
    T_GEONW_BH_NXT: {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_BH_RES: {"FL": 8,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_BH_LT: {"FL": 8,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_BH_RHL : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT" },

    T_GEONW_CH_NH : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_RES1: {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_HT : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_HST : {"FL": 4,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_TC : {"FL": 8,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_FLAGS : {"FL": 1,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_RES2: {"FL": 7,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_PL: {"FL": 16,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_MHL: {"FL": 8,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_CH_RES3: {"FL": 8,  "TYPE": int, "ALGO": "DIRECT" },

    T_GEONW_LP_GN_ADDR_M : {"FL": 1 , "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_GN_ADDR_TPT : {"FL": 5,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_GN_ADDR_RES : {"FL": 10,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_GN_ADDR_MID : {"FL": 48,  "TYPE": int, "ALGO": "DIRECT" },

    T_GEONW_LP_TS: {"FL": 32,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_LAT: {"FL": 32,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_LON: {"FL": 32,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_PAI : {"FL": 1,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_SPD : {"FL": 15,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_HDG : {"FL": 16,  "TYPE": int, "ALGO": "DIRECT" },
    T_GEONW_LP_RES: {"FL": 32,  "TYPE": int, "ALGO": "DIRECT" },

}

def estimateSCHCPacketLength(ruleJSON):
    """
    Estimate the length of a SCHC packet based on the field properties.
    This function assumes that all fields are present and uses their fixed lengths.
    """
    packetLength = 0
    compressionRules = ruleJSON.get("Compression", [])
    for field, properties in FIELD__DEFAULT_PROPERTY.items():
        # Filter out fields which are not relevant to Geonetworking
        if "GEONW" not in field:
            continue
        
        ruleCDA = None

        # Get the exact compression rule for the field
        for compressionRule in compressionRules:
            if compressionRule.get("FID") == field:
                # If the field is elided, we do not count its length
                ruleCDA = compressionRule["CDA"]
                break

        if ruleCDA is None:
            raise("Field {} not found in compression rules".format(field))
    
        if ruleCDA in ["not-sent", "compute-length"] :
            # If the field is elided, we do not count its length
            continue

        if ruleCDA == "mapping-sent":
            # Get the target value
            targetValue = compressionRule["TV"]
            # Calculate the length of bits required to represent the target value
            # Simplistic assumption, TV is used as an enum, so the min. bits required
            # to represent targetValue is the log2 of the value + 1
            tvLength = ceil(log(len(targetValue)) / log(2)) 
            packetLength += tvLength

        if ruleCDA == "value-sent":
            # If the field is sent as a value, we use the fixed length defined in properties
            packetLength += properties["FL"]
        # TODO sending MSB/LSB

    return packetLength