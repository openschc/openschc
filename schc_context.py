
import mic_crc32

# rule is defined at the other place.
c01 = {
    "cid": 0,
    "rid_size": 3,
    "default_rid": 1,
    "default_dtag": 1,
    "mic_func": mic_crc32,
}

contexts = [ c01 ]

class schc_context:

    def __init__(self, cid):
        '''
        cid: context id
        '''
        self.C = None
        for i in contexts:
            if i["cid"] == cid:
                self.C = i
        if self.C == None:
            raise ValueError("ERROR: invalid cid=%d" % cid)
        #
        self.cid = self.C["cid"]
        self.rid_size = self.C["rid_size"]
        self.default_dtag = self.C["default_dtag"]
        self.mic_func = self.C["mic_func"]
