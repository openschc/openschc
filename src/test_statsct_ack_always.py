#---------------------------------------------------------------------------

from gen_base_import import *  # used for now for differing modules in py/upy

import protocol
import net_sim_sched
import net_sim_layer2
import net_sim_core
from gen_rulemanager import RuleManager
import math
#import statsct static class 
from stats.statsct import Statsct
try:
    from ucollections import OrderedDict
except ImportError:
    from collections import OrderedDict
#---------------------------------------------------------------------------



rule_context = {
    "devL2Addr": "*",
    "dstIID": "*"
}

compress_rule = {
    "ruleLength": 3,
    "ruleID": 5,
    "compression": {
        "rule_set": []
    }
}

frag_rule1 = {
    "ruleLength": 6,
    "ruleID": 1,
    "profile": { "L2WordSize": 8 },
    "fragmentation": {
        "FRMode": "AckOnError",
        "FRModeProfile": {
            "dtagSize": 2,
            "WSize": 3,
            "FCNSize": 3,
            "ackBehavior": "afterAll1",
            "tileSize": 392,
            "MICAlgorithm": "RCS_RFC8724",
            "MICWordSize": 8
        }
    }
}

frag_rule2 = {
    "ruleLength": 6,
    "ruleID": 2,
    "profile": { "L2WordSize": 8 },
    "fragmentation": {
        "FRMode": "AckOnError",
        "FRModeProfile": {
            "dtagSize": 2,
            "WSize": 3,
            "FCNSize": 3,
            "ackBehavior": "afterAll1",
            "tileSize": 392,
            "MICAlgorithm": "RCS_RFC8724",
            "MICWordSize": 8
        }
    }
}
#tile size 240 bytes -> 1920 bits
#49 -> 392
frag_rule3 = {
    "ruleLength": 6,
    "ruleID": 1,
    "profile": {
        "L2WordSize": 8
    },
    "fragmentation": {
        "FRMode": "NoAck",
        "FRModeProfile": {
            "dtagSize": 2,
            "FCNSize": 3,
            "MICAlgorithm": "RCS_RFC8724",
            "MICWordSize": 8
        }
    }
}

frag_rule4 = {
    "ruleLength": 6,
    "ruleID": 2,
    "profile": {
        "L2WordSize": 8
    },
    "fragmentation": {
        "FRMode": "NoAck",
        "FRModeProfile": {
            "dtagSize": 2,
            "FCNSize": 3,
            "MICAlgorithm": "RCS_RFC8724",
            "MICWordSize": 8
        }
    }
}



#---------------------------------------------------------------------------

def make_node(sim, rule_manager, devaddr=None, extra_config={}):
    node = net_sim_core.SimulSCHCNode(sim, extra_config)
    node.protocol.set_rulemanager(rule_manager)
    if devaddr is None:
        devaddr = node.id
    node.layer2.set_devaddr(devaddr)
    return node

#---------------------------------------------------------------------------
#lost_rate in %
loss_rate = 10
loss_config = {"mode":"rate", "cycle":loss_rate}
#loss_config = None
#L2 MTU size in bits - byte
#l2_mtu = 56
#Size of data in bytes
#data_size = 14

l2_mtu = 408 #in bits
SF = 12

#l2_mtu = 1936
#SF = 8
# EU863-870 band, maximum payload size:
#         DR0 = SF12: 51 bytes - 408 bits
#         DR1 = SF11: 51 bytes - 408 bits
#         DR2 = SF10: 51 bytes - 408 bits
#         DR3 = SF9: 115 bytes - 920 bits
#         DR4 = SF8: 242 bytes - 1936 bits
#         DR5 = SF7: 242 bytes - 1936 bits

#For US902-928:
#         DR0: 11 - 88 bits
#         DR1: 53 - 424 bits
#         DR2: 125 - 1000 bits
#         DR3: 242 - 1936 bits
#         DR4: 242 - 1936 bits

#---------------------------------------------------------------------------
#Configuration of test_statsct
#Number of repetitions
repetitions = 1
sim_results = []
total_results = OrderedDict()
test_file = False
fileToSend = "testfile_large.txt"
#fileToSend = "testfile.txt"
data_size = 300 #Size of data in bytes

min_packet_size = int(l2_mtu /8) #byes
#min_packet_size = 60 #60
min_packet_size = 251 #60
max_packet_size = 1290 #bytes 
#packet_sizes = [80,160,320,640,1280]
#packet_sizes = [320]
#packet_sizes = [320,640,1280]
packet_sizes = [80,160,320,640]
packet_sizes = [80]

tile_size = 49
#tile_size = 240
payload_ack_always = tile_size * 2
ack_on_error = True
#---------------------------------------------------------------------------
""" Init stastct module """
Statsct.initialize()
Statsct.log("Statsct test")
Statsct.set_packet_size(data_size)
Statsct.set_SF(SF)
#---------------------------------------------------------------------------

#no-ack
rm0 = RuleManager()
rm0.add_context(rule_context, compress_rule, frag_rule3, frag_rule4)

rm1 = RuleManager()
rm1.add_context(rule_context, compress_rule, frag_rule4, frag_rule3)
#ack-on-error
if ack_on_error:
    rm0 = RuleManager()
    rm0.add_context(rule_context, compress_rule, frag_rule1, frag_rule2)

    rm1 = RuleManager()
    rm1.add_context(rule_context, compress_rule, frag_rule2, frag_rule1)

#--------------------------------------------------

simul_config = {
    "log": True,
}
if loss_config is not None:
    simul_config["loss"] = loss_config

#for packet_size in range(min_packet_size, max_packet_size,11):
for packet_size in packet_sizes:
    temp_packet_size = packet_size
    repetitions = math.ceil(packet_size / payload_ack_always)
    print("repetitions -> {}".format(repetitions))
    for i in range(repetitions):
        print("{}".format(temp_packet_size))
        if temp_packet_size >= payload_ack_always:
            temp_packet_size -= payload_ack_always
            send_data = payload_ack_always
            print("if packet_size: {}, temp_packet_size:{}, send_data:{}".format(packet_size,temp_packet_size,send_data))
        else:
            send_data = temp_packet_size
            temp_packet_size = 0
            #break
        
        print("0packet_size: {}, temp_packet_size:{}, send_data:{}".format(packet_size,temp_packet_size,send_data))
        

        print("packet_size - > {}".format(send_data))
        #input('')
        #for i in range(repetitions):
        print("packet_size - > {}".format(send_data))
        #---------------------------------------------------------------------------
        """ Init stastct module """
        Statsct.initialize()
        Statsct.log("Statsct test")
        Statsct.set_packet_size(send_data)
        #---------------------------------------------------------------------------
        Statsct.get_results()
        sim = net_sim_core.Simul(simul_config)
        devaddr = b"\xaa\xbb\xcc\xdd"
        node0 = make_node(sim, rm0, devaddr)    # SCHC device
        node1 = make_node(sim, rm1, devaddr)    # SCHC gw
        sim.add_sym_link(node0, node1)
        node0.layer2.set_mtu(l2_mtu)
        node1.layer2.set_mtu(l2_mtu)

        print("SCHC device L3={} L2={} RM={}".format(node0.layer3.L3addr, node0.id,
                                                    rm0.__dict__))
        print("SCHC gw     L3={} L2={} RM={}".format(node1.layer3.L3addr, node1.id,
                                                    rm1.__dict__))
        print("rules -> {}, {}".format(rm0.__dict__, rm1.__dict__))

        #device rule
        for rule1 in rm0.__dict__:
            print(rm0.__dict__[rule1])
            for info in rm0.__dict__[rule1]:
                print("info -> {}".format(info))
                Statsct.set_device_rule(info)
        #input('')
        #gw rule
        for rule1 in rm1.__dict__:
            print(rm1.__dict__[rule1])
            for info in rm1.__dict__[rule1]:
                print("info -> {}".format(info))
                Statsct.set_gw_rule(info)

        #---------------------------------------------------------------------------
        Statsct.setSourceAddress(node0.id)
        Statsct.setDestinationAddress(node1.id)
        #---------------------------------------------------------------------------
        
        if test_file:
            file = open(fileToSend, 'r')
            print('file: ', file)
            payload = file.read().encode()
            print("Payload")
            print("{}".format(payload))
            #payload = ipv_header.replace(" ","/x").encode() + payload
            print("Payload size:", len(payload))
            print("Payload: {}".format(b2hex(payload)))
            print("")
        else:
            payload = bytearray(range(1, 1+send_data))
        node0.protocol.layer3.send_later(1, node1.layer3.L3addr, payload)
        #---------------------------------------------------------------------------    
        Statsct.addInfo('real_packet', payload)
        Statsct.addInfo('real_packet_size', len(payload))
        #---------------------------------------------------------------------------
        #try:
        sim.run()
        #except Exception as e:
        #    print("Exception: -> {}".format(e))
        #    input('Enter to continue')

        print('simulation ended')
        #Statsct.print_results()
        print('Sender Packet list ')
        Statsct.print_packet_list(Statsct.sender_packets)

        print('Receiver Packet list ')
        Statsct.print_packet_list(Statsct.receiver_packets)

        print("Results")
        Statsct.print_ordered_packets()
        #print(Statsct.get_results())
        print('performance metrics')
        sim_results.append(Statsct.calculate_tx_parameters())
        #print("{}".format(sim_results))

        input('Continue to next sim')
    #--------------------------------------------------
    
    
    average_goodput = 0
    average_total_delay = 0
    average_channe_occupancy = 0
    reliability = 0
    number_success_packets = 0
    number_failed_packets = 0
    number_success_fragments = 0
    number_failed_fragments = 0
    channel_occupancy_sender = 0
    channel_occupancy_receiver = 0
    total_data_send = 0
    for result in sim_results:
        print("{}".format(result))
        #average_goodput += result['goodput']
        total_data_send += result['total_data_send']
        average_total_delay += result['total_delay']
        average_channe_occupancy += result['channel_occupancy']
        number_success_fragments += result['succ_fragments']
        number_failed_fragments += result['fail_fragments']
        channel_occupancy_sender += result['channel_occupancy_sender']
        channel_occupancy_receiver += result['channel_occupancy_receiver']
        if result['packet_status']:
            number_success_packets += 1
        else:
            number_failed_packets += 1
    #average_goodput = average_goodput / len(sim_results)
    #average_channe_occupancy = average_channe_occupancy / len(sim_results)
    #average_total_delay = average_total_delay / len(sim_results)
    reliability = number_success_packets / (number_success_packets + number_failed_packets)
    ratio = number_success_fragments / (number_success_fragments + number_failed_fragments)
    print("{}".format(len(payload)))
    average_goodput = packet_size / total_data_send
    print("goodput:{}, total delay: {}, channel Occupancy: {}, reliability: {}, ratio (FER): {} total_data_send:{}".format(
        average_goodput,
        average_total_delay, average_channe_occupancy, reliability, ratio*100, total_data_send))
    total_results[packet_size] = {'goodput':average_goodput, 'total_delay': average_total_delay,
                                 'channel_occupancy':average_channe_occupancy, 
                                 'reliability': reliability, 'ratio': ratio*100,
                                 'channel_occupancy_sender':channel_occupancy_sender,
                                 'channel_occupancy_receiver':channel_occupancy_receiver}
    sim_results = []
    #input("")
#print("{}".format(total_results))
print("goodput")
print("\\addplot coordinates {")
for packet_size in total_results:
    #print("{}:".format(packet_size))
    if 'goodput' in total_results[packet_size]:
        print("({},{})".format(int(packet_size), (100*total_results[packet_size]['goodput'])))
print("}; \\addlegendentry{method=ack-on-error - S}")

print("total_delay")
print("\\addplot coordinates {")
for packet_size in total_results:
    #print("{}:".format(packet_size))
    if 'total_delay' in total_results[packet_size]:
        print("({},{})".format(int(packet_size), total_results[packet_size]['total_delay']))
print("}; \\addlegendentry{method=ack-on-error - S}")

print("channel_occupancy")
print("\\addplot coordinates {")
for packet_size in total_results:
    #print("{}:".format(packet_size))
    if 'channel_occupancy' in total_results[packet_size]:
        print("({},{})".format(int(packet_size), total_results[packet_size]['channel_occupancy']))
print("}; \\addlegendentry{method=ack-on-error - S}")

print("channel_occupancy_sender")
print("\\addplot coordinates {")
for packet_size in total_results:
    #print("{}:".format(packet_size))
    if 'channel_occupancy_sender' in total_results[packet_size]:
        print("({},{})".format(int(packet_size), total_results[packet_size]['channel_occupancy_sender']))
print("}; \\addlegendentry{method=ack-on-error - S}")

print("channel_occupancy_receiver")
print("\\addplot coordinates {")
for packet_size in total_results:
    #print("{}:".format(packet_size))
    if 'channel_occupancy_receiver' in total_results[packet_size]:
        print("({},{})".format(int(packet_size), total_results[packet_size]['channel_occupancy_receiver']))
print("}; \\addlegendentry{method=ack-on-error - S}")




print("reliability")
print("\\addplot coordinates {")
for packet_size in total_results:
    #print("{}:".format(packet_size))
    if 'reliability' in total_results[packet_size]:
        print("({},{})".format(int(packet_size), total_results[packet_size]['reliability']))
print("}; \\addlegendentry{method=ack-on-error - S}")

print("ratio")
print("\\addplot coordinates {")
for packet_size in total_results:
    #print("{}:".format(packet_size))
    if 'ratio' in total_results[packet_size]:
        print("({},{})".format(int(packet_size), total_results[packet_size]['ratio']))
print("}; \\addlegendentry{method=ack-on-error - S}")

# sim = net_sim_core.Simul(simul_config)
# devaddr = b"\xaa\xbb\xcc\xdd"
# node0 = make_node(sim, rm0, devaddr)    # SCHC device
# node1 = make_node(sim, rm1, devaddr)    # SCHC gw
# sim.add_sym_link(node0, node1)
# node0.layer2.set_mtu(l2_mtu)
# node1.layer2.set_mtu(l2_mtu)

# print("SCHC device L3={} L2={} RM={}".format(node0.layer3.L3addr, node0.id,
#                                              rm0.__dict__))
# print("SCHC gw     L3={} L2={} RM={}".format(node1.layer3.L3addr, node1.id,
#                                              rm1.__dict__))

# #--------------------------------------------------

# payload = bytearray(range(1, 1+data_size))
# node0.protocol.layer3.send_later(1, node1.layer3.L3addr, payload)


# sim.run()
#---------------------------------------------------------------------------
