
from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg
from schctile import TileList

#---------------------------------------------------------------------------
# XXX: put rule_manager

Rule = namedtuple("Rule", "rule_id_size dtag_size window_size"
                  + " fcn_size mode tile_size mic_algorithm")

def rule_from_dict(rule_as_dict):
    rule_as_dict = { k.replace("-","_"): v for k,v in rule_as_dict.items() }
    return Rule(**rule_as_dict)

#---------------------------------------------------------------------------

class FragmentAckOnError():
    def __init__(self, protocol, rule, profile=None):
        self.protocol = protocol
        self.rule = rule
        self.profile = profile
        self.dtag = 0
        self.event_timeout = 5
        self.retry_counter = 0

    def set_packet(self, packet):
        #self.rule_only_for_hackathon103 = rule # XXX this must be removed.
        self.tile_list = TileList(self.rule, packet)
        # update dtag for next
        self.dtag += 1
        if self.dtag > pow(2,self.rule.dtag_size-1):
            self.dtag = 0

    def get_frags(self):
        '''
        get contiguous fragments to be sent.
        '''
        mtu_size = self.protocol.layer2.get_mtu_size()
        max_tiles = int((mtu_size - schcmsg.get_header_size(self.rule)) /
                     self.rule.tile_size)
        tiles = self.tile_list.get_tiles(max_tiles)
        if tiles is not None:
            return schcmsg.frag_sender_tx(
                self.rule, rule_id=self.rule.rule_id, dtag=self.dtag,
                win=tiles[0]["w-num"], fcn=tiles[0]["t-num"],
                payload=TileList.get_bytearray(tiles))
        else:
            return None

    def send_frag(self):
        frag = self.get_frags()
        if frag is None:
            return
        src_dev_id = self.protocol.layer2.mac_id
        print(frag)
        print(src_dev_id, frag.packet.get_content())
        args = (frag.packet.get_content(), src_dev_id, None,
                self.event_sent_frag)
        self.protocol.scheduler.add_event(0, self.protocol.layer2.send_packet,
                                          args)

    def start_sending(self):
        self.send_frag()

    def event_sent_frag(self, status): # status == nb actually sent (for now)
        self.update_frags_sent_flag()
        self.send_frag()

    def update_frags_sent_flag(self):
        self.tile_list.update_sent_flag()

    def recv_ack(self, packet, peer_iid=None):
        print("DEBUG: recv_ack:", packet)  # XXX
        message = schcmsg.frag_sender_rx(packet, self.rule, self.dtag)

        print("parsed message:", message.__dict__, message.payload.__dict__)

        if message.cbit == 0:
            self.tile_list.unset_sent_flag(message.win, message.bitmap)
            self.send_frag()
        elif message.cbit == 1:
            #XXX
            pass
        else:
            #XXX
            pass

    def recv_frag(self, packet, peer_iid=None):
        s = self.find_session(peer_iid=peer_iid)
        if s is None:
            # add it as a new session.
            # XXX rule = rulemanager.find_rule(...)
            rule = self.rule_only_for_hackathon103
            s = fragment_receiver(packet, peer_iid=peer_iid,
                                  config=self.config, rule=rule,
                                  scheduler=self.scheduler,
                                  layer2=self.layer2)
            return
        s.recv_frag(packet)

    def find_session(self, peer_iid=None):
        if peer_iid:
            for i in self.session_list:
                if i.peer_iid == peer_iid:
                    return i
            else:
                return None
        else:
            # XXX
            return None



#---------------------------------------------------------------------------

# temporary class before merging after hackathon
class SCHCProtocolSender(schc.SCHCProtocol):
    '''
    assuming that there is only one session to be handled.
    '''
    def __init__(self, *args, **kwargs):
        schc.SCHCProtocol.__init__(self, *args, **kwargs)
        self.session = FragmentAckOnError(self, None) # XXX:hack

    def set_frag_rule(self, rule): #XXX: hack
        schc.SCHCProtocol.set_frag_rule(self, rule)
        self.session.rule = rule

    def send_packet(self, packet, peer_iid=None):
        # Should do:
        # - compression
        # - fragmentation
        # (and sending packets)
        #compression_rule = XXX
        #self.compression_manager.compress(compression_rule)
        packet = packet[:]  # Null compression

        # XXX:TODO select the rule
        self.session.set_packet(packet)
        frag = self.session.get_frags()
        self.scheduler.add_event(0, self.layer2.send_packet,
                                 (frag.packet.get_content(),))
        self.session.update_frags_sent_flag()
        #self.scheduler.add_event(1, self.event_receive_packet, (frag,))
        '''
        if not self.rule["ack-after-recv-all1"]:
            self.event_timeout = self.scheduler.add_event(
                    3, self.recv_ack_timeout, None)
        '''

    '''
    def recv_ack_timeout(self):
        # XXX check the retry counter.
        if self.retry_coounter > self.rule["retry-counter"]:
            print("DEBUG: stop sending due to limit the retry counter.")
            # XXX send_sender_abort()
            return
        self.send_frag(self.peer_iid)
    '''

    def event_receive_packet(self, peer_id, raw_packet):
        '''
        if self.session.is_ack_timeout():
            print("DEBUG: ack timeout. XXX send sender-abort.")
            return
        '''
        print("DEBUG: S<R: [mac%s] -> SCHC[mac:%s] %s"
              % (self.layer2.iid, peer_id, packet))
        self.session.process_packet(raw_packet)
        self.session.recv_ack(packet, peer_iid=self.layer2.iid)

#---------------------------------------------------------------------------
