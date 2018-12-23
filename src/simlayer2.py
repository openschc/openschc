#---------------------------------------------------------------------------

class SimulLayer2:
    __mac_id_base = 0

    def __init__(self, sim):
        self.sim = sim
        self.protocol = None
        self.mac_id = SimulLayer2.__get_unique_mac_id()
        self.receive_function = None
        self.event_timeout = None
        self.counter = 1 # XXX: replace with is_transmitting?
        self.is_transmitting = False
        self.packet_queue = []

    def _set_protocol(self, protocol):
        self.protocol = protocol

    def set_receive_callback(self, receive_function):
        self.receive_function = receive_function

    def send_packet(self, packet, src_dev_id, dst_dev_id=None,
                    transmit_callback=None):
        self.packet_queue.append((packet, src_dev_id, dst_dev_id,
                                  transmit_callback))
        if not self.is_transmitting:
            self._send_packet_from_queue()

    def _send_packet_from_queue(self):
        assert not self.is_transmitting
        assert len(self.packet_queue) > 0

        self.is_transmitting = True
        (packet, src_dev_id, dst_dev_id, transmit_callback
        ) = self.packet_queue.pop(0)
        print(transmit_callback, "AAAAAAA")

        self.sim.send_packet(packet, src_dev_id, dst_dev_id,
                             self._event_sent_callback, (transmit_callback,))

    def _event_sent_callback(self, transmit_callback, status):
        assert self.is_transmitting
        self.is_transmitting = False
        if transmit_callback != None:
            transmit_callback(status)

    def event_receive_packet(self, other_mac_id, packet):
        assert self.protocol != None
        self.protocol.event_receive_from_L2(other_mac_id, packet)

    @classmethod
    def __get_unique_mac_id(cls):
        result = cls.__mac_id_base
        cls.__mac_id_base += 1
        return result

    def get_mtu_size(self):
        return 56   # XXX

#---------------------------------------------------------------------------
