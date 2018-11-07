# C.A. 2018

from base_import import *

#---------------------------------------------------------------------------

Rule = namedtuple("Rule", "rule_id_size rule_id dtag_size window_size"
                  + " fcn_size mode tile_size mic_algorithm")

def rule_from_dict(rule_as_dict):
    rule_as_dict = { k.replace("-","_"): v for k,v in rule_as_dict.items() }
    return Rule(**rule_as_dict)

#---------------------------------------------------------------------------

FAKE_RULE_ID = 0

class FakeRuleManager:
    def __init__(self):
        pass

    def set_frag_rule(self, rule):
        self.rule = rule

    def find_frag_rule(self, schc_packet_bitbuffer, meta_info):
        #schc_packet_bitbuffer.set
        frag_meta_info = {}
        return FAKE_RULE_ID, self.rule, frag_meta_info

    def get_frag_rule_by_id(self, rule_id):
        if rule_id != FAKE_RULE_ID:
            raise ValueError("rule_id", rule_id)
        meta_info = {}
        return self.rule, meta_info


#---------------------------------------------------------------------------
