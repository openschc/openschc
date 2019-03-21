import SendAndReceive as SR
import Join as join
import pycom
import time
from machine import UART
import ubinascii
import _thread

# Define a function for the thread
def th_func(delay,id):
    while True:
        while len(packetsToSend) > 0:
            print('packetsToSend Buffer len: ',len(packetsToSend))
            msg = packetsToSend[0]
            packetsToSend.pop(0)
            SR.sendReceive(ubinascii.unhexlify(msg))
            print('Sent packet: ', ubinascii.unhexlify(msg))
            #time.sleep(1)


join.loRaJoin()
print('Join = OK')
uart = UART(1, 57600)                         # init with given baudrate
uart.init(57600, bits=8, parity=None, stop=1, timeout_chars = 15) # init with given parameters

#Create the sending thread
packetsToSend = []
_thread.start_new_thread(th_func, (1,2))


while True:
    if uart.any() > 0:
        #print('Algo llego, talla: ',uart.any())
        line= uart.readline()
        if line != b'sys get ver\r\n' :
            #remove the commands
            line = line.decode('utf-8').replace('mac tx uncnf 1 ', '')
            line = line.replace('\r\n', '')
            packetsToSend += [line]
        #SR.sendReceive(line)
        uart.write('mac_tx_ok\r\n')
        #print('packetsToSend size : ', len(packetsToSend))
        #print('packetsToSend: ', packetsToSend)
    time.sleep(0.5)
