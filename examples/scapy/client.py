import socket
import time
import pycom
import binascii
import struct
import kpn_senml.cbor_encoder as cbor
import BME280 # acces to BME280 temperature

# get access to the temprature sensor through I2C bus
from machine import I2C

i2c = I2C(0, I2C.MASTER, baudrate=400000)
print (i2c.scan())
bme = BME280.BME280(i2c=i2c)

# network part
from network import LoRa

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868) #, device_class=LoRa.CLASS_C)
#
mac = lora.mac()
print ('devEUI: ',  binascii.hexlify(mac))

# create an OTAA authentication parameters
app_eui = binascii.unhexlify(
     '70B3D57ED0033AE3'.replace(' ',''))
#     '0000000000000000'.replace(' ',''))

app_key = binascii.unhexlify(
     'B0923EE49E056F29C1482EE5846FADF4'.replace(' ',''))  # TTN
     #'11223344556677881122334455667788'.replace(' ',''))   # Acklio
     #'11 00 22 00 33 00 44 00 55 00 66 00 77 00 88 00'.replace(' ',''))   # chirpstack

pycom.heartbeat(False) # stop blue blinking
pycom.rgbled(0x101010) # set led to white

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

pycom.rgbled(0x000000) # stop the led, set to black

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

mid = 0 # MID is different in each CoAP Message

def send_coap(uri_path, message):
    global mid

    pycom.rgbled(0x100000) # set Pycom led to red
    s.setblocking(True)    # blocking send and recvfrom
    s.settimeout(10)       # blocking duration

    s.bind(38) # set the ruleID on the fPort
    mid += 1   # increase MID field, no limit since only 6 LSB are taken

    # residue for up rule 38 is 6 bits for MID and 2 bits for URI-path
    uri_idx = ['temperature', 'pressure', 'humidity', 'memory'].index(uri_path)
    schc_r = (mid << 2) & 0xFF | uri_idx
    print ("MID: ", mid, "URL:", uri_path, " => Residue:", bin(schc_r))

    # compose message and send by adding data
    schc_msg = struct.pack("!B", schc_r) + message
    s.send(schc_msg)

    pycom.rgbled(0x000010) # set the led to blue

    data = None
    try: # blocking recv to recied Downling msg
        data, fport = s.recvfrom(64)
        pycom.rgbled(0x001000) # green
    except: # timeout no dat received
        pycom.rgbled(0x000000) # black

    if data: # received data
        if fport == 38: # chek RuleID
            # downlink residues are 1 byte for Code
            code, = struct.unpack("!B", data)
            print ("RuleID", fport, "Residue", binascii.hexlify(data),\
                   "Code "+str(hex(code>>5)).replace("0x","") + \
                     '.0'+ str(hex(code & 0b00011111)).replace("0x", ""))
            return code
        else:
            print ("Unknown rule")
            return None
    else:
        return None # no data recieved

    s.setblocking(False)
    time.sleep (29)

preiod = 10 # send temperature every 10 s
while True:
    t = int(bme.read_temperature()*100)
    print ("Temperature: ", t)
    code = send_coap ("temperature", cbor.dumps(t))

    if code != None: # error notification
        period = 30  # increase sending period
    else:
        period = 10 # no error, regular period

    print ("Period:", period)
    time.sleep(period)
    print ('-'*10)
