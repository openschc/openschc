
from schc_param import *
try: import json
except: import ujson as json
from schc_ruledb_tag import *
from schc_ruledb import schc_ruledb

class schc_runtime_fragment_rule:

    def __init__(self, C, r):
        '''
        C: a runtime context.
        r: a dict-like fragment rule.
        '''
        self.C = C
        self.rid = r[TAG_RID]
        self.__set_mode(r[TAG_MODE])
        self.dtag_size = r[TAG_DTAG_SIZE]
        self.win_size = 0 if self.mode == SCHC_MODE.NO_ACK else 1
        self.fcn_size = r[TAG_FCN_SIZE]
        self.max_fcn = (2**self.fcn_size) - 2
        self.fcn_all_1 = (2**self.fcn_size) - 1 # same to bitmap_size
        self.fcn_all_0 = 0
        self.bitmap_size = (2**self.fcn_size) - 1
        self.bitmap_all_1 = (2**self.bitmap_size)-1
        self.cbit_size = 0 if self.mode == SCHC_MODE.NO_ACK else 1
        #
        # sanity check the base values
        if self.rid > (2**self.C.rid_size)-1:
            raise ValueError("rule_id is bigger than the field size.")
        if self.fcn_size == 0:
            raise ValueError("fcn_size must be more than 0, but %d" %
                             self.fcn_size)
        if self.mode == SCHC_MODE.NO_ACK:
            if self.fcn_size != 1:
                raise ValueError("fcn_size in NO-ACK mode must be 1, but %d" %
                                 self.fcn_size)

    def __set_mode(self, mode):
        if mode == "NO-ACK":
            self.mode = SCHC_MODE.NO_ACK
        elif mode == "ACK-ALWAYS":
            self.mode = SCHC_MODE.ACK_ALWAYS
        elif mode == "ACK-ON-ERROR":
            self.mode = SCHC_MODE.ACK_ON_ERROR
        else:
            raise ValueError("invalid mode=%s" % mode)

class schc_fragment_ruledb(schc_ruledb):

    def __init__(self):
        self.ruledb = {}

    def get_runtime_rule(self, cid, rid):
        return schc_runtime_fragment_rule(self.get_runtime_context(cid),
                                  self.get_rule(cid, rid))

    def load_json_str_one(self, cid, json_str):
        '''
        e.g.
            {
                "FRAG_RULE": {
                    "RID": 3,
                    "MODE": "ACK-ON-ERROR",
                    "DTAG_SIZE": 3,
                    "FCN_SIZE": 3,
                    "DEFAULT_DTAG": 1
                }
            }
        '''
        j = json.loads(json_str)
        self.is_defined(j, TAG_FRAG_RULE)
        #
        rule = j[TAG_FRAG_RULE]
        self.is_int(rule, TAG_RID)
        self.is_defined(rule, TAG_MODE)
        self.is_int(rule, TAG_DTAG_SIZE)
        self.is_int(rule, TAG_DEFAULT_DTAG)
        self.is_int(rule, TAG_FCN_SIZE)
        #
        # canonicalize
        rule[TAG_MODE] = rule[TAG_MODE].upper()
        #
        self.update_rule(cid, rule[TAG_RID], rule)
        return rule[TAG_RID]

    def load_json_file_one(self, cid, json_file):
        return self.load_json_str_one(cid, open(json_file).read())
        
        
'''
test code
'''
if __name__ == "__main__":
    frdb = schc_fragment_ruledb()
    cid = frdb.load_context_json_file("example-rule/context-001.json")
    rid = frdb.load_json_file(cid, "example-rule/fragment-rule-001.json")
    #frdb.load_json_file(cid, ["example-rule/fragment-rule-002.json",
    #                          "example-rule/fragment-rule-003.json"])
    print("## pprint()")
    frdb.pprint()
    print("## get_context(%s)" % str(cid))
    print(frdb.get_context(cid))
    print("## get_rule(%s, %s)" % (str(cid), str(rid)))
    print(frdb.get_rule(cid, rid))
    print("## pprint(cid=%s, rid=%s)" % (str(cid), str(rid)))
    frdb.pprint(cid=cid, rid=rid)
    #
    frdb.get_runtime_context(cid)
    rrf = frdb.get_runtime_rule(cid, rid)
    print(rrf)
    print(rrf.C)

