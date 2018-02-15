
from schc_param import *
import mic_crc32

'''
NOTE:
    rule_id and the length of the field must be negotiated
    between the nodes in out-of-band before they start communication.

- both size of win and bitmap must be 0 in NO_ACK mode
'''

fr01 = {
    "rid": 1,
    "type": "fragment",
    "mode": "no-ack",
    "dtag_size": 3,
    "fcn_size": 1,
    "mic_func": "crc32",
    }

fr02 = {
    "rid": 2,
    "type": "fragment",
    "mode": "ack-always",
    "dtag_size": 3,
    "fcn_size": 3,
    "mic_func": "crc32",
    }

fr03 = {
    "rid": 3,
    "type": "fragment",
    "mode": "ack-on-error",
    "dtag_size": 3,
    "fcn_size": 3,
    "mic_func": "crc32",
    }

global_rules = [ fr01, fr02, fr03 ]

class schc_rule:

    def __init__(self, C, rid):
        '''
        C: context instance
        rid: rule id
        '''
        # XXX need to be better to get a rule.
        # XXX schc_rule instance is more likey to keep the static information.
        self.C = C
        self.__set_R(rid)
        self.rid = self.R["rid"]
        self.__set_mode()
        self.dtag_size = self.R["dtag_size"]
        self.win_size = 0 if self.mode == SCHC_MODE.NO_ACK else 1
        self.fcn_size = self.R["fcn_size"]
        self.max_fcn = (2**self.fcn_size) - 2
        self.fcn_all_1 = (2**self.fcn_size) - 1 # same to bitmap_size
        self.fcn_all_0 = 0
        self.bitmap_size = (2**self.fcn_size) - 1
        self.bitmap_all_1 = (2**self.bitmap_size)-1
        self.cbit_size = 0 if self.mode == SCHC_MODE.NO_ACK else 1
        self.__set_mic_func()
        #
        # sanity check the base values
        if rid > (2**self.C.rid_size)-1:
            raise ValueError("rule_id is too big than the field size.")
        if self.fcn_size == 0:
            raise ValueError("fcn_size must be more than 0, but %d" %
                             self.fcn_size)
        if self.mode == SCHC_MODE.NO_ACK:
            if self.fcn_size != 1:
                raise ValueError("fcn_size in NO-ACK mode must be 1, but %d" %
                                 self.fcn_size)

    def __set_R(self, rid):
        self.R = None
        for i in global_rules:
            if i["rid"] == rid:
                self.R = i
                return
        #
        raise ValueError("ERROR: unknown rid=%d" % rid)

    def __set_mode(self):
        if self.R["mode"] == "no-ack":
            self.mode = SCHC_MODE.NO_ACK
        elif self.R["mode"] == "ack-always":
            self.mode = SCHC_MODE.WIN_ACK_ALWAYS
        elif self.R["mode"] == "ack-on-error":
            self.mode = SCHC_MODE.WIN_ACK_ON_ERROR
        else:
            raise ValueError("invalid mode=%s" % self.R["mode"])

    def __set_mic_func(self):
        if self.R["mic_func"] == "crc32":
            self.mic_func = mic_crc32
        else:
            raise ValueError("invalid mic func=%s" % self.R["mic_func"])
        # set the mic size.
        dummy, self.mic_size = self.mic_func.get_mic(b"dummy")
