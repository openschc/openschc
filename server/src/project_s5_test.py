
from SCHC_server import SCHC_server

class Project_s5_test:
    def receive_message():
        fromGW = {
            "fPort": 2300,
            "devEUI": "70B3D54997463CB4",
        }
        
        schc = SCHC_server()
        schc.layer_2.setPort(fromGW["fPort"])
        schc.layer_2.setDevEUI(fromGW["devEUI"])
        #scheduler.run()
#------------------ACK on Error--------------------
        
        Fragment1 = b'\x09\x04\x01\x02\x03\x04\x05' 
        Fragment2 = b'\x09\x0c\x06\x07\x08\x09\x0a' 
        Fragment3 = b'\x09\x14\x0b\x0c\x0d\x0e\x0f'  
        Fragment4 = b'\x09\x1c\x10\x11\x12\x13\x14'  
        Fragment5 = b'\x09\x24\x15\x16\x17\x18\x19' 
        Fragment6 = b'\x09\x2c\x1a\x1b\x1c\x1d\x1e'  
        Fragment7 = b'\x09\x34\x1f\x20\x21\x22\x23'  
        Fragment8 = b'\x09\x3c\x24\x25\x26\x27\x28'  
        Fragment9 = b'\x09\x44\x29\x2a\x2b\x2c\x2d'  
        Fragment10 = b'\x09\x4c\x2e\x2f\x30\x31\x32'  
        Fragment11 = b'\x09\x54\x33\x34\x35\x36\x37' 
        Fragment12 = b'\x09\x5c\x38\x39\x3a\x3b\x3c'  
        Fragment13 = b'\x09\x64\x3d\x3e\x3f\x40\x41'  
        Fragment14 = b'\x09\x6c\x42\x43\x44\x45\x46'  
        Fragment15 = b'\x09\x74\x47\x48\x49\x4a\x4b' 
        Fragment16 = b'\x09\x7c\x4c\x4d\x4e\x4f\x50'  
        Fragment17 = b'\x09\x84\x51\x52\x53\x54\x54'  #55--->54 
        Fragment18 = b'\x09\x8c\x56\x57\x58\x59\x5a'  
        Fragment19 = b'\x09\x94\x5b\x5c\x5d\x5e\x5f'  
        Fragment20 = b'\x09\x9c\x60\x61\x62\x63\x64' 
        Fragment21 = b'\x09\x9f\x65\xf0\x0f\x42'

        Fragment22 = b'\x09\x9f\x65\xf0\x0f\x42'  #request ack
        Fragment23 = b'\x09\x9f\x65\xf0\x0f\x42'  #request ack
        Fragment24 = b'\x09\x9f'                  #abort message
        '''
#---------------------ACK ON ERROR loss paquet--------------
        Fragment1 = b'\x09\x04\x32\x30\x31\x38\x2d'
        Fragment2 = b'\x09\x0c\x31\x31\x2d\x32\x30'
        Fragment3 = b'\x09\x14\x20\x31\x31\x3a\x30'
        Fragment4 = b'\x09\x1c\x30\x3a\x31\x36\x20'
        Fragment5 = b'\x09\x24\x2d\x20\x64\x61\x65'
        Fragment6 = b'\x09\x2c\x6d\x6f\x6e\x2e\x70'
        Fragment7 = b'\x09\x34\x79\x20\x28\x31\x36'
        Fragment8 = b'\x09\x3c\x32\x29\x20\x2d\x20'
        Fragment9 = b'\x09\x44\x49\x4e\x46\x4f\x20'
        Fragment10 = b'\x09\x4c\x3a\x20\x53\x74\x6f'
        Fragment11 = b'\x09\x54\x70\x70\x69\x6e\x67'
        Fragment12 = b'\x09\x5c\x20\x64\x61\x65\x6d'
        Fragment13 = b'\x09\x64\x6f\x6e\x2e\x2e\x2e'
        Fragment14 = b'\x09\x6f\x59\x08\x89\x16\x0a'
        Fragment15 = b'\x09\x6f\x59\x08\x89\x16\x0a'
        '''

        '''
#-----------------------NO ACK-----------------------------------------
        Fragment1 = b'\x48\x01\x02\x03\x04\x05\x06'
        Fragment2 = b'\x48\x07\x08\x09\x0a\x0b\x0c'
        Fragment3 = b'\x48\x0d\x0e\x0f\x10\x11\x12'
        Fragment4 = b'\x48\x13\x14\x15\x16\x17\x18'
        Fragment5 = b'\x48\x19\x1a\x1b\x1c\x1d\x1e'
        Fragment6 = b'\x48\x1f\x20\x21\x22\x23\x24'
        Fragment7 = b'\x48\x25\x26\x27\x28\x29\x2a'
        Fragment8 = b'\x48\x2b\x2c\x2d\x2e\x2f\x30'
        Fragment9 = b'\x48\x31\x32\x33\x34\x35\x36'
        Fragment10 = b'\x48\x37\x38\x39\x3a\x3b\x3c'
        Fragment11 = b'\x48\x3d\x3e\x3f\x40\x41\x42'
        Fragment12 = b'\x48\x43\x44\x45\x46\x47\x48'
        Fragment13 = b'\x48\x49\x4a\x4b\x4c\x4d\x4e'
        Fragment14 = b'\x48\x4f\x50\x51\x52\x53\x54'
        Fragment15 = b'\x48\x55\x56\x57\x58\x59\x5a'
        Fragment16 = b'\x48\x5b\x5c\x5d\x5e\x5f\x60'
        Fragment17 = b'\x48\x61\x62\x63\x64'
        Fragment18 = b'\x4f\x65\xf0\x0f\x42'
        '''
        
#-------------------------------------NO ACK---------------------------
        '''
        answer = schc.reassemble(Fragment1)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment2)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment3)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment4)  
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment5)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment6) 
        print("respuesta ",answer)        
        answer =schc.reassemble(Fragment7)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment8)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment9)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment10)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment11)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment12)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment13)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment14)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment15)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment16)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment17)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment18)
        print("respuesta ",answer)
#------------------ACK ON EROR packet one losse------------------------
        '''
        answer = schc.reassemble(Fragment1)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment2)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment3)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment4)  
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment5)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment6) 
        print("respuesta ",answer)        
        answer =schc.reassemble(Fragment7)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment8)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment9)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment10)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment11)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment12)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment13)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment14)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment15)
        print("respuesta ",answer)
        
        answer =schc.reassemble(Fragment16)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment17)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment18)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment19)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment20)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment21)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment22)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment23)
        print("respuesta ",answer)
        answer =schc.reassemble(Fragment24)
        print("respuesta ",answer)
        
#-----------------------------------------------------------------------

    if __name__ == "__main__":
        receive_message()    


#-----------------------------------------------------------------
#0100 1110
#0100 1000
#0100 1001
#0100 1010
#0100 1011
#0100 1100
#0100 1101
#0100 1110
 
 
 

 
 
 
 
 
 
  
  
  
            

