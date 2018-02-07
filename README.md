SCHC test
==========

This software is expected to run on MicroPython.
Only premitive python code and modules are used
so that this software can work on pycom.

## requirement

- python3 is required. not tested on python2.

## TODO

- ack requesting.
- bitmap optimization.
- abort messaging.

## clone

some modules are included.  therefore, you need to clone recursively.

    git clone --recursive git://github.com/tanupoo/schc-fragment.git

or

    git clone git://github.com/tanupoo/schc-fragment.git
    cd schc-fragment
    git submodule update --init --recursive

## fragment sender

           |      
           V      
    +------------+
    |  compress  |
    +------------+
    |  fragment  |
    +------------+
           |
           V
      Lower Layer
    
      +--- ... --+-------------- ... --------------+-----------+--...--+
      |  Rule ID |Compressed Hdr Fields information|  payload  |padding|
      +--- ... --+-------------- ... --------------+-----------+--...--+
    
                 Figure 4: LPWAN Compressed Format Packet
    
         +-----------------+-----------------------+---------+
         | Fragment Header |   Fragment payload    | padding |
         +-----------------+-----------------------+---------+
    
                        Figure 6: Fragment format.

## Fragment State Machine in the fragment sender

- WINDOW mode

            .----------------------------------------------------<----.
            |                                                         |
            |   .-----<---.          .-<- RETRY_ALL0 -.               |
            |   |         |          |                |R              |
            |   |         |          |                |               |
    INIT ->-+-+-+-> CONT -S-->-+--->-+--> SEND_ALL0 --B---> WIN_DONE -'
              |                |                      |                  
              |--<-------------'    T1                '---> FAIL         
              |          All-1       .---> FAIL      T1                  
              |                      |                                 
              '-->--+--> SEND_ALL1 --B--R--->---------> DONE
                    |                   |  
                    |                   | 
                    '-<- RETRY_ALL1 -<--' 

- NO-ACK mode

                .-----<---.
                |         |
                |         |
    INIT ->-+-+-+-> CONT -S-->-+
              |                |
              |--<-------------'
              |          All-1
              |
              '-->--+--> SEND_ALL1 --------->---------> DONE

## fragment receiver

the size of the rule id is defined in the context X.
therefore if you receive a packet, you can take the rule id.

    +---------------------
    | rule id | dtag | ...
    +---------------------

once you get the rule id, then you can know how to defragment and decompress.

Note that the receiver never sends any FCN that the receiver
hasn't received.
the receiver only sends a bitmap which is recorded the fact
sequentially that the receiver received a fragment that the
sender sent.

### state machine.

The state is mainteined in each window.

XXX When the fragment receiver (FR) sends an ack to the fragent sender (FS) ?
XXX it should only happen immediately after FR receives all-x fragment ?
XXX or, plus, whenever FR receves any fragment retransmitted ?

    S: sending something
    R: receiving something
    B: I/O Blocking
    T1, T2: Time out

                    Pull ACK0
                 .-->---------------.
                 |                  |
             .-<-R--B- CONT_ALL0 -<-S-<-.
             |      |                   |          Pull ACK0
             |    T1'-> FAIL         NG |   .----------<---.
             |                          |   |              |
         .->-+----->-- CHECK_ALL0 ----+-'   |             R|
         |                            |     |              |  T2
         '-------------------.     OK +--->-+-> SEND_ACK0 -B->-.
                             |        |     S                  |
             .-<- CONT <-.   |        |                        |
             |           |   |All-0   |  ACK-ON-ERROR          |
    INIT -->-+-----B-----R->-'        '--->--------------------+-> WIN_DONE
                   |     |                                        
        FAIL <-----' T1  |                                        
                         |                  S                     
         .-------------<-' All-1     OK .->-+-> SEND_ACK1 -B->---> DONE
         |                              |   |              |  T2
         '->-+----->-- CHECK_ALL1 ------+   |             R|
             |                          |   |              |
             |    T1.-> FAIL            |   '----------<---'
             |      |                   |          Pull ACK1
             '-<-R--B- CONT_ALL1 -<-S-<-'
                 |                  |  NG
                 '-->---------------'
                    Pull ACK1

In NO-ACK mode, the state transition is:

             .-<- CONT <-.         
             |           |
    INIT -->-+-----B-----R------->---> CHECK_ALL1 --+-> DONE
                   |       All-1
        FAIL <-----' T1

## Message format

- Rule ID:
- FCN: N bits, 
- DTag: T bits, the size is 0 to 2^T-1
- W: 1 bit, Window bit.
- MIC: M bits, CRC32 is recommended.
- C: 1 bit, set to 1 when MIC was matched. Otherwise, set to 0.
- bitmap: will be truncated. see 5.5.3
- P1,P2: padding, must be within 7.
- []: denoting a byte boundary.

## Bitmap size

N = 3
All-1 = 7
All-0 = 0
FCN = [ 6, 5, 4, 3, 2, 1, 0 ]
Bitmap Size = 7

## NO ACK mode

Any packets are from the fragment sender to the fragment receiver.
No packets are from the fragment receiver.

- the fragments except the last one

     Format: [ Rule ID | DTag |FCN|P1][   Payload   |P2]

- the last fragment

     Format: [ Rule ID | DTag |FCN|   MIC  |P1][    Payload     |P2]

- Abort message to abort the transmission.

XXX not defined in draft-09.

     Format: [ Rule ID | DTag |FCN|   FF   |P1]

### Example message of NO ACK mode

Rule ID = 6, DTag = 2, N = 1

- The first fragment

     Format: [ Rule ID | DTag |FCN|P1][ Payload |P2]
       Size:  3         3      1   1   8         0    = 16 bits
    Content:  110       010    0   0   01001101

- The last fragment

     Format: [ Rule ID | DTag |FCN|  MIC   |P1][ Payload |P2]
       Size:  3         3      1   32       1   8         0    = 48 bits
    Content:  110       010    1   010..101 0   11100100

- Abort message

     Format: [ Rule ID | DTag |FCN|   FF   |P1]
       Size:  3         3      1   8        1    = 16 bits
    Content:  110       010    0   11111111 0

## Window mode

### Packets from the fragment sender to the fragment receiver.

- Fragmentation header and payload

     Format: [ Rule ID | DTag |W|FCN|P1][ Payload |P2]

- All-0 fragment

The all bits of FCN is set to All-0.

     Format: [ Rule ID | DTag |W|FCN|P1][ Payload |P2]

- Request of Ack for All-0, All-0 empty.

The all bits of FCN is set to All-0.

     Format: [ Rule ID | DTag |W|FCN|P1]

- All-1 fragment, the last fragment

The all bits of FCN is set to All-1.

     Format: [ Rule ID | DTag |W|FCN|  MIC   |P1][ Payload |P2]

- Requst of Ack for All-1, called All-1 empty

The all bits of FCN is set to All-1.

     Format: [ Rule ID | DTag |W|FCN|  MIC   |P1]

XXX Why is the mis required ?

- All-1 Abort message to abort the transmission.

XXX what is the value of FCN ?

     Format: [ Rule ID | DTag |W|FCN|  FF    |P1]

### Example message from the fragment sender

- The first fragment

     Format: [ Rule ID | DTag |W|FCN|P1     ][ Payload |P2|
       Size:  3         3      1 3   6        8         0    = 24
    Content:  110       010    0 110 000000   11100100

- All-0 fragment

     Format: [ Rule ID | DTag |W|FCN|P1     ][ Payload |P2|
       Size:  3         3      1 3   6        8         0    = 24
    Content:  110       010    0 000 000000   11100100

- Request of Ack for All-0

     Format: [ Rule ID | DTag |W|FCN|P1     ]
       Size:  3         3      1 3   6        = 16
    Content:  110       010    0 000 000000

- All-1 fragment, the last fragment

     Format: [ Rule ID | DTag |W|FCN|  MIC   |P1      ][ Payload |P2]
       Size:  3         3      1 3   32       6         8         0    =
    Content:  110       010    0 111 010..101 000000    11100100

### Packets from the fragment receiver to the fragment sender.

- Ack for All-0, some fragments have not been received.

    Format: [ Rule ID | DTag |W|  Bitmap  |P1]

- Ack for All-0, all fragments have been received.

    Format: [ Rule ID | DTag |W|P1]

- Ack for All-1 when MIC was correct.

     Format: [ Rule ID | DTag |W|C|P1]

- Ack for All-1 when MIC was incorrect.

     Format: [ Rule ID | DTag |W|C|  Bitmap  |P1]

- ACK Abort

     Format: [ Rule ID | DTag |W| All-1 |  FF  |P1]

### Example message from the fragment receiver

- Ack for All-0

     Format: [ Rule ID | DTag |W|  Bitmap  |P1]
       Size:  3         3      1 7          2       = 16
    Content:  110       010    0 0100110    00

- Ack for All-0, bitmap optimization applied.

NOTE: This is the case the bitmap has not been truncated
so as to align a byte boundary.

     Format: [ Rule ID | DTag |W|  Bitmap  |P1]
       Size:  3         3      1 7          2      = 16
    Content:  110       010    0 1101111    00

- Ack for All-1 if MIC was correct.

     Format: [ Rule ID | DTag |W|C|P1]
       Size:  3         3      1 1 0
    Content:  110       010    0 1

- if MIC was incorrect.

     Format: [ Rule ID | DTag |W|C|  Bitmap  |P|
       Size:  3         3      1 1 7          1   = 16
    Content:  110       101    0 0 1011111    0

- ACK Abort

     Format: [ Rule ID | DTag |W|All-1|  FF  |P|
       Size:  3         3      1 3     8      7  = 24
    Content:  110       101    0 111   0100110     00

## Bitmap optimization

- e.g. Ack for All-0, all fragments has been received.

the format before transmission.

     Format: [ Rule ID | DTag |W|  Bitmap  |
       Size:  2         3      1 7
    Content:  11        110    0 1111111

the format transmitted is going to be below.

     Format: [ Rule ID | DTag |W|  Bitmap  |P1]
       Size:  2         3      1 2          0
    Content:  11        110    0 11

- e.g. Ack for All-0, the first 2 fragments has not been received.

the format before transmission.

     Format: [ Rule ID | DTag |W|  Bitmap  |
       Size:  2         3      1 7
    Content:  11        110    0 0011111

the format transmitted is going to be below.

     Format: [ Rule ID | DTag |W|  Bitmap  |P1]
       Size:  2         3      1 2          0
    Content:  11        110    0 00

- e.g. Ack for All-0, the first 3 fragments hasn't been received.

the format before transmission.

     Format: [ Rule ID | DTag |W|  Bitmap  |
       Size:  2         3      1 7
    Content:  11        110    0 0001111

the format transmitted is going to be below.

     Format: [ Rule ID | DTag |W|  Bitmap  |P1]
       Size:  2         3      1 7          3
    Content:  11        110    0 0001111    000

- e.g. N=4, Ack for All-1, the first fragment hasn't been received.

the format before transmission.

     Format: [ Rule ID | DTag |W|C|  Bitmap  |
       Size:  2         3      1 1 15
    Content:  11        110    0 0 0111 1111 1111 111

the format transmitted is going to be below.

     Format: [ Rule ID | DTag |W|C|  Bitmap  ]
       Size:  2         3      1 1 1
    Content:  11        110    0 0 0

## Usage

You need two consoles.

One is for the sender.

    ./test-client-udp.py 127.0.0.1 9999

The other is for the receiver.

    ./test-server-udp.py 9999 -dd 

The -dd option would be useful for you first trial.

### test-client

    usage: test-client-udp.py [-h] [-I MSG_FILE] [--interval INTERVAL]
                              [--l2-size L2_SIZE] [--rid RULE_ID]
                              [--loss-list LOSS_LIST] [--loss-rate LOSS_RATE]
                              [--loss-random] [-v] [-d] [--verbose]
                              [--debug DEBUG_LEVEL] [--version]
                              SERVER PORT
    
    this is SCHC example.
    
    positional arguments:
      SERVER                specify the ip address of the server.
      PORT                  specify the port number in the server.
    
    optional arguments:
      -h, --help            show this help message and exit
      -I MSG_FILE           specify the file name including the message, default
                            is stdin.
      --interval INTERVAL   specify the interval for each sending.
      --l2-size L2_SIZE     specify the payload size of L2. default is 6.
      --rid RULE_ID         specify the rule id. default is 1
      --loss-list LOSS_LIST
                            specify the index numbers to be lost for test. e.g.
                            --loss-list=3,8 means the 3rd and 8th packets are
                            going to be lost.
      --loss-rate LOSS_RATE
                            specify the rate of the packet loss. e.g. --loss-
                            rate=0.2 means 20% to be dropped.
      --loss-random         enable to lose a fragment randomly for test.
      -v                    enable verbose mode.
      -d                    increase debug mode.
      --verbose             enable verbose mode.
      --debug DEBUG_LEVEL   specify a debug level.
      --version             show program's version number and exit

### test-receiver

    usage: test-server-udp.py [-h] [--address SERVER_ADDRESS] [--port CONF_FILE]
                              [--timeout TIMEOUT] [-v] [-d] [--verbose]
                              [--debug _DEBUG_LEVEL] [--version]
                              PORT
    
    positional arguments:
      PORT                  specify the port number in the server.
    
    optional arguments:
      -h, --help            show this help message and exit
      --address SERVER_ADDRESS
                            specify the ip address of the server to be bind.
                            default is any.
      --port CONF_FILE      specify the configuration file.
      --timeout TIMEOUT     specify the number of the timeout.
      -v                    enable verbose mode.
      -d                    increase debug mode.
      --verbose             enable verbose mode.
      --debug _DEBUG_LEVEL  specify a debug level.
      --version             show program's version number and exit



