import pytest

#from src import frag_send

#import fixtures.fragmentation_rulefile as frf
#import fixtures.fragmentation_generic as fg# The code to test

def test_noack_fragmentation():
    import sys
    sys.path.append('../src')
    from frag_send import FragmentAckOnError
    file = FragmentAckOnError(rule, 12, None, None, None)
    pass
    #frf.generateFile()
    #frf.generateFile(frMode="ACKONERROR")

def test_ackonerr_fragmentation():
    #import sys
    #sys.path.append('../src/..')
    pass
    #frf.generateFile()
    #frf.generateFile(frMode="ACKONERROR")
    
#def test_frag_noack():
 #   FNA=FS.FragmentNoAck()
 #   print (str(FNA))
 #   assert 1 
    #frf.generateFile()
    #frf.generateFile(frMode="ACKONERROR")
    
#@pytest.mark.usefixtures("generateFile") 
#def test_frag():
#    stdout = fg.frag_generic(frf.generateFile(),packet_loss=False)
#    assert "msg_type_queue -> ['SCHC_ACK_OK']" in stdout
#    assert "----------------------- ACK Success" in stdout