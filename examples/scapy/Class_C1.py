from network import LoRa
from network import WLAN
import socket
import time
import pycom
import binascii
import select

print('Connecting to WiFi...',  end='')
# Connect to a Wifi Network
wlan = WLAN(mode=WLAN.STA)
#wlan.connect(ssid='RSM-B25', auth=(WLAN.WPA2, "df72f6ce24"))
wlan.connect(ssid='Martinez', auth=(WLAN.WPA2, "marino92"))
#wlan.connect(ssid='chirppygate', auth=(WLAN.WPA2, "marino92"))

while not wlan.isconnected():
    print('.', end='')
    time.sleep(1)
print(" OK")

print ('IP: ',  wlan.ifconfig()[0])

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868, public=True, device_class=LoRa.CLASS_C)
#
mac = lora.mac()
print ('devEUI: ',  binascii.hexlify(mac))

# create an OTAA authentication parameters
app_eui = binascii.unhexlify('00 00 00 00 00 00 00 02'.replace(' ','') )
app_key = binascii.unhexlify('6c c9 e2 a5 ea be 98 71 8c 54 ae 4c 2e 30 38 fb'.replace(' ','') )
dev_eui = binascii.unhexlify('16 64 a2 1b a5 32 71 1d'.replace(' ',''))

pycom.heartbeat(False)
pycom.rgbled(0x101010) # white

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key),  timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')
print('Joined...')

pycom.rgbled(0x000000) # black

def lora_events(lora):
    events = lora.events()
    print (events)

lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT | LoRa.TX_FAILED_EVENT), handler=lora_events)

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)
#s.bind(10)

w = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
w.bind(('0.0.0.0', 10000))

ip = socket.getaddrinfo("user.ackl.io",80)
print('ip', ip)
s.send(b"toto")

while True:
    pycom.rgbled(0x100000) # red
    s.setblocking(False)
    #s.settimeout(10)

    r = select.select ([s, w], [], [] )
    #s.send(b"toto")
    #time.sleep(1)
    print ('here? ', r)
    if r[0]:
        print (r[0], r[0][0]==s)
        if r[0][0] == s:
            print ("Coming from LoRaWAN")
            data, fport = s.recvfrom(64)
            print (data)
            #w.send(data)
            w.sendto(data, (ip, 8888)) # 54.37.158.10 user.ackl.io

#while True:
#    pycom.rgbled(0x100000) # red
#    s.setblocking(False)
    #s.settimeout(10)

#    try:
#        s.send(b"toto")
#        time.sleep(1)
#        data, port = s.recvfrom(64)
#        if data:
#            print('rx: ', data, 'port: ', port)
#        pycom.rgbled(0x001000) # green
#    except:
#        print (end=".")
#        pycom.rgbled(0x000000) # black

#    print (end=".")
#    time.sleep(0.1)
