"""
.. module: schc
  "platform: Python, Micropython
"""

"""
This file documents the abstract interface between the core object
protocol.SCHCProtocol and the rest of the system.
It is not intended to be imported nor used in pratical code.

Object composition is used, and an instance of SCHCProtocol should
be provided with 3 instances of classes:
- UpperLayer: the upper layer for SCHC (e.g. layer 3 = IPv6 layer)
- LowerLayer: the lower layer for SCHC (e.g. layer 2 = LPWAN technology layer)
- System: everything that is related to system/implementation details.
  At minimum, System provides a Scheduler object (used for implementing 
  timers), and basic logging.

If UpperLayer, LowerLayer, etc. need anything that is specific to the 
implementation, they would typically recover the System object from the
SCHCProtocol instance with `get_system`.
"""

abstract = None # For writing 'abstract' methods without having to write "pass"

#---------------------------------------------------------------------------

class AbstractUpperLayer:
    """The AbstractUpperLayer is the layer 3 = IPv6 layer.

    It is the object that receives reassembled/decompressed packets from the
    SCHC protocol:
    - received packets are received through its method `recv_packet`
    - packets sent by this layer to SCHC (for compression/fragmentation) should
      be sent by calling the method `schc_send` of the associated SCHCProtocol
      instance
    """

    def _set_protocol(self, protocol):
        """Called automatically by the constructor of protocol.SCHCProtocol. 

        This is because both AbstractUpperLayer and protocol.SCHCProtocol 
        (probably) need a reference to each other, so this gives the 
        opportunity for the AbstractUpperLayer (created first) to get the 
        reference to the associated protocol.SCHCProtocol instance.
        """
        abstract

    def recv_packet(self, address, raw_packet):
        """Called by protocol.SCHCProtocol to pass packets to this upper layer.

        This is called when SCHC has gone through the reassembly/decompression
        process.
        """
        # XXX: call not implemented yet in the code?
        abstract

#---------------------------------------------------------------------------

class AbstractLowerLayer:
    """The AbstractLowerLayer is the layer 2, aka MAC layer, aka LPWAN layer.

    It is the object that receives SCHC packets/fragments/acks to be sent 
    physically (as MAC layer of the LPWAN technology):

    - The associated SCHCProtocol instance will call its method `send_packet`
      to send .
     
    - packets sent by SCHC to this layer (after compression/fragmentation) 
      should be sent by calling the method `schc_recv` of the associated
      SCHCProtocol instance.
    """
    
    def _set_protocol(self, protocol):
        """Called automatically by the constructor of protocol.SCHCProtocol. 

        This is because both AbstractLowerLayer and protocol.SCHCProtocol 
        (probably) need a reference to each other, so this gives the 
        opportunity for the AbstractLowerLayer (created first) to get the 
        reference to the associated protocol.SCHCProtocol instance.
        """
        abstract

    def send_packet(self, packet, other_address, transmit_callback=None):
        """Called by SCHC when a (SCHC) packet is to be sent on the LPWAN.

        :param packet: The SCHC packet, SCHC fragment or SCHC ACK, to be sent
        :param other_address: The (MAC) address of the other side
        :param transmit_callback: A function called after completion of the 
            transmission, with a transmission status (XXX: defined?)
        """
        abstract

    def get_mtu_size(self):
        """Return the current MTU (Maximum Transmission Unit) of this layer.
        """
        abstract

#---------------------------------------------------------------------------

class AbstractScheduler:
    """Allows to schedule events in the future, and cancel them."""

    def get_clock(self):
        """Return the clock in the scheduler.  Any type of value should be
        acceptable as it is logging purpose."""
        abstract

    def add_event(self, time_in_sec, event_function, event_args):
        """Add an event (function) that will be called in the future.

        :param time_in_sec: the delay (compared to current time) after which
            the event_function will be called as `event_function(*event_args)`
        :param event_function: the function that will be called back
        :param event_args: the arguments (usually a tuple) for the function
        :returns: an object (event handle) that can be used to cancel it.
        """
        abstract

    def cancel_event(self, event_handle):
        """Cancel an event that had been scheduled in the future by `add_event`.

        Cancelling an event that has already be run is undefined (XXX: check)

        :param event_handle: the returned object when the event to cancel was
            added with `add_event`
        """
        abstract

#---------------------------------------------------------------------------

class AbstractSystem:
    def get_scheduler(self):
        """Return an instance of a scheduler 

        The returned instance implements the AbstractScheduler interface
        """
        abstract

    def log(self, name, message):
        """Log a message.

        :param name: a string indicated the subsystem (upper layer, 
             fragmentation, etc.) that generated the log. Used for filtering.
        :param message: a string to be printed"""
        abstract

#---------------------------------------------------------------------------
