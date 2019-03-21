from SendAndReceive import sendReceive
import Join as join
import pycom
import time
from machine import UART
import ubinascii
import _thread

# Define a function for the thread
def th_func(delay,id):
    sr = sendReceive()
    sr.loRaJoin()
    sr.initializeParameters()
    print('Join = OK')
    while True:
        while len(packetsToSend) > 0:
            print('packetsToSend Buffer len: ',len(packetsToSend))
            tuple = packetsToSend[0]
            msg = tuple[0]
            receive = tuple[1]
            print("msg= ", msg, "  Need to receive = ", receive)
            packetsToSend.pop(0)
            uart.write('ok\r\n')
            response = sr.sendReceive(ubinascii.unhexlify(msg))
            print('Sent packet: ', ubinascii.unhexlify(msg))
            if receive:
                if(response is None):
                    print('Response:  ',response)
                    uart.write('mac_tx_ok\r\n')
                else:
                    reponse = ubinascii.hexlify(response).decode('utf-8')
                    reponse = "mac_rx " + reponse +"\r\n"
                    print('Response received:  ',reponse)
                    uart.write(reponse)
                    time.sleep(0.5)
                    uart.write('mac_tx_ok\r\n')


#Create the sending thread
packetsToSend = []
_thread.start_new_thread(th_func, (1,2))

contadorError = 0
uart = UART(1, 57600)                         # init with given baudrate
uart.init(57600, bits=8, parity=None, stop=1, timeout_chars = 15) # init with given parameters
while True:
    if uart.any() > 0:
        #print('Algo llego, talla: ',uart.any())
        print('contadorError: ', contadorError)
        line= uart.readline()
        print('Received: ', line)
        if line != b'sys get ver\r\n' :
            line = line.decode('utf-8')
            if "uncnf" in line:
                line = line.replace('mac tx uncnf 1 ', '')
                receive = False
                uart.write('mac_tx_ok\r\n')
                print("uncnf")
            if "cnf" in line:
                line = line.replace('mac tx cnf 1 ', '')
                receive = True
                print("cnf")
            #remove the commandsline = line.decode('utf-8').replace('mac tx uncnf 1 ', '')
            line = line.replace('\r\n', '')
            if False:
            #if contadorError == 10:
            #if contadorError == 10 or contadorError == 11:
                print('PACKET', contadorError, ' LOST')
                uart.write('ok\r\n')
                time.sleep(0.5)
                uart.write('mac_tx_ok\r\n')
            else:
                packetsToSend += [(line, receive)]
        #SR.sendReceive(line)
        if line == b'sys get ver\r\n' :
            uart.write('mac_tx_ok\r\n')
        contadorError += 1
    time.sleep(0.5)
