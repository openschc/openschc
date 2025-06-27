#---------------------------------------------------------------------------

# Template for schc simulation
import argparse

from gen_base_import import *  # used for now for differing modules in py/upy

import protocol
import net_sim_sched
import net_sim_layer2
import net_sim_core
from gen_rulemanager import RuleManager

from stats.statsct import Statsct

if sys.implementation.name == "micropython":
    ap = argparse.ArgumentParser(description="a SCHC simulator.")
else:
    ap = argparse.ArgumentParser(description="a SCHC simulator.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

ap.add_argument("--context", action="store", dest="context_file",
                default="example/context-100.json",
                help="specify a file name containing a context in JSON.")
ap.add_argument("--rule-comp", action="store", dest="rule_comp_file",
                default="example/comp-rule-100.json",
                help="specify a file name containing a compression rule in JSON.")
ap.add_argument("--rule-fragin", action="store", dest="rule_fragin_file",
                default="example/frag-rule-201.json",
                help="specify a file name containing an inbound fragment rule in JSON.")
ap.add_argument("--rule-fragout", action="store", dest="rule_fragout_file",
                default="example/frag-rule-202.json",
                help="specify a file name containing a outbound fragment rule in JSON.")
ap.add_argument("--loss-mode", action="store", dest="loss_mode", default=None,
                choices=["cycle", "list", "rate"],
                help="specify the mode of loss.")
ap.add_argument("--loss-param", action="store", dest="loss_param", default=None,
                help="specify the parameter for the mode of loss.")
ap.add_argument("--data-file", action="store", dest="data_file", default=None,
                help="specify the file name containing the data to be sent.")
ap.add_argument("--data-size", action="store", dest="data_size", type=int, default=14,
                help="specify the size of data, used if --data-file is not specified.")
ap.add_argument("--l2-mtu", action="store", dest="l2_mtu", type=int, default=56,
                help="specify the size of L2 MTU.")
opt = ap.parse_args()

loss_config = None
if opt.loss_mode in ["cycle","list","rate"]:
    if opt.loss_param is None:
        raise ValueError(
                "--loss-param is required if --loss-mode is specified.")
    if opt.loss_mode == "cycle":
        loss_config = {"mode":"cycle", "cycle":int(opt.loss_param)}
    elif opt.loss_mode == "list":
        loss_config = {"mode":"list",
                       "count_num":[int(_) for _ in opt.loss_param.split(",")]}
    elif opt.loss_mode == "rate":
        loss_config = {"mode":"rate", "cycle":int(opt.loss_param)}
elif opt.loss_mode is not None:
    raise ValueError("--loss-mode must be either 'cycle', 'list', or 'rate'")

#---------------------------------------------------------------------------

def make_node(sim, rule_manager, devaddr, extra_config={}):
    node = net_sim_core.SimulSCHCNode(sim, extra_config)
    node.protocol.set_rulemanager(rule_manager)
    node.layer2.set_devaddr(devaddr)
    return node

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
""" Init stastct module """
Statsct.initialize()
Statsct.log("Statsct test")
#---------------------------------------------------------------------------



rule = []
for k in [opt.context_file, opt.rule_comp_file, opt.rule_fragin_file,
          opt.rule_fragout_file]:
    with open(k) as fd:
        rule.append(json.loads(fd.read()))

rm0 = RuleManager()
rm0.add_context(rule[0], rule[1], rule[2], rule[3])

rm1 = RuleManager()
rm1.add_context(rule[0], rule[1], rule[3], rule[2])

simul_config = {
    "log": True,
}
if loss_config is not None:
    simul_config["loss"] = loss_config
sim = net_sim_core.Simul(simul_config)

devaddr = b"\xaa\xbb\xcc\xdd"
node0 = make_node(sim, rm0, devaddr)    # SCHC device
node1 = make_node(sim, rm1, devaddr)    # SCHC gw
sim.add_sym_link(node0, node1)
node0.layer2.set_mtu(opt.l2_mtu)
node1.layer2.set_mtu(opt.l2_mtu)

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
        for tag in info:
            print(tag)
            print(info[tag])
            if tag == "fragSender":
                print('fragSender rule -> {}'.format(info[tag]))
            elif tag == "fragReceiver": 
                print('fragReceiver rule -> {}'.format(info[tag]))
input('')
#gw rule
for rule1 in rm1.__dict__:
    print(rm1.__dict__[rule1])
    for info in rm1.__dict__[rule1]:
        print("info -> {}".format(info))
        Statsct.set_gw_rule(info)
        for tag in info:
            print(tag)
            print(info[tag])
            if tag == "fragSender":
                print('fragSender rule -> {}'.format(info[tag]))
            elif tag == "fragReceiver": 
                print('fragReceiver rule -> {}'.format(info[tag]))
input('')
 
#---------------------------------------------------------------------------
Statsct.setSourceAddress(node0.id)
Statsct.setDestinationAddress(node1.id)
 
#---------------------------------------------------------------------------
 
#---------------------------------------------------------------------------
 
if opt.data_file is not None:
    payload = open(opt.data_file,"rb").read()
else:
    payload = bytearray(range(1, 1+int(opt.data_size)))
 
#---------------------------------------------------------------------------    
Statsct.addInfo('real_packet', payload)
Statsct.addInfo('real_packet_size', len(payload))
#---------------------------------------------------------------------------
 
 
node0.protocol.layer3.send_later(1, node1.layer3.L3addr, payload)
 
sim.run()
print('simulation ended')
Statsct.print_results()
print('Sender Packet list -> {}'.format(Statsct.sender_packets))
Statsct.print_packet_list(Statsct.sender_packets)
 
#---------------------------------------------------------------------------
 
