from network import LoRa
import socket
import time
import binascii
import pycom


class sendReceive:

    def initializeParameters(self):
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        #s.bind(5)
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
        self.s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)
        self.s.setblocking(True)
        self.s.settimeout(1)
        print("paramseters ini")

    def sendReceive(self,message):

        #pycom.rgbled(0x110000)
        print('msg size: ', len(message))
        self.s.send(message)
        try:
            data = self.s.recv(64)
            print("response len: ", len(data))
            if(len(data)<2):
                data = None
            else:
                pycom.rgbled(0x000011)
            print('Response: ',data)
        except:
            print ('timeout in receive ')
            pycom.rgbled(0x000000)
            data =  None
        pycom.rgbled(0x001100)
        self.s.setblocking(False)
        return data
        #time.sleep(2)
        #pycom.rgbled(0x000000)


    def loRaJoin(self):
        self.lora = LoRa(mode=LoRa.LORAWAN)
        self.lora.sf(7)
        # create an OTAA authentication parameters
        app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
        app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))
        pycom.heartbeat(False)
        pycom.rgbled(0x111111)
        # join a network using OTAA (Over the Air Activation)
        self.lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)
        # wait until the module has joined the network
        while not self.lora.has_joined():
            time.sleep(2.5)
            print('Not yet joined...')
        pycom.rgbled(0x000000)
