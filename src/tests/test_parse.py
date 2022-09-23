import pytest
import pcapng

ETHERNET_HEADER_LENGTH = 14

def test_import():
    import compr_parser

def test_parse():
    import compr_parser
    
    parser = compr_parser.Parser(None)
    
    packets = []
    with open('tests/coap.pcapng', 'rb') as fp:
        pcapngScanner = pcapng.FileScanner(fp)
        for block in pcapngScanner:
            if type(block)==pcapng.blocks.EnhancedPacket:
                 packets += [block.packet_data[ETHERNET_HEADER_LENGTH:]]
    
    for packet in packets:
        parsedFrame = parser.parse(
            pkt       = packet,
            direction = 'UP',
            layers    = ["IPv6", "ICMP", "UDP"]
        )
