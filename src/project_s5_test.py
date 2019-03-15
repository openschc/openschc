
from SCHC_server import SCHC_server
import binascii
from simsched import SimulScheduler as Scheduler
import sys

class Project_s5_test:
    def send_message():
        #read parameters
        if len(sys.argv) == 2:
            ruleId = str(sys.argv[1])
            fileToSend = "testfile.txt"
        elif len(sys.argv) == 3:
            ruleId = str(sys.argv[1])
            fileToSend = str(sys.argv[2])
        else:
            ruleId = "1"
            fileToSend = "testFile.txt"
        ruleId = int(ruleId)
        print("ruleId: ", ruleId, "fileToSend: ", fileToSend)
        #create protocol instance
        scheduler = Scheduler()
        schc = SCHC_server(scheduler)

        '''Message payload generation'''
        '''payload = bytearray(range(1, 20+1))
        print("Payload")
        print(binascii.hexlify(payload))
        print("Payload size:", len(payload))
        print("")'''

        #read file for payload
        file = open(fileToSend, 'r')
        print('file: ', file)
        payload = file.read().encode()
        print("Payload")
        print(binascii.hexlify(payload))
        print("Payload size:", len(payload))
        print("")
        #send message
        schc.sendMessage(payload, ruleId)
        scheduler.run()


    def receive_message():
        
        schc = SCHC_server()
        '''Fragment1 = b'\x48\x01\x02\x03\x04\x05\x06'
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
        Fragment1 = b'\x48\x32\x30\x31\x38\x2d\x31'
        Fragment2 = b'\x48\x31\x2d\x32\x30\x20\x31'
        Fragment3 = b'\x48\x31\x3a\x30\x30\x3a\x34'
        Fragment4 = b'\x48\x35\x20\x2d\x20\x76\x61'
        Fragment5 = b'\x48\x6e\x74\x61\x67\x65\x5f'
        Fragment6 = b'\x48\x70\x72\x6f\x32\x2e\x70'
        Fragment7 = b'\x48\x79\x20\x28\x37\x32\x36'
        Fragment8 = b'\x48\x29\x20\x2d\x20\x49\x4e'
        Fragment9 = b'\x48\x46\x4f\x20\x3a\x20\x4d'
        Fragment10 = b'\x48\x65\x6d\x6f\x69\x72\x65'
        Fragment11 = b'\x48\x20\x63\x6f\x6e\x73\x6f'
        Fragment12 = b'\x48\x6c\x65\x20\x76\x69\x64'
        Fragment13 = b'\x48\x65\x65\x0a\x32\x30\x31'
        Fragment14 = b'\x48\x38\x2d\x31\x31\x2d\x32'
        Fragment15 = b'\x48\x30\x20\x31\x31\x3a\x30'
        Fragment16 = b'\x48\x30\x3a\x34\x35\x20\x2d'
        Fragment17 = b'\x48\x20\x76\x61\x6e\x74\x61'
        Fragment18 = b'\x48\x67\x65\x5f\x70\x72\x6f'
        Fragment19 = b'\x48\x32\x2e\x70\x79\x20\x28'
        Fragment20 = b'\x48\x34\x36\x33\x29\x20\x2d'
        Fragment21 = b'\x48\x20\x49\x4e\x46\x4f\x20'
        Fragment22 = b'\x48\x3a\x20\x49\x6e\x74\x65'
        Fragment23 = b'\x48\x72\x76\x61\x6c\x6c\x65'
        Fragment24 = b'\x48\x20\x64\x27\x61\x72\x63'
        Fragment25 = b'\x48\x68\x69\x76\x61\x67\x65'
        Fragment26 = b'\x48\x20\x3d\x20\x36\x30\x20'
        Fragment27 = b'\x48\x6d\x69\x6e\x2e\x0a'
        Fragment28 = b'\x4f\x1e\x20\x1a\x90'
#-----------------------------------------------------------------------
        schc.reassemble(Fragment1)
        schc.reassemble(Fragment2)
        schc.reassemble(Fragment3)
        schc.reassemble(Fragment4)
        schc.reassemble(Fragment5)
        schc.reassemble(Fragment6)
        schc.reassemble(Fragment7)
        schc.reassemble(Fragment8)
        schc.reassemble(Fragment9)
        schc.reassemble(Fragment10)
        schc.reassemble(Fragment11)
        schc.reassemble(Fragment12)
        schc.reassemble(Fragment13)
        schc.reassemble(Fragment14)
        schc.reassemble(Fragment15)
        schc.reassemble(Fragment16)
        schc.reassemble(Fragment17)
        schc.reassemble(Fragment18)
        schc.reassemble(Fragment19)
        schc.reassemble(Fragment20)
        schc.reassemble(Fragment21)
        schc.reassemble(Fragment22)
        schc.reassemble(Fragment23)
        schc.reassemble(Fragment24)
        schc.reassemble(Fragment25)
        schc.reassemble(Fragment26)
        schc.reassemble(Fragment27)
        schc.reassemble(Fragment28)




#-----------------------------------------------------------------------

    if __name__ == "__main__":
        #receive_message()
        send_message()
