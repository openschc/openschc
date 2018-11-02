try:
    from dissector_icmpv6 import dissect_icmpv6
    from dissector_udp import dissect_udp
except:
    from .dissector_icmpv6 import dissect_icmpv6
    from .dissector_udp import dissect_udp

dissectors_L4 = {
    17: dissect_udp,
    58: dissect_icmpv6,
}
