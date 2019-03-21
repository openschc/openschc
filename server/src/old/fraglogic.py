#---------------------------------------------------------------------------

import warnings
import struct

import sys
sys.path.append("../../PLIDO-tanupoo")
import fragment
#import schc_fragment as fragment

sys.path.append("../python")
import BitBuffer as BitBufferModule

#---------------------------------------------------------------------------

class BitBuffer_XXX(BitBufferModule.BitBuffer):
    #XXX debug and put in BitBuffer.py
    def __init__(self, *args, **kwargs):
        BitBufferModule.BitBuffer.__init__(self, *args, **kwargs)
    
    def add_bits(self, bits_as_long_int, nb_bits):
        for i in range(nb_bits, -1, -1):
            self.add_bit(bits_as_long_int & (1 << i))

    pop_bit = BitBufferModule.BitBuffer.next_bit

    def pop_bits(self, nb_bits):
        result = 0
        for i in range(nb_bits, -1, -1):
            if self.pop_bit():
                result |= (1<<i)

    def pop_byte(self):
        return self.pop_bits(8)

    def pop_bytes(self, nb_bytes):
        return bytearray([self.pop_byte() for i in range(nb_bytes)])

    def get_content(self):
        return self._buf[:]

    
class FakeBitBuffer:
    def __init__(self, content = []):
        self.content = content[:]
        
    def add_bits(self, bits_as_long, nb_bits):
        self.content.append((bits_as_long, nb_bits))

    def get_bits(self, nb_bits):
        bits_as_long, added_nb_bits = self.content.pop(0)
        assert nb_bits == added_nb_bits
        return bits_as_long

    def get_content(self):
        return self.content[:]

    
def test_BitBuffer():
    bitbuffer = FakeBitBuffer()
    bitbuffer.add_bits(0xf, 4)
    bitbuffer.add_bits(0,   2)
    bitbuffer.add_bits(0x1, 2)
    for i in range(3):
        bitbuffer.add_bits(0,   1)
        bitbuffer.add_bits(0x1, 1)
    bitbuffer.add_bits(0x3, 2)
    print(bitbuffer.get_content())
    #print([bin(x) for x in bitbuffer.get_content])


#test_BitBuffer(); exit_now()

        

#---------------------------------------------------------------------------
        
RELIABILITY_OPTION_LIST = ["no-ack", "window", "ack-on-error"]

class SchcFragmentFormat:
    def __init__(self, R, T, N, M, mode="window"):
        if mode not in RELIABILITY_OPTION_LIST:
            raise ValueError("unknown reliability option", mode)
        self.R = R
        self.T = T
        self.N = N
        self.M = M
        self.mode = mode
        
        if self.mode == "no-ack":
            self.window_field_bitsize = 0
        else: self.window_field_bitsize = 1

        #   880	   fragments format this field has a size of R - T - N - 1 bits when
        #   881	   Window mode is used.  In No ACK mode, the Rule ID field has a size of
        #   882	   R - T - N bits see format section.
        self.rule_id_bitsize = (self.R - self.T - self.N
                                - self.window_field_bitsize)

        assert self.rule_id_bitsize >= 0
        assert self.N >= 1
        assert self.mode == "window" # XXX in this version of the code

    def get_all_0(self):
        return 0

    def get_all_1(self):
        return 2**self.N - 1

    def get_fcn_max(self):
        """maximum value of the FCN, itself included"""
        self.fcn_max = 2**self.N - 2

    def pack_fragment(self, rule_id, dtag, window_index, advertized_fcn, 
                      payload, mic = b""):
        #  1013	                <------------ R ---------->
        #  1014	                          <--T--> 1 <--N-->
        #  1015	               +-- ... --+- ... -+-+- ... -+---...---+
        #  1016	               | Rule ID | DTag  |W|  FCN  | payload |
        #  1017	               +-- ... --+- ... -+-+- ... -+---...---+
        #
        # and
        #
        # 1105	         <------------ R ------------>
        # 1106	                    <- T -> 1 <- N -> <---- M ----->
        # 1107	         +-- ... --+- ... -+-+- ... -+---- ... ----+---...---+
        # 1108	         | Rule ID | DTag  |W| 11..1 |     MIC     | payload |
        # 1109	         +-- ... --+- ... -+-+- ... -+---- ... ----+---...---+
        
        bit_buffer = FakeBitBuffer()
        bit_buffer.add_bits(rule_id, self.rule_id_bitsize)
        bit_buffer.add_bits(dtag, self.T)
        bit_buffer.add_bits(window_index%2, 1)
        bit_buffer.add_bits(advertized_fcn, self.N)
        assert (    (len(mic) == 0 and advertized_fcn != self.get_all_1())
                 or (len(mic) != 0 and advertized_fcn == self.get_all_1()))
        if len(mic) > 0:
            bit_buffer.add_bits(mic, self.M)
        bit_buffer.add_bits(payload, 8*len(payload))
        return bit_buffer.get_content()

    def pack_empty_fragment(self, advertized_fcn):
        #  1083	                 <------------ R ------------>
        #  1084	                            <- T -> 1 <- N ->
        #  1085	                 +-- ... --+- ... -+-+- ... -+
        #  1086	                 | Rule ID | DTag  |W|  0..0 |   TODO
        #  1087	                 +-- ... --+- ... -+-+- ... -+
        #  1088	
        #  1089	                  Figure 13: All-0 empty format fragment
        
        # XXX
        raise RuntimeError("Not implemented yet: XXX")

    def unpack_fragment_or_ack(self):
        pass

    def pack_ack(self, XXX):
        pass


#---------------------------------------------------------------------------


INTER_FRAGMENT_DELAY = 1.0 # seconds
WAIT_BITMAP_TIMEOUT = 5.0 # seconds

class WindowAckModeSender:
    """The fragmentation manager handles the logic of the fragment sending etc.
    """
    
    def __init__(self, system_manager, fragment_format_XXX_unused, full_packet,
                 rule_id, dtag, window_max_size, fragment_size):
        self.rule_id = rule_id
        self.dtag = dtag
        R = 16 # header size
        T = 4  # DTag size
        N = 4  # FCN size
        M = 8  # MIC size
        BITMAP_SIZE = 8 # bits
        
        self.system_manager = system_manager
        
        # XXX: use soichi code again:
        #fragment.fp = fragment_format #XXX: hack
        #self.fragment = fragment.fragment(
        #    srcbuf=full_packet, rule_id=rule_id, dtag=dtag,
        #    noack=False, window_size=window_size)
        ##self.fragment = fragment.fragment(
        ##    srcbuf=full_packet, dtag=dtag, rid=rule_id)
        #print(self.fragment.__dict__) #XXX
        
        self.fragment_size = fragment_size
        self.nb_fragment = (len(full_packet) + fragment_size-1) // fragment_size

        # 1376     Intially, when a fragmented packet need to be sent, the window is set
        # 1377     to 0, a local_bit map is set to 0, and FCN is set the the highe
        # 1378     possible value depending on the number of fragment that will be sent
        # 1379     in the window (INIT STATE).
        self.state = "INIT"
        self.window_index = 0

        # (some of these variables are duplicates of the class fragment.fragment)

        self.full_packet = full_packet
        self.full_packet_position = 0
        
        self.window_index = 0        
        self.window_max_size = window_max_size
        
        self.R = R
        self.T = T
        self.N = N
        self.M = M
        self.format_mgr = SchcFragmentFormat(R=R, T=T, N=N, M=M, mode="window")
        
        print("STATE INIT, fragmentation parameters:")
        print("  nb_fragment={}".format(self.nb_fragment))
        print("  fragment_size={}".format(fragment_size))
        print("  R(header size)={}".format(self.R))
        print("  T(DTag size)={}".format(self.T))
        print("  N(FCN size)={}".format(self.N))

        self.init_current_window()

        
    def init_current_window(self):
        # pre-compute the fragments to send in the window, and init variables.
        # (the fragment_size is allowed to be changed between windows)
        
        assert self.full_packet_position < len(self.full_packet)
        remaining_nb_byte = len(self.full_packet) - self.full_packet_position
        remaining_nb_fragment = (
            (remaining_nb_byte + self.fragment_size-1) // self.fragment_size )

        assert remaining_nb_fragment > 0
        self.is_last_window = (remaining_nb_fragment < self.window_max_size)
        if not self.is_last_window:
            self.window_size = self.window_max_size
        else: self.window_size = remaining_nb_fragment 

        p, fs = self.full_packet_position, self.fragment_size
        self.fragment_list = [ self.full_packet[p+i*fs:p+(i+1)*(fs)]
                               for i in range(self.window_size)]
        self.window_fragment_index = 0
        
        print("window #{} last={} nb_frag={}\n  frag={}".format(
            self.window_size, self.is_last_window, self.window_size,
            self.fragment_list))

    #--------------------------------------------------

    def start(self):
        assert self.state == "INIT"
        self.state = "SEND"
        self.send_current_fragment()
        
    def get_current_fcn(self):
        fi = self.window_fragment_index
        if self.is_last_window and fi == self.window_size-1:
            #   913	   are expected when there is no error.  The FCN for the last fragment
            #   914	   is an all-1.  It is also important to note that, for No ACK mode or
            return self.format_mgr.get_all_1(), True
        else:
            return self.window_size-1 - fi, False

    def send_current_fragment(self):
        assert self.state == "SEND"
        frag_content = self.fragment_list[self.window_fragment_index]
        advertized_fcn, is_very_last_fragment = self.get_current_fcn()
        
        if is_very_last_fragment:
            mic = self.mic
        else: mic = b""
            
        full_fragment = self.format_mgr.pack_fragment(
            rule_id = self.rule_id, dtag = self.dtag,
            window_index = self.window_index,
            advertized_fcn = advertized_fcn,
            payload = frag_content, mic = mic
        )
        self.system_manager.send_packet(full_fragment)

        # 1384	   regulation rules or constraints imposed by the applications.  Each
        # 1385	   time a fragment is sent the FCN is decreased of one value and the
        # 1386	   bitmap is set.  The send state can be leaved for different reasons
        # XXX: is the bitmap the one of the FCN?
        
        if self.window_fragment_index == self.window_size-1:
            # 1386	   bitmap is set.  The send state can be leaved for different reasons
            # 1387	   (for both reasons it goes to WAIT BITMAP STATE):
            self.state = "WAIT BITMAP"
            
            if is_very_last_fragment:
                # 1471	   [...] FCN==0 & more frags [...]
                # 1389	   o  The FCN reaches value 0 and there are more fragments.  In that
                # 1390	      case an all-0 fragmet is sent and the timer is set.  The sender
                # 1391	      will wait for the bitmap acknowledged by the receiver.
                self.system_manager.add_event(
                    WAIT_BITMAP_TIMEOUT,
                    self.event_wait_bitmap_timeout_check, (self.window_index, False))
            else:
                # 1471	   [...] last frag [...]
                # 1393	   o  The last fragment is sent.  In that case an all-1 fragment with
                # 1394	      the MIC is sent and the sender will wait for the bitmap
                # 1395	      acknowledged by the receiver.  The sender set a timer to wait for
                # 1396	      the ack.
                self.system_manager.add_event(
                    WAIT_BITMAP_TIMEOUT,
                    self.event_wait_bitmap_timeout_check, (self.window_index, True))
        else:
            self.window_fragment_index += 1
            self.system_manager.add_event(
                INTER_FRAGMENT_DELAY, self.event_next_fragment, ())

    
    #--------------------------------------------------


    def send_empty_fragment(self):
        # 1410	   In ACK Always, if the timer expire, an empty All-0 (or All-1 if the
        # 1411	   last fragment has been sent) fragment is sent to ask the receiver to
        if self.is_last_window:
            advertized_fcn = self.format_mgr.get_all_0()
        else: advertized_fcn = self.format_mgr.get_all_1()
        
        XXX
        self.system_manager.send_packet(empty_fragment)

    def is_finished(self):
        return not (self.position < len(self.full_packet))
        
    def get_next_fragment_real(self):
        return self.fragment.next_fragment(self.fragment_size)


    def event_next_fragment(self):
        assert self.state == "SEND"
        # 1464	[...] send Window + frag(FCN)
        self.send_current_fragment()
        
    def event_wait_bitmap_timeout_check(self, window_index, final):
        assert window_index <= self.window_index
        if window_index != self.window_index:
            return # not really a time out (as window_index has progressed)
        assert self.state == "WAIT BITMAP"
        # 1410	   In ACK Always, if the timer expire, an empty All-0 (or All-1 if the
        # 1411	   last fragment has been sent) fragment is sent to ask the receiver to
        # 1412	   resent its bitmap.  The window number is not changed.
        print("WAIT BITMAP: timeout")
        warnings.warn("XXX:should implement MAX_ATTEMPTS")
        self.send_empty_fragment()
        self.system_manager.add_event(
            WAIT_BITMAP_TIMEOUT,
            self.event_wait_bitmap_timeout_check, (self.window, True))

    def event_packet(self, raw_packet):
        #print("RECEIVE", raw_packet)
        if self.state == "INIT":
            print("ERROR: unexpected packet in state INIT", raw_packet)
            return
        elif self.state == "SEND":
            print("ERROR: unexpected packet in state SEND", raw_packet)
            return
        elif self.state == "WAIT BITMAP":
            # XXX:how do we know the packet format?:
            self.process_ack(raw_packet)
        else: raise RuntimeError("unexpected state", self.state)

    def process_ack(self, raw_packet):
        warnings.warn("XXX:hardwired formats, sizes, constants")
        window, bitmap = struct.unpack(b"!BB", raw_packet)
        bitmap = bitmap >> 1 # XXX - only for hardcoded case
        print("ACK", window, bitmap, self.bitmap)
        # 1662	   If the window number on the received bitmap is correct, the sender
        if window != self.window:
            print("ERROR: bad window number", window, self.window)
            return
        if bitmap & ~self.bitmap != 0: 
            print("ERROR: inconsistent bitmap", bitmap, self.bitmap)
            # XXX: what to do? - should not happen except for last
            return

        resend_bitmap = self.bitmap & ~bitmap
        if resend_bitmap == 0:
            # 1662	   If the window number on the received bitmap is correct, the sender
            # 1663	   compare the local bitmap with the received bitmap.  If they are equal
            # 1664	   all the fragments sent during the window have been well received.  If
            
            if not self.is_finished():
                # 1665	   at least one fragment need to be sent, the sender clear the bitmap,
                # 1666	   stop the timer and move its sending window to the next value.  If no
                
                # XXX: (optional) stop timer
                self.window_index += 1
                self.window = self.window+1 # XXX!!: modulo
                nb_remaining_fragment = (self.nb_fragment
                                         - self.window_size * self.window_index)
                print("UPDATE:", nb_remaining_fragment, self.nb_fragment,
                      self.window_size, self.window_index)
                self.fcn = min(nb_remaining_fragment, self.max_fcn) # XXX:factor in
                unfinished, packet = self.get_next_fragment()
                self.state = "SEND"                
                self.send_fragment_and_prepare_next(packet, unfinished)

            else:
                # 1667	   more fragments have to be sent, then the fragmented packet
                # 1668	   transmission is terminated.
                self.state = "END"
                self.event_transmission_completed()
                
        else:
            # 1670	   If some fragments are missing (not set in the bit map) then the
            # 1671	   sender resend the missing fragments.  When the retransmission is
            # 1672	   finished, it start listening to the bitmap (even if a All-0 or All-1
            # 1673	   has not been sent during the retransmission) and returns to the
            # 1674	   waiting bitmap state.

            # 1685	   If the local-bitmap is different from the received bitmap the counter
            # 1686	   Attemps is increased and the sender resend the missing fragments
            # 1687	   again, when a MAX_ATTEMPS is reached the sender sends an Abort and
            # 1688	   goes to error.
            raise NotImplementedError("XXX not implemented yet, sorry")

    def event_transmission_completed(self):
        print("transmssion completed")
        
    def get_current_fragment(self):
        print("fragment window={} fcn={} current_frag_index={}".format(
            self.window, self.fcn, self.fragment_index))
        header = struct.pack(b"!BB", self.window, self.fcn)
        return header + bytes(self.content[self.fragment_index].encode("ascii"))

    def process_ack_old(self, raw_packet):
        # Next fragment
        self.window = (self.window+1) % 2 # protocol
        self.fcn = self.max_fcn_per_window # - because it will be the first of the new window
        self.fragment_index += 1 # internal data structure

        if self.fragment_index == len(self.content):
            print("Finished trasnmission of fragments")
            return b""

        if self.fragment_index == len(self.content)-1:
            self.fcn = 1 # protocol - because it is the end of the content in this case
            return self.get_current_fragment() # XXX + "MIC"
        else:
            return self.get_current_fragment()

#---------------------------------------------------------------------------
