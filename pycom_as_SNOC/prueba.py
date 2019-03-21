from SendAndReceive import sendReceive
import Join as join
import pycom
import time
from machine import UART
import ubinascii
import _thread


contadorError = 0
sr = sendReceive()
sr.loRaJoin()
sr.initializeParameters()
print('Join = OK')
uart = UART(1, 57600)                         # init with given baudrate
uart.init(57600, bits=8, parity=None, stop=1, timeout_chars = 15) # init with given parameters
#msg = "11111111111111111111"
msg = "1111111111111111111122222222222222222222333333333333333333334444444444444444444455555555555555555555"
while True:
    response = sr.sendReceive(ubinascii.unhexlify(msg))
    print('msg sent')
    time.sleep(15)
    print('ready to send')
