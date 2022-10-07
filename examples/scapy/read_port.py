import socket
import binascii

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
s.bind ("::", 12345)

while True:
    x = s.read(2000)
    print (binascii.hexlify(x))