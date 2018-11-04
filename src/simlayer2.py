
class SimulLayer2:
    mac_id = 0

    def __init__(self, scheduler, delay=1):
        self.scheduler = scheduler
        self.delay = delay
        self.link_list = []
        self.mac_id = SimulLayer2.__get_unique_mac_id()
        self.receive_function = None
        self.event_timeout = None

    def add_link(self, other):
        assert other not in self.link_list
        self.link_list.append(other)

    def set_receive_callback(self, receive_function):
        self.receive_function = receive_function

    def send_packet(self, packet):
        # should be moved in a generic Simul class:
        for other in self.link_list:
            self.scheduler.add_event(self.delay, other.event_receive_packet,
                                     (other.mac_id, packet))

    def event_receive_packet(self, other_mac_id, packet):
        if self.receive_function != None:
            self.receive_function(other_mac_id, packet)
        else:
            print("%s SimulLayer2: %s->%s %s " %
                  (self.scheduler.get_time(),
                   self.mac_id, other_mac_id, packet))

    def __get_unique_mac_id():
        result = SimulLayer2.mac_id
        SimulLayer2.mac_id += 1
        return result
