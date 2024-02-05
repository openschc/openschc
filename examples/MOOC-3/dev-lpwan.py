import socket
import select
import cbor2 as cbor
import random
import time
import struct
import binascii

CORE_SCHC = ("10.0.0.21", 0x5C4C)
MID_LENGTH=3
KNOWN_URI = ["/temp", "/humi", "/pres"]

MID = 1

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", 8888))

def coap_send_measurement(value, uri):
    global MID

    if uri not in KNOWN_URI:
        print("unknown URI")
        return None
    
    if type(value) is not bytes: # not cbor
        value = cbor.dumps(value)

    uri_idx = KNOWN_URI.index(uri)
    print ("MID", MID, "URI", uri,  
            "(index:", uri_idx, ")", 
            "value", binascii.hexlify(value) )

    schc_residue = (0x00 & 0b0000_0111) << 5 | \
                   (MID & 0b0000_0111) << 2 | \
                   (uri_idx) & 0b0000_0011
    
    if MID == 0b0000_0111:
        MID = 1
    else:
        MID += 1
    
    schc_pkt = struct.pack("!B", schc_residue) + value
    print ("sending:", binascii.hexlify(schc_pkt))
    tunnel.sendto(schc_pkt, CORE_SCHC)

def wait_ack():
    readable, writable, exp = select.select ([tunnel], [], [], 1)
    print ("readable", readable)
    if len(readable) == 1:
        msg = tunnel.recv(1000)
        print ("Get downlink", binascii.hexlify(msg))
        return True
    else:
        print ("No answer")
        return False

class sensor():
    def __init__ (self, uri, period, init_value, evolution):
        self.uri = uri
        self.period = period
        self.current_value = init_value
        self.evolution=evolution

    def get_uri():
        return self.uri
    
    def get_period():
        return self.period

    def get_value(self):
        self.current_value += random.randint(-self.evolution, +self.evolution)
        return self.current_value


temperature = sensor("temp", 60, 20, 1)
humidity    = sensor("humi", 120, 50, 5)
pressure    = sensor("pres", 90, 1000, 10)

start_time = int(time.time())

event_queue = [(temperature, start_time+10), 
               (humidity, start_time+40), 
               (pressure, start_time+30)]


while True:
    next_event = event_queue.pop(0)
    wait_time = next_event[1] - int(time.time())
    if wait_time > 0:
        time.sleep(wait_time)

    sensor = next_event[0]
    coap_send_measurement(sensor.get_value(), sensor.get_uri())

    print("add")

    event_queue.append((sensor, int(time.time() + sensor.get_period())))
    sorted(event_queue, key=lambda x: x[1])
    print (event_queue)








while True:
    sensor_id = random.randint(0,2)
    if m == 0:
        temp += random.randint (-5, +5)
        coap_send_measurement(temp, "/temp")
    elif m == 1:
        humi += random.randint (-10, +10)
        coap_send_measurement(humi, "/humi")
    elif m == 2:
        pres += random.randint (-10, +10)
        coap_send_measurement(pres, "/pres")

    time.sleep(random.randint(1, 7))
    wait_ack()
