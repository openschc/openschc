import json
from schc_ruledb_tag import *
import mic_crc32

class schc_runtime_context:

    def __init__(self, c):
        '''
        C: a dict-like context.
        '''
        self.cid = c[TAG_CID]
        self.rid_size = c[TAG_RID_SIZE]
        self.default_dtag = c[TAG_DEFAULT_RID]
        self.__set_mic_func(c[TAG_MIC_FUNC])

    def __set_mic_func(self, mic_func_name):
        if mic_func_name == "CRC32":
            self.mic_func = mic_crc32
        else:
            raise ValueError("invalid mic func=%s" % mic_func_name)
        # set the mic size.
        dummy, self.mic_size = self.mic_func.get_mic(b"dummy")

class schc_ruledb:
    '''
    self.ruledb = {
        <cid>: {
            "CID": <cid>,
            "FRAG_RULE": {
                <rid>: {
                    "RID": <rid>,
                    ...
                }
                ...
            }
        }
    '''

    def is_int(self, x, tag):
        self.is_defined(x, tag)
        if not isinstance(x[tag], int):
            raise ValueError("ERROR: %s %s is not an integer." % (tag, x[tag]))

    def is_defined(self, x, tag):
        if tag not in x:
            raise ValueError("ERROR: %s is not defined." % tag)

    def load_context_json_file(self, json_file):
        '''
        e.g.
            {
                "CONTEXT": {
                    "CID": 1,
                    "RID_SIZE": 3,
                    "DEFAULT_RID": 1,
                    "MIC_FUNC": "CRC32"
                }
            }
        '''
        j = json.load(open(json_file))
        self.is_defined(j, TAG_CONTEXT)
        #
        x = j[TAG_CONTEXT]
        self.is_defined(x, TAG_CID)
        self.is_int(x, TAG_CID)
        self.is_defined(x, TAG_MIC_FUNC)
        if TAG_RID_SIZE in x:
            self.is_int(x, TAG_RID_SIZE)
        else:
            self.is_int(x, TAG_DEFAULT_RID)
        #
        cid = x[TAG_CID]
        if self.get_context(cid):
            raise ValueError("ERROR: %s %d has already existed." % (TAG_CONTEXT,
                                                                    cid))
        #
        self.ruledb[cid] = x
        self.ruledb[cid][TAG_FRAG_RULE] = {}
        return cid

    def get_context(self, cid):
        return self.ruledb.get(cid)

    def get_runtime_context(self, cid):
        return schc_runtime_context(self.get_context(cid))

    def pprint(self, cid=None, indent=4):
        if cid == None:
            print(json.dumps(self.ruledb, indent=indent))
        else:
            print(json.dumps(self.get_context(cid), indent=indent))

