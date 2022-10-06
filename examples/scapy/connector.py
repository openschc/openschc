# import socket programming library
import socket
import time
import base64
import binascii
from turtle import down
import cbor2 as cbor
import json

# import thread module
from _thread import *
import threading

from flask import Flask
from flask import request
from flask import Response

import requests

TTN_Downlink_Key = "NNSXS.PQBBC2TARHN6XXNESIYCG4JM2DO4PSHF45FWLYY.MFXGU63UKOPV5FYFXHX4KWA7XLF347Z75W6Q6DHWHCNVDEOGMMLA"


sock_r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_r.bind(("0.0.0.0",12345))

sock_w = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
openschc_port = 33033

SF_MTU = [None, #0
          None, #1
          None, #2
          None, #3
          None, #4
          None, #5
          None, #6
          250,  #7
          250,  #8
          123,  #9
          59,   #10
          59,   #11
          59    #12
          ]

"""
Structure of the exchange, a CBOR structure 

{ # generic values
    1: technology : 1 lorawan, ...
    2: ID (e.g. devEUI in LoRaWAN)
    3: possible MTU # in LoRaWAN regarding the DR the possible frame size
    4: payload 
# informational values regarding the technology
   -1: LoRaWAN SF
   -2: fPort
}

"""


def recv_data(sock):
    print ("starting listening")
    while True:
        data, addr = sock_r.recvfrom(2000)
        print (">>>", binascii.hexlify(data))
        msg = cbor.loads(data)

        if msg[1] != 1:
            print ("not LoraWAN Technology")
            continue

        dev_eui = binascii.hexlify(msg[2]).decode().upper()
        if not dev_eui in app_id:
            print ("device unknown", dev_eui)
            continue


        if app_id[dev_eui][0] == 'ttn':
            payload = msg[4]

            print (">>", binascii.hexlify(payload))

            fport = payload[0] # first byte is the rule ID
            content = payload[1:]

            print (">>>>", binascii.hexlify(content))

            downlink_msg = {
                "downlinks": [{
                    "f_port":   fport,
                    "frm_payload": base64.b64encode(content).decode()
                }]}
            downlink_url = \
            "https://eu1.cloud.thethings.network/api/v3/as/applications/" + \
            app_id[dev_eui][1] + "/devices/" +  app_id[dev_eui][2] + "/down/push"

            headers = {
                'Content-Type': 'application/json',
                'Authorization' : 'Bearer ' + TTN_Downlink_Key
            }

            print (downlink_url)
            print (downlink_msg)
            print ( headers)

            x = requests.post(downlink_url, 
                                data = json.dumps(downlink_msg), 
                                headers=headers)
            print ("downlink sent", x)
        elif app_id[dev_eui][0] == 'chirpstack':
            print("chirpstack")
        else:
            print ("unknown LNS")

app_id = {} # contains the mapping between TTN application_id and dev_eui

x = threading.Thread(target=recv_data, args=(1,))
x.start()

app = Flask(__name__)


@app.route('/ttn', methods=['POST']) # API V3 current
def get_from_ttn():
    fromGW = request.get_json(force=True)
    print (fromGW)

    downlink = None
    if "uplink_message" in fromGW:

        payload = base64.b64decode(fromGW["uplink_message"]["frm_payload"])
        #downlink = forward_data(payload)

        message = {
            1 : 1, # Techo LoRaWAN
            2 : binascii.unhexlify(fromGW["end_device_ids"]["dev_eui"]),
            3 : SF_MTU[fromGW["uplink_message"]["settings"]["data_rate"]["lora"]["spreading_factor"]],
            4 : fromGW["uplink_message"]["f_port"].to_bytes(1, byteorder="big") + payload,

            -1: fromGW["uplink_message"]["settings"]["data_rate"]["lora"]["spreading_factor"],
            -2: fromGW["uplink_message"]["f_port"]   
        }
        print (message)
        print (binascii.hexlify(cbor.dumps(message)))
        sock_w.sendto(cbor.dumps(message), ("127.0.0.1", openschc_port))

        app_id [fromGW["end_device_ids"]["dev_eui"].upper()] = ["ttn",
                fromGW["end_device_ids"]["application_ids"]["application_id"],
                fromGW["end_device_ids"]["device_id"]
                ]

        print (app_id)


    resp = Response(status=200)
    return resp

@app.route('/chirpstack', methods=['POST']) 
def get_from_chirpstack():
    fromGW = request.get_json(force=True)
    print (fromGW)


    if "data" in fromGW:
        payload = base64.b64decode(fromGW["data"])
        print(binascii.hexlify(payload))

        dev_eui = binascii.hexlify(base64.b64decode(fromGW["devEUI"]))
        fport = fromGW["fPort"]

        print (dev_eui, fport)
        app_id[dev_eui.decode().upper()] = ['chirpstack']

        print (app_id)

        message = {
            1 : 1,
            2 : dev_eui,
            3 : SF_MTU[fromGW["txInfo"]["loRaModulationInfo"]["spreadingFactor"]],
            4 : fport.to_bytes(1, byteorder="big") + payload,

            -1: fromGW["txInfo"]["loRaModulationInfo"]["spreadingFactor"],
            -2 : fport
        }
        print (message)
        print (binascii.hexlify(cbor.dumps(message)))

        sock_w.sendto(cbor.dumps(message), ("127.0.0.1", openschc_port))

    resp = Response(status=200)
    return resp

app.run(host="0.0.0.0", port=7002)



#y.start()