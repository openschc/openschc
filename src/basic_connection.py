import time
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from gen_utils import dprint, sanitize_value
from compr_core import *
import frag_send # to get types
import frag_recv

from scapy.all import hexdump

import binascii
import cbor2 as cbor

class ScapyLowerLayer:
    def __init__(self, position, socket=None, other_end=None):
        self.protocol = None
        self.position = position
        self.other_end = other_end
        self.sender_delay = 0
        self.sock = socket

    # ----- AbstractLowerLayer interface (see: architecture.py)
        
    def _set_protocol(self, protocol):
        self.protocol = protocol
        self._actual_init()

    def send_packet(self, packet, dest, transmit_callback=None):
        #print ("L2_connection.py: send_pkt, dest ", dest, "packet", packet)
        if dest != None and dest.find("udp") == 0:
            destination = (dest.split(":")[1], int(dest.split(":")[2]))

            res = self.sock.sendto(packet, destination)
            #print ("send status", res, "bytes to", destination )

        elif dest != None and dest.find("lorawan") == 0:
            destination = ("127.0.0.1", 12345)
            device_id = dest.split(":")[1]

            print (destination, device_id)

            msg = {
                1: 1,
                2: binascii.unhexlify(device_id),
                4: packet
            }

            print (binascii.hexlify(cbor.dumps(msg)))
            self.sock.sendto(cbor.dumps(msg), destination)

        else:
            print ("No destination found, not sent:", packet, dest)
            return False

#        else:
#            destination = self.other_end


        # define error_rate rand ou un vecteur avec 0 et 1
        # if error then not send

        if transmit_callback is not None:
            print ("OLD BEHAVIOR", transmit_callback)
            transmit_callback(1)
        #print (self.protocol.sender_delay)
        time.sleep(self.protocol.sender_delay)

    def get_mtu_size(self):
        return 50 # XXX

    # ----- end AbstractLowerLayer interface

    def _actual_init(self):
        pass

    def event_packet_received(self):
        """Called but the SelectScheduler when an UDP packet is received"""
        packet, address = self.sd.recvfrom(MAX_PACKET_SIZE)
        sender_address = address_to_string(address)
        position = self.position
        print ("sender address", sender_address)
        if position == T_POSITION_DEVICE:
            self.protocol.schc_recv(core_id = sender_address, schc_packet = packet)
        else :
            self.protocol.schc_recv(device_id = sender_address, schc_packet = packet)



class ScapyScheduler:
    def __init__(self):
        self.queue = []
        self.clock = 0
        self.next_event_id = 0
        self.current_event_id = None
        self.observer = None
        self.item=0
        self.fd_callback_table = {}
        self.last_show = 0 
        self.session_id = None


    # ----- AbstractScheduler Interface (see: architecture.py)

    def get_clock(self):
        return time.time()
         
    def add_event(self, rel_time, callback, args, session_id = None): #TODO
        assert rel_time >= 0
        event_id = self.next_event_id
        self.next_event_id += 1
        self.session_id = session_id
        clock = self.get_clock()
        abs_time = clock + rel_time
        self.queue.append((abs_time, event_id, callback, args, session_id))
        return event_id

    def cancel_event(self, event):
        item_pos = 0
        item_found = False
        elm = None
        for q in self.queue:
            if q[1] == event:
                item_found = True
                break
            item_pos += 1

        if item_found:
            elm = self.queue.pop(item_pos)

        return elm

    def cancel_session(self, session_id = None): #TODO
        elm = []
        indices = [i for i, x in enumerate(self.queue) if x[4] == session_id]
        self.queue = [i for j, i in enumerate(self.queue) if j not in indices]
        return elm

    # ----- Additional methods

    def _sleep(self, delay):
        """Implements a delayfunc for sched.scheduler
        This delayfunc sleeps for `delay` seconds at most (in real-time,
        but if any event appears in the fd_table (e.g. packet arrival),
        the associated callbacks are called and the wait is stop.
        """
        self.wait_one_callback_until(delay)


    def wait_one_callback_until(self, max_delay):
        """Wait at most `max_delay` second, for available input (e.g. packet).
        If so, all associated callbacks are run until there is no input.
        """
        fd_list = list(sorted(self.fd_callback_table.keys()))
        print (fd_list)
        while True:
            rlist, unused, unused = select.select(fd_list, [], [], max_delay)
            if len(rlist) == 0:
                break
            for fd in rlist:
                callback, args = self.fd_callback_table[fd]
                callback(*args)
            # note that sched impl. allows to return before sleeping `delay`

    def add_fd_callback(self, fd, callback, args):
        assert fd not in self.fd_callback_table
        self.fd_callback_table[fd] = (callback, args)

    def run(self, session=None, display_period=None): 
        factor= 10
        if self.item % factor == 0:
            seq = ["|", "/", "-", "\\", "-"]
            print ("{:s}".format(seq[(self.item//factor)%len(seq)]),end="\b", flush=True)
        self.item +=1

        if display_period and time.time() - self.last_show > display_period: # display the event queue every minute
            print ("*"*40)
            print ("EVENT QUEUE")
            self.last_show = time.time()
            for q in self.queue:
                print ("{0:6.2f}: id.{1:04d}".format(q[0]-time.time(), q[1]), q[2])

            if session:
                print ("-"*30)
                for s in session.session_manager.session_table:
                    s_id = "{}-{}/{}-{}".format(s[0], s[1], s[2],s[3])
                    print ("{:10} |".format(s_id), end="")
                    if isinstance(session.session_manager.session_table[s], frag_send.FragmentNoAck):
                        print ("Sending NoAck")
                    elif isinstance(session.session_manager.session_table[s], frag_recv.ReassemblerNoAck):
                        print ("Receiving NoAck ", end="")
                        print (len(session.session_manager.session_table[s].tile_list), "tiles")
                    else:
                        print (session.session_manager.session_table[s])
            print ("*"*40)

        while len(self.queue) > 0:
            self.queue.sort()

            wake_up_time = self.queue[0][0]
            if time.time() < wake_up_time:
                return

            event_info = self.queue.pop(0)
            self.clock, event_id, callback, args, session_id = event_info
            self.current_event_id = event_id
            if self.observer is not None:
                self.observer("sched-pre-event", event_info)
            callback(*args)
            if self.observer is not None:
                self.observer("sched-post-event", event_info)
            if display_period:
                print("Queue running event -> {}, callback -> {}".format(event_id, callback.__name__))

# --------------------------------------------------        

class ScapySystem:
    def __init__(self):
        self.scheduler = ScapyScheduler()

    def get_scheduler(self):
        return self.scheduler

    def log(self, name, message):
        print(name, message)

# --------------------------------------------------
