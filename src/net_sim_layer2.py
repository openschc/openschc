"""
.. module:: net_sim_layer2
   :platform: Python, Micropython
"""
#---------------------------------------------------------------------------
#from stats.statsct import Statsct

from gen_utils import dprint
import warnings

class SimulLayer2:
    """
    The layer 2 of LPWA is not symmetry.
    The LPWA device must know the devaddr assigned to itself before processing
    the SCHC packet.
    The SCHC gateway must know the devaddr of the LPWA device before
    transmitting the message to the NS.  And, it must know the devaddr
    when it receives the message from the NS.
    Therefore, in this L2 simulation layer, the devaddr must be configured
    before it starts by calling set_devaddr().
    """
    __mac_id_base = 0

    def __init__(self, sim):
        self.sim = sim
        self.protocol = None
        self.device_id = None
        self.core_id = None
        self.receive_function = None
        self.event_timeout = None
        self.counter = 1 # XXX: replace with is_transmitting?
        self.is_transmitting = False
        self.packet_queue = []
        self.mtu = 56
        self.role = None 
        self.id = None

    def _set_protocol(self, protocol):
        self.protocol = protocol
        #Statsct.addInfo('protocol', protocol.__dict__)
    
    def set_id(self, id):
        self.id = id

    def set_receive_callback(self, receive_function):
        self.receive_function = receive_function

    def send_packet(self, packet, dest, transmit_callback=None):
        # Note: transmit_callback should wait for one argument, indicating if the transmission was ok
        print ("net_sim_layer2.py: send_packet, dest ", dest, "packet", packet, "transmitting ?", self.is_transmitting)
        # here, we could limit queue size, and drop packet if queue full, with proper call to transmit_callback(False) :
        self.packet_queue.append((packet, None, dest, transmit_callback))
        if not self.is_transmitting:
            self._send_packet_from_queue()

    def _send_packet_from_queue(self):
        assert not self.is_transmitting
        assert len(self.packet_queue) > 0

        self.sim._log(f"(XXX dbg-sched) _send_packet_from_queue {len(self.packet_queue)}")
        self.is_transmitting = True
        (packet, src_dev_id, dst_dev_id, transmit_callback) = self.packet_queue.pop(0)

        dprint("++++++++++++ src, dst -- ", src_dev_id, dst_dev_id)
        dprint("send packet from queue -> {}, {}, {}, {}".format(packet, src_dev_id, dst_dev_id, transmit_callback is None))
        print("src_dev_id, dst_dev_id", src_dev_id, src_dev_id, self.is_transmitting)
        self.sim.send_packet(packet, src_dev_id, dst_dev_id, self._event_sent_callback, transmit_callback) # Calls send_packet in net_sim_core.py

    def _event_sent_callback(self, transmit_callback):
        assert self.is_transmitting
        self.is_transmitting = False
        warnings.warn("transmit_callback() is back")
        self.is_transmitting = False
        #if transmit_callback != None:
            #transmit_callback(status)
        if len(self.packet_queue) > 0:
            self._send_packet_from_queue()
        if transmit_callback != None:
            transmit_callback(True) # transmission was ok

    def event_receive_packet(self, other_mac_id, packet):
        dprint("+++++ ---- event_receive_packet device_id", self.device_id)
        dprint("+++++ ---- event_receive_packet other_mac", other_mac_id)
        dprint("event_receive_packet core_id", self.core_id)
        dprint("event_receive_packet position", self.protocol.position)
        assert self.protocol != None
        assert self.device_id is not None
        assert self.core_id is not None
        self.protocol.schc_recv(packet, device_id=self.device_id, core_id = self.core_id)


    @classmethod
    def __get_unique_mac_id(cls):
        result = cls.__mac_id_base
        cls.__mac_id_base += 1
        return result

    def set_device_id(self, devaddr):
        self.device_id = devaddr

    def set_core_id(self, devaddr):
        self.core_id = devaddr

    def set_mtu(self, mtu):
        self.mtu = mtu
        self.protocol.connectivity_manager.set_mtu(mtu)

    def get_mtu_size(self):
        return self.mtu

#---------------------------------------------------------------------------
