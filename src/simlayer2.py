import Lora as LoRa
#---------------------------------------------------------------------------
class SimulLayer2:
    __mac_id_base = 0
    mac_id = 0
    deveui= '70B3D5499EFE2D91'
    appeui= '0000000000000000'
    appkey= '11223344556677881122334455667788'

    def __init__(self):
        self.protocol = None
        self.mac_id = SimulLayer2.__get_unique_mac_id()
        self.receive_function = None
        self.event_timeout = None
        self.counter = 1 # XXX: replace with is_transmitting?
        self.is_transmitting = False
        self.packet_queue = []
        self.port = "/dev/ttyAMA0"
        self.verbosity = 2
        self.lora = LoRa.Lora(self.port, self.verbosity)
        self.mtu = 56
        print('deveui ', self.deveui, '  appeui ', self.appeui, '  appkey ', self.appkey)

    def _set_protocol(self, protocol):
        self.protocol = protocol

    def set_receive_callback(self, receive_function):
        self.receive_function = receive_function

    def send_packet(self, packet, src_dev_id, dst_dev_id=None,
                    transmit_callback=None, receive = False):
        self.packet_queue.append((packet, src_dev_id, dst_dev_id,
                                  transmit_callback, receive))
        if not self.is_transmitting:
            self._send_packet_from_queue()

    def _send_packet_from_queue(self):
        assert not self.is_transmitting
        assert len(self.packet_queue) > 0

        self.is_transmitting = True
        (packet, src_dev_id, dst_dev_id, transmit_callback, receive
        ) = self.packet_queue.pop(0)
        #print(transmit_callack, "AAAAAAA")
        self.send_packetX(packet,receive, src_dev_id, dst_dev_id, self._event_sent_callback, (transmit_callback,))
        #self.sim.send_packet(packet, src_dev_id, dst_dev_id,self._event_sent_callback, (transmit_callback,))

    def send_packetX(self, packet, receive, src_id, dst_id=None, callback=None, callback_args=tuple() ):
        print("Sent packet: ",packet.hex())
        print("Listen to receive data? : ",receive)
        #print('*****Recepcion requerida: ', receive)
        received = self.lora.send(packet.hex(), receive = receive, verbosity = 2)
        if receive:
            if received != None and len(received) > 0 :
                received = received.replace(" ","")
                received = bytes.fromhex(received)
                print('Received in layer 2:',received)
                self.event_receive_packet(dst_id, received)
        if callback != None:
            count = 1
            args = callback_args+(count,)
            callback(*args)
        return count

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

    def set_mtu(self, mtu):
        self.mtu = mtu

    def get_mtu_size(self):
        return self.mtu

#---------------------------------------------------------------------------
