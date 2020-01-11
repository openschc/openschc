""" Client Send
This file allow the communication between client and server
"""
from time import sleep

class ClientSend:

    def __init__(self, socketClientConnection):
        """
        Initialize Client Send Class
        :param socketClientConnection: Contain a instance of client connection to a server. This instance allow to
        communicate a client with a server.
        """
        self.socketClientConnection = socketClientConnection

    def send(self, message):
        """
        This method allow to send a schc packet from client to server
        :param message: Contain a schc packet to send from client to server
        """
        print("Message to Server", message)
        Bytes = self.socketClientConnection.send(message)
        print("Sent Bytes:", Bytes)
        sleep(1)

    def Receive(self):
        """
        This method receive a schc packet from server
        :return currentMsg: schc packet sent from server
        """
        currentMsg = ''
        sleep(0.1)
        try:
            print("Ready to receive a message")
            currentMsg = self.socketClientConnection.recv(2048)
        except:
            print("Any message from server")
        return currentMsg