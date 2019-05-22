#---------------------------------------------------------------------------

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import RuleManager

#import statsct static class 
from stats.statsct import Statsct
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
        "FRMode": "ackOnError",
        "FRModeProfile": {
            "dtagSize": 2,
            "WSize": 5,
            "FCNSize": 3,
            "ackBehavior": "afterAll1",
            "tileSize": 9,
            "MICAlgorithm": "crc32",
            "MICWordSize": 8
        }
    }
}

frag_rule2 = {
    "ruleLength": 6,
    "ruleID": 2,
    "profile": { "L2WordSize": 8 },
    "fragmentation": {
        "FRMode": "ackOnError",
        "FRModeProfile": {
            "dtagSize": 2,
            "WSize": 5,
            "FCNSize": 3,
            "ackBehavior": "afterAll1",
            "tileSize": 9,
            "MICAlgorithm": "crc32",
            "MICWordSize": 8
        }
    }
}




#---------------------------------------------------------------------------

def make_node(sim, rule_manager, devaddr=None, extra_config={}):
    node = simul.SimulSCHCNode(sim, extra_config)
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
#L2 MTU size in bits

l2_mtu = 56
#Size of data in bytes
data_size = 14

l2_mtu = 408
#Size of data in bytes
data_size = 51

#---------------------------------------------------------------------------
#Configuration of simulator
#Number of repetitions
repetitions = 1
sim_results = []
#---------------------------------------------------------------------------
""" Init stastct module """
Statsct.initialize()
Statsct.log("Statsct test")
Statsct.set_packet_size(data_size)
#---------------------------------------------------------------------------

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


for i in range(repetitions):
    #---------------------------------------------------------------------------
    """ Init stastct module """
    Statsct.initialize()
    Statsct.log("Statsct test")
    Statsct.set_packet_size(data_size)
    #---------------------------------------------------------------------------
    Statsct.get_results()
    sim = simul.Simul(simul_config)
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

    payload = bytearray(range(1, 1+data_size))
    node0.protocol.layer3.send_later(1, node1.layer3.L3addr, payload)
    #---------------------------------------------------------------------------    
    Statsct.addInfo('real_packet', payload)
    Statsct.addInfo('real_packet_size', len(payload))
    #---------------------------------------------------------------------------
    sim.run()
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
    print("{}".format(sim_results))

    #input('Continue to next sim')
#--------------------------------------------------
average_goodput = 0
average_total_delay = 0
average_channe_occupancy = 0
reliability = 0
number_success_packets = 0
number_failed_packets = 0
number_success_fragments = 0
number_failed_fragments = 0
for result in sim_results:
    print("{}".format(result))
    average_goodput += result['goodput']
    average_total_delay += result['total_delay']
    average_channe_occupancy += result['channel_occupancy']
    number_success_fragments += result['succ_fragments']
    number_failed_fragments += result['fail_fragments']
    if result['packet_status']:
        number_success_packets += 1
    else:
        number_failed_packets += 1
average_goodput = average_goodput / len(sim_results)
average_channe_occupancy = average_channe_occupancy / len(sim_results)
average_total_delay = average_total_delay / len(sim_results)
reliability = number_success_packets / (number_success_packets + number_failed_packets)
ratio = number_success_fragments / (number_success_fragments + number_failed_fragments)

print("goodput:{}, total delay: {}, channel Occupancy: {}, reliability: {}, ratio (FER): {}".format(average_goodput,
    average_total_delay, average_channe_occupancy, reliability, ratio))



# sim = simul.Simul(simul_config)
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
