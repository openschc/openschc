from network import LoRa
import time
import pycom
import binascii

def loRaJoin():
    lora = LoRa(mode=LoRa.LORAWAN)
    # create an OTAA authentication parameters
    app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
    app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))
    pycom.heartbeat(False)
    pycom.rgbled(0x111111)
    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)
    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')
    pycom.rgbled(0x000000)
