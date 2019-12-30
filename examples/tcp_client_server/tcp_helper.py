"""
Helper: 
- provides a simplified interface for creating objects and running openschc
- provides defaults for most configuration options, but allows to be more
  explicit and override some settings
- allow

TCP Helper:
- Helper creates programs communicating (exchanging SCHC packets) through TCP 
  sockets, one is a (TCP) server, others are (TCP) clients

** Fundamentally, running openschc requires assembly of 4 objects:
- RuleManager
- UpperLayer that receives and sends upper layer packets (e.g. IP packets)
- LowerLayer that receives and sends lower layer packets (e.g. SCHC packets,
  sent through LoRaWAN, Sigfox, NB-IoT, or here through TCP sockets)
- Scheduler that manages time and events
- which are used in one main object SCHCProtocol

1) These objects can be created in sequence:
- The scheduler is created automatically by the helper
- The RuleManager should be created externally, as the object from 
- helper.create_upper_layer(...)
- helper.create_lower_layer(...)
- helper.create_schc_protocol(...)

2) And then the 
helper.run()

Or alternately the
scheduler = helper.get_scheduler()
scheduler.run()

** Defaults
The helper also would create the objects with defaults if the objects
have not been created.

"""

import protocol
import gen_rulemanager


DefaultTcpAddress = ""
DefaultTcpPort = 8642
DefaultFragmentation = True
DefautlCompression = True


class TcpUpperLayer:
    """The upper layer called to received IP packets after reassembly
    and uncompression

    It is also the place where that send packet to """

    def send_at(self, delay_sec, packet):
        """Makes the uppe layer send the packet 
        :param delay_sec: the time before sending next packet
        :param packet: the packet to send (bytes)
        """
        XXX

class TcpHelper:

    def __init__(self, config={}):
        self.config = config.copy()
        self.upper_layer = None
        self.lower_layer = None
        self.protocol = None
        self.scheduler = XXX

        
    def set_mode(self, mode):
        """set whether the node is a client or a server
        :param mode: "client" or "server"
        """
        if mode != "client" and mode != "server":
            raise ValueError("Mode should be 'client' or 'server'",  mode)
        self.config["mode"] = mode

    def set_tcp_address(self, address):
        self.config["tcp-address"] = address

    def set_tcp_port(self, port):
        self.config["tcp-port"] = port

    def set_fragmentation(self, enabled):
        self.config["fragmentation"] = enabled

    def set_compression(self, enabled):
        self.config["compression"] = enabled
            
    
    def get_scheduler(self):
        return self.scheduler

    
    def create_upper_layer(self):
        self.upper_layer = TcpUpperLayer(XXX)
        return self.upper_layer

    def set_upper_layer(self, upper_layer):
        self.upper_layer = upper_layer
    
    def get_upper_layer(self):
        if self.upper_layer is None:
            raise RuntimeError("create_upper_layer or create_schc_protocol "
                               "should be called first")
        return self.upper_layer

    
    def create_lower_layer(self):
        self.lower_layer = TcpLowerLayer(XXX)
        return self.lower_layer

    def set_lower_layer(self, lower_layer):
        self.lower_layer = lower_layer
    
    def get_lower_layer(self):
        if self.lower_layer is None:
            raise RuntimeError("create_lower_layer or create_schc_protocol "
                               "should be called first")
        return self.lower_layer


    def create_schc_protocol(self, rule_manager=None, lower_layer=None,
                             upper_layer=None):
        if rule_manager is None:
            if self.rule_manager is None:
                XXX
            else:
                rule_manager = self.rule_manager
        if lower_layer is None:
            if self.lower_layer is None:
                XXX
            else:
                lower_layer = self.lower_layer
        if upper_layer is None:
            if self.upper_layer is None:
                XXX
            else:
                upper_layer = self.upper_layer

        schc_protocol = protocol.SCHCProtocol()

        self.rule_manager = rule_manager
        self.upper_layer = upper_layer
        self.lower_layer = lower_layer
        self.schc_protocol = schc_protocol

        return self.schc_protocol

    def run(self):
        self.scheduler.run()
    
#---------------------------------------------------------------------------
