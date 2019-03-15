#!/usr/bin/python

## @package rpilora
#  This script allow the control of the rpilorawan expansion board for Raspberry Pi.
#
#

import time
import serial
import sys
from time import sleep
import argparse

class RPIlora(object):
	portOpen = False
	verbosity = 1

	def __init__(self, port, verbosity):
		# allow serial port choice from parameter - default is /dev/ttyAMA0
		portName = port
		self.verbosity = verbosity

		if self.verbosity >= 2 : print('Serial port : ' + portName)
		self.ser = serial.Serial(
			port=portName,
			baudrate=57600,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS
		)

	def getc(self, size, timeout=1):
		return ser.read(size).decode()

	def putc(self, data, timeout=1):
		serialcmd = data
		self.ser.write(serialcmd.encode())
		sleep(0.001) # give device time to prepare new buffer and start sending it

	def WaitFor(self, success, failure, timeOut):
		return self.ReceiveUntil(success, failure, timeOut) != ''

	def ReceiveUntil(self, success, failure, timeOut):
			if self.verbosity >= 2: ("       #method ReceiveUntil")
			iterCount = timeOut / 0.15
			self.ser.timeout = 0.1
			currentMsg = ''
			while iterCount >= 0 and success not in currentMsg and failure not in currentMsg :
				sleep(0.1)
				while self.ser.inWaiting() > 0 : # bunch of data ready for reading
						c = self.ser.read()
						currentMsg += c.decode()
				iterCount -= 1
			if success in currentMsg :
				return currentMsg
			elif failure in currentMsg :
				if self.verbosity >= 2: print('       Failure (' + currentMsg.replace('\r\n', '') + ')')
			else :
				if self.verbosity >= 2: print('       Receive timeout (' + currentMsg.replace('\r\n', '') + ')')
			return ''

	def open(self):
		#print("self.portOpen = ", self.portOpen)
		if self.portOpen == False :
			if self.ser.isOpen() : # on some platforms the serial port needs to be closed first
				#print('Serial port already open, closing it')
				self.ser.close()
			self.close()
			try:
				self.ser.open()
			except serial.SerialException as e:
				sys.stderr.write("Could not open serial port {}: {}\n".format(ser.name, e))
				print('SerialException Could not open serial port')
				sys.exit(1)

			serialcmd = 'sys get ver\r\n'
			self.ser.write(serialcmd.encode())
			if self.WaitFor('\r\n', 'ERROR', 3) :
				if self.verbosity >= 2: print('Modem OK')
				self.portOpen = True
				return True
			else:
				if self.verbosity >= 2: print('Modem Error')
				self.ser.close()
				return False
		else:
			return True

	def sendCommand(self, message):
		serialcmd = message + "\r\n"
		self.ser.write(serialcmd.encode())
		#rxData = self.ReceiveUntil('\r\n', 'ERROR', 5).replace('\r\n', '')
		rxData = self.ReceiveUntil('\r\n', 'ERROR', 10).replace('\r\n', '')
		return rxData

	def close(self):
		if self.ser.isOpen():
			self.ser.close()
