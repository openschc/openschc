from enum import Enum, unique, auto

DEFAULT_FRAGMENT_RID = 1
DEFAULT_L2_SIZE = 6
DEFAULT_RECV_BUFSIZE = 512
DEFAULT_RECV_TIMEOUT = 6
DEFAULT_RECV_TIMEOUT_SENDER = 3

@unique
class SCHC_MODE(Enum):
    NO_ACK = auto()
    ACK_ALWAYS = auto()
    ACK_ON_ERROR = auto()
