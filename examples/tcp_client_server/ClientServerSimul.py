"""Client-Server Simulation
This file allows to launch the simulation of a client or a server service.

How to run this simulation?
Server
 python3 ClientServerSimul.py --r server
Client
 python3 ClientServerSimul.py --r client
"""
import sys
import argparse
import ClientConnection
import ServerConnection
import os

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

class ClientServerSimul:

    def __init__(self, opt):
        """
        Initialize Client-Server simulation class
        :param role: Contain the role defined during execution process on terminal: client or server
        """
        self.configuration = {}
        self.config(opt)
        self.client = None
        self.server = None

    def config(self, opt):
        """
        This method allow to set the general configuration of the simulation.
        :param role: Define a role: client or server
        """
        self.configuration['role'] = opt.role
        self.configuration['ipServer'] = "127.0.0.1"
        self.configuration['portServer'] = 12345
        self.configuration['l2_mtu'] = 72  # In bits
        # self.configuration['size_message'] = 255# In bytes
        # self.configuration['ack_on_error'] = True
        self.configuration['time_between_iteration'] = opt.time_between_iteration
        self.configuration['packet_loss_simulation'] = opt.packet_loss_simulation
        # self.configuration['payload_file_simulation'] = False
        self.configuration['payload_name_file'] = opt.payload_name_file
        self.configuration['rule_name_file'] = opt.rule_name_file
        self.configuration['mode_with_compression'] = opt.mode_with_compression
        # print(self.configuration)

    def start(self):
        """
        This method is called to start a client or server service. This method allow to initialize and configure a
        client or server service and create a socket connection between several client to a server.
        """
        if self.configuration['role'] == "client":
            print("")
            self.client = ClientConnection.ClientConnection(self.configuration)
            self.client.connection()
            self.client.client()
        elif self.configuration['role'] == "server":
            print("")
            self.server = ServerConnection.ServerConnection(self.configuration)
            self.server.connection()
            self.server.server()


# -----------------------------------------------------------------------------------
# for param in sys.argv:
#     print(param)

ap = argparse.ArgumentParser(description="a SCHC simulator.",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("--role", action="store", dest="role",
                default="client",
                help="specify a role: client or server.")
ap.add_argument("--payload", action="store", dest="payload_name_file",
                default="",
                help="Specify a payload file name. e.g. payload/testfile_small.txt.")
ap.add_argument("--rule", action="store", dest="rule_name_file",
                default="{}/examples/comp-rule-100.json".format(os.environ.get("OPENSCHCDIR",".."),
                help="Specify a rule file name. e.g.  examples/comp-rule-100.json."))
ap.add_argument("--time", action="store", dest="time_between_iteration", type=int,
                default=10,
                help="Specify a time in seconds between each sending message .")
ap.add_argument("--loss", type=str2bool, nargs='?', dest="packet_loss_simulation",
                const=True, default=False,
                help="Simulation using packet loss: True or False.")
ap.add_argument("--compression", type=str2bool, nargs='?', dest="mode_with_compression",
                const=False, default=True,
                help="Simulation using compression: True or False.")
opt = ap.parse_args()

schcConfig = ClientServerSimul(opt)
schcConfig.start()
# ------------------------------------------------------
