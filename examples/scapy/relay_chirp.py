#!/usr/bin/env python3

import sys
import argparse
from flask import Flask
from flask import request
from flask import Response
import pprint
import json
import binascii

import socket
import select
import time
import base64

import requests

app = Flask(__name__)
app.debug = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('socket:', sock)

@app.route('/TTN', methods=['POST'])
def get_from_chirpstack():
    import secret as secret

    #print (secret.server)
    #fromGW = request.get_json(force=True)
    #print (request.environ.get('REMOTE_PORT'))
    #pprint.pprint (fromGW)

    #downlink = None
    downlink = b"downkink test test downkink test"
    #if "data" in fromGW:
        #payload = base64.b64decode(fromGW["data"])
        #downlink = forward_data(payload)
        #print (fromGW["fPort"])

    if downlink != None:
        answer = {
            "deviceQueueItem": {
		            "data": base64.b64encode(downlink).decode('utf-8'),
                    "fPort": 3,
            }
        }
        pprint.pprint (answer)
        dev_eui = '1664a21ba532711d'
        #device = binascii.hexlify(base64.b64decode(fromGW["devEUI"])).decode()
        downlink_url = secret.server+'/api/devices/'+dev_eui+'/queue'
        print (downlink_url)
        headers = {
            "content-type": "application/json",
            "grpc-metadata-authorization" : "Bearer "+ secret.key
        }
        print (headers)
        x = requests.post(downlink_url, data = json.dumps(answer), headers=headers)
        print(x)


    resp = Response(status=200)
    return resp

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="show uplink and downlink messages")
    parser.add_argument('--http_port',  default=9999,
                        help="set http port for POST requests")
    parser.add_argument('--forward_port',  default=33033,
                        help="port to forward packets")
    parser.add_argument('--forward_address',  default='127.0.0.1',
                        help="IP address to forward packets")

    args = parser.parse_args()
    verbose = args.verbose
    defPort = args.http_port
    forward_port = args.forward_port
    forward_address = args.forward_address

    app.run(host="0.0.0.0", port=defPort)

while True:
    get_from_chirpstack()
    time.sleep(30)
