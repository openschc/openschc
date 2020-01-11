THIS.CODE.IS.UNDER.CONSTRUCTION

import tcp_helper as helper
import gen_rulemanager
#import protocol

helper_config = {
    "mode": "client",
    "address": None, # or IPv4/IPv6 address
    "port": None, # TCP port,
    "compression": False,
    "fragmentation": False
}

rule_manager = XXX
rule_manager.Add({ rule_set })

helper  = helper.helper(helper_config)
#tcp_layer2 = helper.create_tcp_connector()
#tcp_layer3 = helper.create_tcp_layer3() # Layer3 special 
schc_protocol = helper.create_schc_protocol(rule_manager, tcp_layer2, tcp_layer3) # scheduler object also created here
tcp_layer3.send_at(10.0, b"0" * 100)

helper  = helper.helper(helper_config)
schc_protocol = helper.create_schc_protocol(rule_manager) # scheduler object also created here
tcp_layer3 = helper.get_layer3()
tcp_layer3 = send_at(10.0, b"00000")

scheduler = helper.get_scheduler()
scheduler.run()

#---------------------------------------------------------

XXX

class MyUpperLayer3(helper.TcpUpperLayer3):
    def __init__(self, XXX, scheduler):
        self.scheduler -= scheduler
    
    def receive(self, packet, meta):
        print(packet, meta)
        

#helper.set_tcp_layer3_factory(MyLayer3)

my_upper_layer3 = MyLayer3(XXX)
helper.set_upper_layer3(my_upper_layer3)
XXX

