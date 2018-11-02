try:
    from dissector_ipv6 import dissect_ipv6
    from dissector_ipv4 import dissect_ipv4
except:
    from .dissector_ipv6 import dissect_ipv6
    from .dissector_ipv4 import dissect_ipv4

dissectors_L3 = {
    4: dissect_ipv4,
    6: dissect_ipv6,
    }
