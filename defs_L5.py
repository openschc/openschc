try:
    from dissector_coap import dissect_coap
except:
    from .dissector_coap import dissect_coap

dissectors_L5 = {
    5683: dissect_coap,
}

