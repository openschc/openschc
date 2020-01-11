"""Client connection and configuration
This file initialize and configure a client service and create a connection to a server
"""
import SchcConfig
import stats.statsct
import ClientSend
import socket
from time import sleep


class ClientConnection:

    def __init__(self, configuration):
        """
        Initialize Client Connection Class
        :param configuration: Contain all configuration done in ClientServerSimul.py file
        """
        self.configuration = configuration
        self.socketClientConnection = None
        self.clientConfig = None
        self.clientSend = None

    def connection(self):
        """
        This method create a connection between client and server with a ip and port
            ip: self.configuration['ipServer']
            port: self.configuration['portServer']
        and allow to start the client schc configuration
        """
        self.socketClientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to server on local computer
        print("Waiting for a server")
        while self.socketClientConnection.connect_ex(
                (self.configuration['ipServer'], self.configuration['portServer'])) != 0:
            sleep(0.1)
        print("Connected to server")
        self.clientSend = ClientSend.ClientSend(self.socketClientConnection)
        self.clientConfig = SchcConfig.SchcConfig(self.configuration, self.clientSend)

    def client_config(self, iteration):
        """
        This method allow to initialize statistics module and configure schc simulation.
        :param iteration: Counter to know how many times a sending process was executed from client.
        """
        print("")
        print("")
        print("--------------- Iteration: ", iteration, " -----------------------")
        stats.statsct.Statsct.initialize()
        self.clientConfig.configSim()

    def send_message(self):
        """
        This method allow to send a message through Schc using the compression and fragmentation process
        """
        payload = self.clientConfig.config_packet()
        self.clientConfig.node0.protocol.layer3.send_later(1, 1, payload)
        self.clientConfig.sim.run()

    def client(self):
        """
        This method execute several times the sending process of a message from client to server
        """
        iteration = 1
        while True:
            self.client_config(iteration)
            self.send_message()
            print("--------------- End iteration: ", iteration, " -----------------------")
            sleep(self.configuration['time_between_iteration'])
            iteration += 1
