"""Client Thread
This file manage of communication between a server and several clients using thread instances.
"""
import threading
from time import sleep
import SchcConfig
import stats.statsct


class ClientThread(threading.Thread):

    def __init__(self, ipClient, portClient, clientSocket, configuration):
        """
        Initialize Client Thread and server configuration calling Schcconfig.py
        :param ipClient: Contain client IP address
        :param portClient: Contain client port
        :param clientSocket: Client socket Instance create by the server in ServerConnection.py
        :param configuration: Contain all configuration done in ClientServerSimul.py file
        """
        threading.Thread.__init__(self)
        self.configuration = configuration
        self.protocol = None
        self.ipClient = ipClient
        self.portClient = portClient
        self.clientSocketInServer = clientSocket
        self.clientConfigInServer = SchcConfig.SchcConfig(self.configuration, self.clientSocketInServer)
        self.iteration = 0
        self.client_config()
        print("[+] Nouveau thread pour %s %s" % (ipClient, portClient,))

    def run(self):
        """
        This method execute a client thread to receive and send schc packets to a specific thread instance.
        """
        while True:
            print("Ready to receive a message")

            try:
                fragment1 = self.clientSocketInServer.recv(2048)
                print("--------------------Yo recibi esto: ", fragment1)
                sleep(0.1)
            except:
                print("Not ready to read")
                return

            try:
                d = fragment1.decode()
                print("--------------------Yo decodifiqué esto: ", d)
                if d == "":
                    return
                else:
                    self.recv_message(fragment1)
            except:
                self.recv_message(fragment1)

            self.protocol = self.clientConfigInServer.node0.protocol

            try:
                state = self.protocol.reassemble_session.session_list[0]['session'].state
                print("STATE : ", state)
            except:
                print("Not fragment state ")
                print("--------------------------- End Iteration ", self.iteration, " --------------------------")
                self.client_config()
                state = ''

            if state == 'DONE':
                self.send_message_from_socket(-1)
                print("--------------------------- End Iteration ", self.iteration, " --------------------------")
                self.client_config()
            elif state == 'ERROR_MIC':
                self.send_message_from_socket(0)
                self.protocol.reassemble_session.session_list[0]['session'].state = 'INIT'
            elif state == 'ACK_REQ':
                self.send_message_from_socket(-1)
                self.protocol.reassemble_session.session_list[0]['session'].state = 'INIT'
            elif state == 'ABORT':
                self.send_message_from_socket(0)
                print("--------------------------- End Iteration ", self.iteration, " --------------------------")
                self.client_config()
            elif state == 'DONE_NO_ACK' or state == 'ERROR_MIC_NO_ACK':
                print("--------------------------- End Iteration ", self.iteration, " --------------------------")
                self.client_config()

        self.clientSocketInServer.close()

    def client_config(self):
        """
        This method allow to initialize statistics module and configure schc simulation in server for a specific thread
        instance.
        """
        self.iteration += 1
        print("")
        print("")
        print("--------------------------- Iteration ", self.iteration, " --------------------------")
        print("---------- Client: Ip = ", self.ipClient, " Port = ", self.portClient, "---------------")
        stats.statsct.Statsct.initialize()
        self.clientConfigInServer.configSim()

    def recv_message(self, fragment):
        """
        This method allow to treat a fragment using schc compression and fragmentation modules
        :param fragment: Contain a fragment received from a client
        """
        print("------------------------------- RECEIVE PACKET ------------------------------")
        print("Fragment received from client: ", fragment)
        self.clientConfigInServer.node0.protocol.layer2.event_receive_packet(self.clientConfigInServer.node0.id,
                                                                             fragment)

    def send_message_from_socket(self, position_queue):
        """
        This method allow to send a message from server to client using socket connection
        :param position_queue: Contain a position in a dictionary of a schc packet to send to a client
        """
        queue_list = self.protocol.scheduler.queue
        print("queue_list", queue_list)
        message = bytearray(self.protocol.scheduler.queue[position_queue][3][0])
        print("Message server to client", message)
        Bytes = self.clientSocketInServer.send(message)
        print("Sent Bytes:", Bytes)
        sleep(1)
