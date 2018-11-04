import socket
import threading

class udp_wrapper:
    iid = 0

    def __init__(self, scheduler, delay=1, bind_addr=None):
        self.scheduler = scheduler
        self.delay = delay
        self.link_list = []
        self.so = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        if bind_addr:
            self.so.bind(bind_addr)
        self.so.connect(("8.8.8.8", 0))
        self.iid = self.so.socket.getsockname()
        self.receive_function = None
        self.recv_th = threading.Thread(self.recv_thread, (self.so))

    def recv_thread(self, so):
        while True:
            so.recvfrom(packet, peer)
            if self.receive_function != None:
                self.receive_function(peer, packet)
            else:
                print("%s SimulLayer2: %s->%s %s " %
                    (self.scheduler.get_time(),
                    self.mac_id, other_mac_id, packet))

    def add_link(self, other):
        self.peer_addr = other

    def set_receive_callback(self, receive_function):
        self.receive_function = receive_function

    def send_packet(self, packet):
        self.so.sendto(packet, self.peer_addr)

