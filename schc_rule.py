
from schc_param import *
import mic_crc32

'''
NOTE:
    rule_id and the length of the field must be negotiated
    between the nodes in out-of-band before they start communication.

- both size of win and bitmap must be 0 in NO_ACK mode
'''

r01 = {
    "rid": 1,
    "mode": SCHC_MODE_NO_ACK,
    "dtag_size": 3,
    "fcn_size": 1,
    "mic_func": mic_crc32,
    }

r02 = {
    "rid": 2,
    "mode": SCHC_MODE_WIN_ACK_ALWAYS,
    "dtag_size": 3,
    "fcn_size": 3,
    "mic_func": mic_crc32,
    }

r03 = {
    "rid": 3,
    "mode": SCHC_MODE_WIN_ACK_ON_ERROR,
    "dtag_size": 3,
    "fcn_size": 3,
    "mic_func": mic_crc32,
    }

rules = [ r01, r02, r03 ]

class schc_rule:

    def __init__(self, C, rid):
        '''
        C: context instance
        rid: rule id
        '''
        # XXX need to be better to get a rule.
        # XXX schc_rule instance is more likey to keep the static information.
        self.C = C
        self.R = None
        for i in rules:
            if i["rid"] == rid:
                self.R = i
        if self.R == None:
            raise ValueError("ERROR: invalid rid=%d" % rid)
        #
        self.rid = self.R["rid"]
        self.mode = self.R["mode"]
        self.dtag_size = self.R["dtag_size"]
        self.win_size = 0 if self.mode == SCHC_MODE_NO_ACK else 1
        self.fcn_size = self.R["fcn_size"]
        self.max_fcn = (2**self.fcn_size) - 2
        self.fcn_all_1 = (2**self.fcn_size) - 1 # same to bitmap_size
        self.fcn_all_0 = 0
        self.bitmap_size = (2**self.fcn_size) - 1
        self.bitmap_all_1 = (2**self.bitmap_size)-1
        self.cbit_size = 0 if self.mode == SCHC_MODE_NO_ACK else 1
        # set the mic function and the size.
        self.mic_func = self.R["mic_func"]
        dummy, self.mic_size = self.mic_func.get_mic(b"dummy")
        #
        # sanity check the base values
        if rid > (2**self.C.rid_size)-1:
            raise ValueError("rule_id is too big than the field size.")
        if self.fcn_size == 0:
            raise ValueError("fcn_size must be more than 0, but %d" %
                             self.fcn_size)
        if self.mode == SCHC_MODE_NO_ACK:
            if self.fcn_size != 1:
                raise ValueError("fcn_size in NO-ACK mode must be 1, but %d" %
                                 self.fcn_size)
