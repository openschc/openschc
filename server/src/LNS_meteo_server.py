import sys, getopt
from flask import Flask
from flask import request
from flask import Response
import base64
import pprint
import json
import cbor2 as cbor
import time
from SCHC_server import SCHC_server
app = Flask(__name__)

app.debug = True
schc = SCHC_server()

@app.route('/lns', methods=['POST'])
def get_from_LNS():

    fromGW = request.get_json(force=True)
    #print("")
    #print("")
    #print ("HTTP POST RECEIVED")
    #pprint.pprint(fromGW)
    if "data" in fromGW:
        payload = base64.b64decode(fromGW["data"])
        #print("fromGW data: ")
        #print(fromGW["data"])
        #print("Size FromGW", len(fromGW["data"]))
        #print ("PayloadReceived: ")
        #print("Size payload ",len(payload))
        print("Payload ",payload.hex())
        schc.reassemble(payload)
        #msg = cbor.loads(payload)
        #print("Message decode: ",msg)
        replyStr = "Pleased to meet you"
        answer = {
          "fPort" : fromGW["fPort"],
          "devEUI": fromGW["devEUI"],
          "data"  : base64.b64encode(bytes(replyStr, 'utf-8')).decode('utf-8')
        }

        #print()
        #print ("HTTP POST REPLY")
        #pprint.pprint(answer)
        resp = Response(response=json.dumps(answer), status=200, mimetype="application/json")
        #print (resp)
        return resp



if __name__ == '__main__':
    print (sys.argv)
    defPort=8231
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


    app.run(host="0.0.0.0", port=defPort)



