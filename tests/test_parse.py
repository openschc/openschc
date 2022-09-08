import pytest
import pcapng

import sys
sys.path.insert(0, "src/")

def test_import():
    import compr_parser

def test_parse():
    import compr_parser
    
    parser = compr_parser.Parser(None)
    
    frames = []
    with open('tests/coap.pcapng', 'rb') as fp:
        pcapngScanner = pcapng.FileScanner(fp)
        for block in pcapngScanner:
            if type(block)==pcapng.blocks.EnhancedPacket:
                 frames += [block.packet_data]
    
    for frame in frames:
        parser.parse(
            pkt       = frame,
            direction = 'UP',
        )