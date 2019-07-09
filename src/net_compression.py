import os
import sys
sys.path.insert(0, '../..')

import getopt

import base64
import pprint
import json
import binascii

import requests
import time
import json
import logging

import http.client

http.client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


destinationDevEUI = "70b3d54995bd3c5d"
url = "https://core.acklio.net:8080/v1/devices/"+destinationDevEUI+"/send"


# -----   SCHC ------


from rulemanager import *


# ----- scapy -----

from scapy.all import *
import scapy.contrib.coap

import ipaddress

def AnalyzePkt(packet):
    print(len(packet))

#    try:
    if True:
        fields, data = packetParser.parser(bytes(packet), direction="dw")
        print("Fields = ", fields, data)

        rule =RM.FindRuleFromHeader(fields, "dw")
        print("RuleID =", rule)

        if rule != None:
            result = struct.pack("!B", rule["ruleid"]) # ruleId is view as a Byte
            res = compressor.apply(fields, rule["content"], "dw")
            if data != None:
                res.add_bytes(data)
            result += res.buffer()

            print ("compressed header = ", binascii.hexlify(result))

            # answer = {
            #     "fPort" : 2,
            #     "devEUI" : destinationDevEUI,
            #     "data": base64.b64encode(result).decode('utf-8')
            # }

            
                                        
            # cookieContent = {"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MjU2Nzk1MTUsInVzZXJJbmZvIjp7ImFkbWluIjpmYWxzZSwidXNlcm5hbWUiOiJNT09DLVBMSURPIn19.p0o4eTyd-fvHXXpU8wXmolokFb_CBHpnKPWo8vZ_CTe8YCTaJYbdX_P043oOUaNzo8q9rP_LnD7DBSCLPJ7_NOJavj9sKLRU9vJDP0U7l5Bm1oK3fdlQX0hO9b2mMLQOOHQeC0h-KvAWg38oam9rKhX-Z42j35bOfMpPKKGgOK9NS5KdieDNds7lko6kl0tEgWjGNEi0ZwagigdNSO863aNC4qvGCjWEj4BLgQ2QcUB4Uy7LsFwCrUWST9nptx1gC2cVnm9G9iFvfyZ3QvHFw9XgPjA1_67suFKEw_2rdmlc0s4JH8oaufLvLtcVhKoBZCItN192hWHEO0xe0Kh4mQ"};

            # print (cookieContent)
            
            # print (requests.post(url, data=json.dumps(answer), cookies=cookieContent))


#    except ValueError:
#        print("next")
        
if __name__ == '__main__':

    print (sys.argv)

    defPort=7002
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp:",["port="])
    except getopt.GetoptError:
        print ("{0} -p <port> -h".format(sys.argv[0]))
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print ("{0} -p <port> -h".format(sys.argv[0]))
            sys.exit()
        elif opt in ("-p", "--port"):
            defPort = int(arg)

    RM = RuleManager()
    RM.addRule(SCHC_RULES.rule_coap0)
    RM.addRule(SCHC_RULES.rule_coap1)
    RM.addRule(SCHC_RULES.rule_coap2)

    compressor = Compressor (RM)
    packetParser = Parser()

sniff (filter="ip6 and udp port 5683", prn=AnalyzePkt, iface="he-ipv6")