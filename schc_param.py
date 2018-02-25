from enum import Enum, unique, auto

DEFAULT_FRAGMENT_RID = 1
DEFAULT_L2_SIZE = 8
DEFAULT_RECV_BUFSIZE = 512
DEFAULT_TIMER_T1 = 6
DEFAULT_TIMER_T2 = 12
DEFAULT_TIMER_T3 = 6

@unique
class SCHC_MODE(Enum):
    NO_ACK = auto()
    ACK_ALWAYS = auto()
    ACK_ON_ERROR = auto()
