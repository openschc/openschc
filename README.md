SCHC test
==========

This software is expected to run on MicroPython.
Only premitive python code and modules are used
so that this software can work on pycom.

## requirement

- python3 is required. not tested on python2.

## TODO

- bitmap optimization
- abort messaging

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

### state machine

- WINDOW mode

            .-----------------------------------------------------<----.
            |                                                          |
            |     .-----<---.       .-<- RETRY_ALL0 -.                 |
            |     |         |       |                |                 |
    INIT ->-+--+--+-> CONT -+->-+->-+--> SEND_ALL0 --+->-+-> WIN_DONE -+-> DONE
               |                |                        |
               '-------->-------+->-+--> SEND_ALL1 --+->-'
                                    |                | 
                                    '-<- RETRY_ALL1 -' 

- NO-ACK mode

                  .-----<---.                                        
                  |         |                                        
    INIT ->-+--+--+-> CONT -+->-+                         +------------+-> DONE
               |                |                         |
               '-------->-------+------> SEND_ALL1 ---+->-'

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

             +------------------------------------<------.
             |                                           |
             |     .-----<---.       .-<- CONT_ALL0 --.  |
             |     |         |       |                |  |
     INIT ->-+--+--+-> CONT -+->-+->-+--> SEND_ACK0 --+--'
                |                |                  
                '-------->-------+->-+--> SEND_ACK1 --+---> DONE
                                     |                | 
                                     '-<- CONT_ALL1 --' 

    RECV_ACK1

XXX When the fragment receiver (FR) sends an ack to the fragent sender (FS) ?
XXX it should only happen immediately after FR receives all-x fragment ?
XXX or, plus, whenever FR receves any fragment retransmitted ?

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

The all bits of FCN is set to 0.

     Format: [ Rule ID | DTag |W|FCN|P1][ Payload |P2]

- Request of Ack for All-0

The all bits of FCN is set to 0.

     Format: [ Rule ID | DTag |W|FCN|P1]

- All-1 fragment, the last fragment

The all bits of FCN is set to 1.

     Format: [ Rule ID | DTag |W|FCN|  MIC   |P1][ Payload |P2]

- All-1 for Retries format fragment also called All-1 empty

The all bits of FCN is set to 1.

     Format: [ Rule ID | DTag |W|FCN|  MIC   |P1]

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

- Ack for All-0

    Format: [ Rule ID | DTag |W|  Bitmap  |P1]

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

