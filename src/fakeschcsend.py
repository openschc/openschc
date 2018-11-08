
from base_import import *  # used for now for differing modules in py/upy

import schc
import schcmsg
from fakerulemgr import rule_from_dict

#---------------------------------------------------------------------------

def make_test_fragment_list(rule, rule_id, dtag, fragment_count):
    one_tile = 30 * b"\0"
    message_list = []

    max_fcn = schcmsg.get_MAX_WIND_FCN(rule)
    fcn_all_1 = schcmsg.get_fcn_all_1(rule)
    current_fcn = max_fcn
    window_number = 0
    for fragment_idx in range(fragment_count):
        message = schcmsg.frag_sender_tx(
            rule, rule_id=rule_id, dtag=dtag, win=window_number,
            fcn=current_fcn, payload=one_tile)
        if current_fcn == 0:
            current_fcn = max_fcn
            window_number += 1
        else:
            current_fcn -= 1
        raw_packet = message.packet.content
        message_list.append(raw_packet)

    message = schcmsg.frag_sender_tx(
        rule, rule_id=rule_id, dtag=dtag, win=window_number,
        fcn=fcn_all_1, mic=b"\0\0\0\0", payload=one_tile)
    raw_packet = message.packet.content
    message_list.append(raw_packet)

    return message_list

#---------------------------------------------------------------------------

class FakeSCHCProtocolSender(schc.SCHCProtocol):

    def start_sending(self):
        packet_list = make_test_fragment_list(
            self.rule, rule_id=9, dtag=1, fragment_count=10)

        for i,packet in enumerate(packet_list):
            self.scheduler.add_event(2*i, self.layer2.send_packet, (packet,))

    def event_receive_packet(self, peer_id, packet):
        pass

#---------------------------------------------------------------------------

def test_make_test_fragment(rule):
    fragment_list = make_test_fragment_list(rule, rule_id=9, dtag=1,
                                            fragment_count=10)

    for i,fragment in enumerate(fragment_list):
        print(i, fragment)

#---------------------------------------------------------------------------
