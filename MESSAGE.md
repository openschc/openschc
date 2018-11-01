Message Format
==============

## FCN value and other significant values

for example,

    N = 3
    All-1 = 7
    All-0 = 0
    FCN = [ 6, 5, 4, 3, 2, 1, 0 ]
    Bitmap Size = 7

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

Note that P1 should be 0, When you want to conform to the draft-09.

## NO ACK mode

Any packets are from the fragment sender to the fragment receiver.
No packets are from the fragment receiver except of the abort message.

XXX the receiver should send an abort message anytime even when NO ACK mode.

- the fragments except the last one

     Format: [ Rule ID | DTag |FCN|P1][   Payload   |P2]

- the last fragment

     Format: [ Rule ID | DTag |FCN|   MIC  |P1][    Payload     |P2]

XXX is it allowed that the sender sends a last fragent with no payload ?
XXX ==> assuming yes.

- Abort message to abort the transmission.

XXX draft-09 only defines for the win modes.

     Format: [ Rule ID | DTag |FCN|   FF   |P1]

- Abort message for the receiver to abort the transmission.

XXX draft-09 only defines for the win modes.

     Format: [ Rule ID | DTag |1..1|   FF   |P1]

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
    Content:  110       010    1   11111111 0

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

XXX is it allowed that the payload is empty ?
XXX ==> assuming yes.

- Requst of Ack for All-1, called All-1 empty

The all bits of FCN is set to All-1.

     Format: [ Rule ID | DTag |W|FCN|  MIC   |P1]

XXX Why is the mic required ?
XXX ==> because it is a same message of All-1 that the payload is empty.

- All-1 Abort message to abort the transmission.

     Format: [ Rule ID | DTag |W|FCN|  FF    |P1]

XXX what is the value of FCN ?
XXX draft-09 assumes the size of Rule ID, DTag, W, FCN is aligned
XXX to the byte boundary.

xXX how about this, in which W-bit is just reveresed.
XXX Format: [ Rule ID | DTag |W|P1]

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

