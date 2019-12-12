""" Server connection and configuration
This file create a connection with a client
"""
from gen_base_import import *
import socket
import ClientThread


class ServerConnection:

    def __init__(self, configuration):
        """
        Initialize Server Connection Class
        :param configuration: Contain all configuration done in ClientServerSimul.py file
        """
        self.configuration = configuration
        self.socketServerConnection = None
        self.clientSocket = None
        self.newThread = None
        self.serverSend = None

    def connection(self):
        """
        This method open a socket with an IP address and port for communicating to several clients
            ip: self.configuration['ipServer']
            port: self.configuration['portServer']
        """
        self.socketServerConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IP4
        self.socketServerConnection.bind((self.configuration['ipServer'], self.configuration['portServer']))
        print("socket binded to ", self.configuration['ipServer'], " ip and port ", self.configuration['portServer'])

    def server(self):
        """
        This method listen to socket to establish a connection with a client and start a thread for this client. An IP
        address and port are assigned to the client when the connection is established
        :return:
        """
        # a forever loop until client wants to exit# put the socket into listening mode
        while True:
            self.socketServerConnection.listen(10)
            print("socket is listening")

            # establish connection with client
            (self.clientSocket, (ipClient, portClient)) = self.socketServerConnection.accept()
            print("Connexion de %s %s" % (ipClient, portClient,))

            # Start a new thread and return its identifier
            self.newThread = ClientThread.ClientThread(ipClient, portClient, self.clientSocket, self.configuration)
            self.newThread.start()
