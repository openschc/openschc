import io
import pytest
import sys
import tempfile

from gen_base_import import *  # used for now for differing modules in py/upy
import net_sim_core
from gen_rulemanager import *
from stats.statsct import Statsct
from compr_core import *
from compr_parser import *
from gen_utils import dprint, dpprint, set_debug_output
import cbor2 as cbor

set_debug_output(False)

#============================ fixtures ========================================

@pytest.fixture
def rule_no_ack():
    file_rules = tempfile.NamedTemporaryFile()
    file_rules.write("""
 {
    "DeviceID" : "lorawan:0000000000000001",
    "SoR" : [
	{
        "RuleID": 11,
	    "RuleIDLength": 6,
	    "NoCompression": []
    },
    {
      "RuleID":12,
      "RuleIDLength":6,
      "Fragmentation":{
         "FRMode":"NoAck",
         "FRDirection" : "DW"
        }
   }
   ]
}   
    """.encode("utf-8"))
    file_rules.seek(0)
    # Use yield instead of return so the temp file survives
    yield file_rules.name

@pytest.fixture
def rule_ack_on_error():
    file_rules = tempfile.NamedTemporaryFile()
    file_rules.write(
        
"""
 {
    "DeviceID" : "lorawan:0000000000000001",
    "SoR" : [
	{
        "RuleID": 11,
	    "RuleIDLength": 6,
	    "NoCompression": []
    },
    {
      "RuleID":12,
      "RuleIDLength":6,
      "Fragmentation": {
         "FRMode":"AckOnError",
         "FRDirection" : "DW",
         "FRModeProfile":{
            "dtagSize":2,
            "WSize":3,
            "FCNSize":3,
            "ackBehavior":"afterAll1",
            "tileSize":392,
            "MICAlgorithm":"RCS_RFC8724",
            "MICWordSize":8,
            "lastTileInAll1":false
        }
    }
    }
    ]
}

    """.encode("utf-8"))
    file_rules.seek(0)
    # Use yield instead of return so the temp file survives
    yield file_rules.name

#============================ helpers =========================================

def frag_generic(rules_filename, packet_loss):
    # --------------------------------------------------
    # General configuration

    l2_mtu = 72  # bits
    data_size = 14  # bytes
    SF = 7

    simul_config = {
        "log": True,
    }

    # ---------------------------------------------------------------------------
    # Configuration packets loss

    if packet_loss:
        # Configuration with packet loss in NoAck and ack-on-error
        loss_rate = 15  # in %
        collision_lambda = 0.1
        background_frag_size = 54
        loss_config = {"mode": "rate", "cycle": loss_rate}
        # loss_config = {"mode":"collision", "G":collision_lambda, "background_frag_size":background_frag_size}
    else:
        # Configuration without packet loss in NoAck and ack-on-error
        loss_rate = None
        loss_config = None

    # ---------------------------------------------------------------------------
    # Init packet loss
    if loss_config is not None:
        simul_config["loss"] = loss_config

    # ---------------------------------------------------------------------------

    def make_node(sim, rule_manager, device_id=None, core_id=None, extra_config={}, role=None):
        extra_config["unique-peer"] = False # What is unique-peer ??
        node_id = device_id
        if role == "core":
            node_id = core_id
        node = net_sim_core.SimulSCHCNode(sim, extra_config, node_id, role)
        node.protocol.set_rulemanager(rule_manager)
        node.layer2.set_device_id(device_id)
        node.layer2.set_core_id(core_id)
        node.layer2.set_id(node_id)
        return node

    # ---------------------------------------------------------------------------
    # Statistic module
    Statsct.initialize()
    Statsct.log("Statsct test")
    Statsct.set_packet_size(data_size)
    Statsct.set_SF(SF)
    
    # ---------------------------------------------------------------------------
    
    #devaddr1 = b"\xaa\xbb\xcc\xdd"
    #devaddr2 = b"\xaa\xbb\xcc\xee"

    device_id = "lorawan:0000000000000001"
    core_id   = "lorawan:0000000000000002"

    print("---------Rules Device -----------")
    rm0 = RuleManager()
    # rm0.add_context(rule_context, compress_rule1, frag_rule3, frag_rule4)
    rm0.Add(device=device_id, file=rules_filename)
    rm0.Print()

    print("---------Rules gw -----------")
    rm1 = RuleManager()
    # rm1.add_context(rule_context, compress_rule1, frag_rule4, frag_rule3)
    rm1.Add(device=device_id, file=rules_filename)
    rm1.Print()

    # ---------------------------------------------------------------------------
    # Configuration of the simulation
    Statsct.get_results()
    sim = net_sim_core.Simul(simul_config)

    device = make_node(sim, rm0, device_id = device_id, core_id = core_id, role=T_POSITION_DEVICE)  # SCHC device
    core = make_node(sim, rm1, device_id = device_id, core_id= core_id, role=T_POSITION_CORE)  # SCHC gw
    sim.add_sym_link(device, core)

    device.layer2.set_mtu(l2_mtu)   
    core.layer2.set_mtu(l2_mtu)

    # ---------------------------------------------------------------------------
    # Information about the devices

    print("-------------------------------- SCHC device------------------------")
    print("SCHC device L2={} RM={}".format(device.id, rm0.__dict__))
    print("-------------------------------- SCHC gw ---------------------------")
    print("SCHC gw     L2={} RM={}".format(device.id, rm1.__dict__))
    print("-------------------------------- Rules -----------------------------")
    print("rules -> {}, {}".format(rm0.__dict__, rm1.__dict__))
    print("")

    # ---------------------------------------------------------------------------
    # Statistic configuration

    Statsct.setSourceAddress(core.id)
    Statsct.setDestinationAddress(device.id)

    # --------------------------------------------------
    # Message

    coap = bytearray(
            b"`\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00" +
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" +
            b"\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00" +
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16" +
            b"2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3" +
            b"foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01" +
            b"\x82  &Ehello Ehello Ehello Ehello Ehello Ehello EhelloEhelloEhelloEhelloEhelloEhelloEhelloEhelloEhello")

    icmp = b'`\x00\x00\x00\x00:\x11\xff\xfe\x80\x00\x00\x00\x00\x00\x00N\x82-\x97u\xb2d\x99\xfe\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\\@0p\x00:\x1fb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    # ---------------------------------------------------------------------------
    # Simulation

    clock = time.time()

    # Core starts to send coap packet

    core.send_later(core.protocol, clock, core_id, device_id, coap) 

    old_stdout = sys.stdout
    set_debug_output(True)
    sys.stdout = io.StringIO()
    sim.run()

    simulation_output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    set_debug_output(False)

    print(simulation_output)
    return simulation_output

#============================ tests ===========================================

@pytest.mark.skip(reason="no way of currently testing this") 
def test_frag_ack_on_error_no_loss(rule_ack_on_error):
    stdout = frag_generic(rule_ack_on_error, packet_loss=False)
    assert "msg_type_queue -> ['SCHC_ACK_OK']" in stdout
    assert "----------------------- ACK Success" in stdout

@pytest.mark.skip(reason="no way of currently testing this") 
def test_frag_ack_on_error_loss(rule_ack_on_error):
    stdout = frag_generic(rule_ack_on_error, packet_loss=True)
    assert "msg_type_queue -> ['SCHC_ACK_OK']" in stdout
    assert "----------------------- ACK Success" in stdout

@pytest.mark.skip(reason="no way of currently testing this") 
def test_frag_no_ack_no_loss(rule_no_ack):
    stdout = frag_generic(rule_no_ack, packet_loss=False)
    print(stdout)
    assert "SUCCESS: MIC matched" in stdout

@pytest.mark.skip(reason="no way of currently testing this") 
def test_frag_no_ack_loss(rule_no_ack):
    # packet loss in NoAck obviously will make an error.
    stdout = frag_generic(rule_no_ack, packet_loss=True)
    print ("++++", stdout)
    assert "ERROR: MIC mismatched" in stdout
