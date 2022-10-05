# import socket programming library
import socket
import time
import base64

# import thread module
from _thread import *
import threading

from flask import Flask
from flask import request
from flask import Response

print_lock = threading.Lock()

sock_r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_r.bind(("0.0.0.0",12345))

sock_w = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def recv_data(sock):
    while True:
        data = sock_r.recvfrom(2000)
        print (">>>", data)


        # if downlink != None:
        #     from ttn_config import TTN_Downlink_Key

        #     downlink_msg = {
        #         "downlinks": [{
        #             "f_port":   fromGW["uplink_message"]["f_port"],
        #             "frm_payload": base64.b64encode(downlink).decode()
        #         }]}
        #     downlink_url = \
        #     "https://eu1.cloud.thethings.network/api/v3/as/applications/" + \
        #     fromGW["end_device_ids"]["application_ids"]["application_id"] + \
        #                     "/devices/" + \
        #                     fromGW["end_device_ids"]["device_id"] + \
        #                     "/down/push"

        #     headers = {
        #         'Content-Type': 'application/json',
        #         'Authorization' : 'Bearer ' + TTN_Downlink_Key
        #     }

        #     x = requests.post(downlink_url, 
        #                         data = json.dumps(downlink_msg), 
        #                         headers=headers)



def send_data(sock):
    while True:
        sock_w.sendto (b"toto", ("127.0.0.1", 33033))
        time.sleep(10)


x = threading.Thread(target=recv_data, args=(1,))
#y = threading.Thread(target=send_data, args=(1,))

app = Flask(__name__)


@app.route('/ttn', methods=['POST', 'GET']) # API V3 current
@app.route('/ttn', methods=['POST']) # API V3 current
def get_from_ttn():
    fromGW = request.get_json(force=True)
    print (fromGW)

    downlink = None
    if "uplink_message" in fromGW:

        payload = base64.b64decode(fromGW["uplink_message"]["frm_payload"])
        #downlink = forward_data(payload)



    resp = Response(status=200)
    return resp


x.start()


app.run(host="0.0.0.0", port=7002)



#y.start()