#---------------------------------------------------------------------------

# Template for schc simulation
import sys
import argparse

from base_import import *  # used for now for differing modules in py/upy

import schc
import simsched
import simlayer2
import simul
from rulemanager import RuleManager

ap = argparse.ArgumentParser(description="a SCHC simulator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("--rule-file", action="store", dest="rule_file",
                default="example/fragment-rule-001.json",
                help="specify a file name containing a rule in JSON.")
ap.add_argument("--loss-mode", action="store", dest="loss_mode", default=None,
                choices=["cycle", "list", "rate"],
                help="specify the mode of loss.")
ap.add_argument("--loss-param", action="store", dest="loss_param", default=None,
                help="specify the parameter for the mode of loss.")
ap.add_argument("--data-file", action="store", dest="data_file", default=None,
                help="specify the file name containing the data to be sent.")
#ap.add_argument("--l2-mtu", action="store", dest="l2_mtu", type=int, default=56,
#                help="specify the size of L2 MTU. default is 56.")
opt = ap.parse_args()

#config = "example/fragment-rule-001.json"
#config = "example/fragment-rule-002.json"

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

with open(opt.rule_file) as fd:
    rule = json.loads(fd.read())

rule_manager = RuleManager()
rule_manager.add(rule)

#---------------------------------------------------------------------------

def make_node(sim, rule_manager, extra_config={}):
    node = simul.SimulSCHCNode(sim, extra_config)
    node.protocol.set_rulemanager(rule_manager)
    return node

#---------------------------------------------------------------------------

simul_config = {
    "log": True,
}
if loss_config is not None:
    simul_config["loss"] = loss_config
sim = simul.Simul(simul_config)

node0 = make_node(sim, rule_manager)
node1 = make_node(sim, rule_manager)
sim.add_sym_link(node0, node1)

print("mac_id:", node0.id, node1.id)
if opt.data_file is None:
    payload = bytearray(range(1, 13+1))
else:
    payload = open(opt.data_file,"rb").read()
node0.protocol.layer3.send_later(1, node1.id, payload)

sim.run()

#---------------------------------------------------------------------------
