try: import json
except: import ujson as json
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
        self.mic_size = self.mic_func.get_mic_size()

class schc_ruledb:
    '''
    cid should not be assumed as an integer.
    e.g.
        self.ruledb = {
            <cid>: {
                "CID": <cid>,
                <rid>: {
                    "RID": <rid>,
                    ...
                    }
                }
                ...
            }
            ...
        }
    '''

    def is_int(self, x, tag):
        self.is_defined(x, tag)
        if not isinstance(x[tag], int):
            raise ValueError("ERROR: %s %s is not an integer." % (tag, x[tag]))

    def is_defined(self, x, tag):
        if tag not in x:
            raise ValueError("ERROR: %s is not defined." % tag)

    def get_runtime_context(self, cid):
        return schc_runtime_context(self.get_context(cid))

    def get_context(self, cid):
        return self.ruledb.get(cid)

    def load_context_json_str(self, json_str):
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
        j = json.loads(json_str)
        self.is_defined(j, TAG_CONTEXT)
        #
        context = j[TAG_CONTEXT]
        self.is_defined(context, TAG_CID)
        self.is_int(context, TAG_CID)
        self.is_defined(context, TAG_MIC_FUNC)
        if TAG_RID_SIZE in context:
            self.is_int(context, TAG_RID_SIZE)
        else:
            self.is_int(context, TAG_DEFAULT_RID)
        #
        # canonicalize
        context[TAG_MIC_FUNC] = context[TAG_MIC_FUNC].upper()
        #
        cid = context[TAG_CID]
        if self.get_context(cid):
            raise ValueError("ERROR: %s %d has already existed." % (TAG_CONTEXT,
                                                                    cid))
        #
        self.ruledb[cid] = context
        return cid

    def load_context_json_file(self, json_file):
        return self.load_context_json_str(open(json_file).read())
    
    def get_rule(self, cid, rid):
        return self.get_context(cid).get(rid)

    def add_rule(self, cid, rid, rule):
        if self.get_rule(cid, rid, rule):
            raise ValueError("ERROR: %s %d has already existed." % (TAG_RID,
                                                                    rid))
        self.update_rule(cid, rid, rule)

    def update_rule(self, cid, rid, rule):
        self.get_context(cid)[rid] = rule

    def delete_rule(self, cid, rid):
        del(self.ruledb[cid][rid])

    def load_json_file(self, cid, json_file):
        '''
        wrapper of load_json_file_one().
        json_file is either a string of the file name or a list
        of the file names.
        '''
        if isinstance(json_file, str):
            return self.load_json_file_one(cid, json_file)
        if isinstance(json_file, list):
            ret = []
            for i in json_file:
                ret.append(self.load_json_file_one(cid, i))
            return ret
        else:
            raise ValueError("ERROR: json_file is a string or list.")

    def load_json_str(self, cid, json_str):
        '''
        wrapper of load_json_file_one().
        json_file is either a string of the file name or a list
        of the file names.
        '''
        if isinstance(json_str, str):
            return self.load_json_str_one(cid, json_str)
        if isinstance(json_str, list):
            ret = []
            for i in json_str:
                ret.append(self.load_json_str_one(cid, i))
            return ret
        else:
            raise ValueError("ERROR: json_file is a string or list.")
        
    def load_json_file_one(self, cid, json_file):
        '''
        template
        '''
        pass

    def pprint(self, cid=None, rid=None, indent=4):
        if cid != None and rid != None:
            print(json.dumps(self.get_rule(cid, rid), indent=indent))
        elif cid != None and rid == None:
            print(json.dumps(self.get_context(cid), indent=indent))
        elif cid == None and rid == None:
            print(json.dumps(self.ruledb, indent=indent))
        else:
            ValueError("cid is not specified.")

