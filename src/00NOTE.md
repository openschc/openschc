
## Notation

    "p": a pdding bit, which must be ignored during the MIC conputation.
    "m": represents a content of MIC.
    "s": a significant bit of padding, which must be included
         for the MIC calculation.
    "r": rule ID field.
    "d": dtag field.
    "w": W field.
    "f": FCN field.
    "a": another significant bit of padding to align the byte boundary
         for the MIC calculation.  the value is zero.

## Q. No-Ack mode and the All-1 fragment.

In No-ACK mode, for example,

    the size of MTU is 56 bits.
    the size of L2 word is 8 bits.
    The size of the SCHC fragment header is 11 bits.
    The size of MIC is 32 bits.

Assumed the size of SCHC packet is 13 bytes (104 bits).

How are the 3rd and 4th fragments ?

I thought that they including the 1st and 2nd are like below.

    |<- header ->|<---------------- tile 1 --------------->|
    |  11 bits   |                 45 bits                 | 1st

    |<- header ->|<---------------- tile 2 --------------->|
    |  11 bits   |                 45 bits                 | 2nd

    |<- header ->|<-  tile 3 ->|<- padding ->|
    |  11 bits   |   14 bits   |   7 bits    | 3rd

    |<- header ->|<------   MIC   ------>|<- padding ->|
    |  11 bits   |        32 bits        |    5 bits   | 4th

However, the sesion of 8.4.1 describes that only the All-1 SCHC
Fragment is padded as needed.

## Q. window number of the last fragment

L2 word is 8 bits.
L2 MTU is 48 bits.
The size of a tile is 32 bits.
The mode is ACK-on-Error.
the size of SCHC fragment header is 16 bits.
    the size of rule ID is 6 bits.
    the size of dtag is 3 bits.
    the size of W is 5 bits.
    the size of FCN is 2 bits.

The size of a SCHC packet is 9 bytes (72 bits).
The number of tiles is going to be 3.
Each fragment is gonna be:

          01234567 01234567 01234567 01234567 01234567 01234567
    Data: 00000100 10000010 ........ ........ ........ ........
          rrrrrrdd dwwwwwff 01234567 01234567 01234567 01234567

          01234567 01234567 01234567 01234567 01234567 01234567
    Data: 00000100 10000001 ........ ........ ........ ........
          rrrrrrdd dwwwwwff 01234567 01234567 01234567 01234567

          01234567 01234567 01234567
    Data: 00000100 10000000 ........
          rrrrrrdd dwwwwwff 01234567

The question is what the window number is for the last MIC fragment ?

          01234567 01234567 01234567 01234567 01234567 01234567
    Data: 00000100 10000?11 mmmmmmmm mmmmmmmm mmmmmmmm mmmmmmmm
          rrrrrrdd dwwwwwff |<------------  MIC ------------->|

The flow is like below:

           Sender               Receiver
             |-----W=0, FCN=2----->|
             |-----W=0, FCN=1----->|
             |-----W=0, FCN=0----->|
         (no ACK)
             |--W=1, FCN=7 + MIC-->|
             |<-- ACK, W=1, C=1 ---| C=1
           (End)

A.

8.2.2.2 "the last window MUST contain WINDOW_SIZE tiles or less." We didn't say (forgot to say) that it must have at least one tile.
8.4.3.1 "In an All-1 SCHC Fragment message, the sender MUST fill the W field with the window number of the last tile of the SCHC Packet."

This flow should be like below:

           Sender               Receiver
             |-----W=0, FCN=2----->|
             |-----W=0, FCN=1----->|
             |-----W=0, FCN=0----->|
             |--W=0, FCN=7 + MIC-->|
             |<-- ACK, W=1, C=1 ---| C=1
           (End)

Next, if the 3rd(FCN=0) and 4th(MIC) messages are lost, could you tell me the complete flow ?
Sorry, I forgot to say that WINDOW_SIZE is 3.

           Sender               Receiver
             |-----W=0, FCN=2----->|
             |-----W=0, FCN=1----->|
             |-----W=0, FCN=0---X->|
             |--W=0, FCN=7+MIC--X->|
             |-----W=0, FCN=0----->| ACK REQ
             |<-- ACK, W=0, C=1 ---| C=1
           (End)
             |<-- ACK, W=0, C=0 ---| C=0, Bitmap: 110
             |-----W=0, FCN=0----->|

The sender doesn't know whether the MIC should be sent or not.

## Q. last tile handling

word is 8 bits.  The size of a tile is 9 bits.
L2 MTU is 48 bits.  The size of a SCHC packet is 7 bytes.
The mode is ACK-on-Error.
the size of SCHC fragment header is 16 bits.
    the size of rule ID is 6 bits.
    the size of dtag is 3 bits.
    the size of W is 5 bits.
    the size of FCN is 2 bits.

          01234567 01234567 01234567 01234567 01234567 01234567 01234567
    Data: ........ ........ ........ ........ ........ ........ ........

The SCHC packet is gonna be separated into 7 tiles.

          012345678 012345678 012345678 012345678 012345678 012345678 01
    Data: ......... ......... ......... ......... ......... ......... ..

Each fragment is gonna be:

          01234567 01234567 01234567 01234567 01234567 01234567
    Data: 00000100 10000010 ........ ........ ........ ...ppppp
          rrrrrrdd dwwwwwff 01234567 01234567 01234567 012

          01234567 01234567 01234567 01234567 01234567 01234567
    Data: 00000100 10000001 ........ ........ ........ ...ppppp
          rrrrrrdd dwwwwwff 34567012 34567012 34567012 345

Because FCN=0 can not carry a tile of which the size is less than L2 word
AND there is no room to put the last tile in the All-1 fragment,
the last tile has to be put into the next window,
of which the number is 1, like below.

          01234567 01234567 01234567
    Data: 00000100 10000110 ..pppppp
          rrrrrrdd dwwwwwff 67

          01234567 01234567 01234567 01234567 01234567 01234567
    Data: 00000100 10000111 mmmmmmmm mmmmmmmm mmmmmmmm mmmmmmmm
          rrrrrrdd dwwwwwff |<------------  MIC ------------->|

However, from the view point of the receiver,
it looks that the All-0 fragment was lost.

How do we solve it ?

## Q. W field of Abort message and ACK-on-Error

> 8.3.4.1.  SCHC Sender-Abort
> 
>    If the W field is present,
> 
>    o  the fragment sender MUST set it to all 1's.  Other values are
>       RESERVED.
> 
>    o  the fragment receiver MUST check its value.  If the value is
>       different from all 1's, the message MUST be ignored.
> 
> 8.3.4.2.  SCHC Receiver-Abort
> 
>    If the W field is present,
> 
>    o  the fragment receiver MUST set it to all 1's.  Other values are
>       RESERVED.
> 
>    o  the fragment sender MUST check its value.  If the value is
>       different from all 1's, the message MUST be ignored.

Since No-ACK mode does not use W field.
In ACK-Allways, the size of the W field is 1, and its value depends on the least significant bit of the window counter.
Therefore, all one in the W field doesn't mean always the abort message.
In ACK-on-Error, the value of all ones in the W field is not reserved.  It is still allowed to be used in the regular message.
If the value of all ones is reserved, ACK-Allways doesn't work.
So, the text of "Other values are RESERVED." sounds strange.

Totally, I would say about the W field in the abort message:

    the fragment sender MUST set it to all ones.
    the fragment receiver MUST check its value. If the value is different from all ones,
    the message MUST NOT be handled for the abort message.

The receiver side is same.  How about this ?

## Q. window counetr of ACK-Always

It seems that "window counter" suddenly appears.

The window counter should be explained first in the section 8.4.2 ACK-Always.
Then, the section 8.4.2.1 Sender behavior should specify how to use the window counter
as similar to the receiver behavior.  e.g. when it's initialized.

Otherwise, the least significant bit of the window number sounds strange.

## content of Padding bits

> 9.  Padding management
> 
>    A Profile MAY define the value of the padding bits.  The RECOMMENDED
>    value is 0.

Do you allow the value of 1 for a regular padding (i.e. except of the abort message) ?
Since all ones has a meaning for the abort message, a regular padding should be 0 for consistency.

A.
it must be consistent.  The padding bit of 1 should be allowed.

## padding and MIC calculation

In draft-17,

> 8.2.3.  Integrity Checking
> 
>     Note that the concatenation of the complete SCHC Packet and the
>     potential padding bits of the last SCHC Fragment does not generally
>     constitute an integer number of bytes.  For implementers to be able
>     to use byte-oriented CRC libraries, it is RECOMMENDED that the
>     concatenation of the complete SCHC Packet and the last fragment
>     potential padding bits be zero-extended to the next byte boundary and
>     that the MIC be computed on that byte array.  A Profile MAY specify
>     another behaviour.

e.g.1. L2 word is 8 bits.  The size of a tile is 9 bits.  L2 MTU is 64 bits.
MAX_FCN is 6.  The mode is ACK-on-Error.
the size of SCHC fragment header is 10 bits.
    the size of rule ID is 3 bits.
    the size of dtag is 2 bits.
    the size of W is 2 bits.
    the size of FCN is 3 bits.

Each fragment is gonna be:

Assumed that the size of a SCHC packet is 4 bytes such as below.

          01234567 01234567 01234567 01234567
    Data: ........ ........ ........ ........

    ".": denotes a bit of either 0 or 1.

The SCHC packet is gonna be separated into 4 tiles.

          012345678 012345678 012345678 01234
    Data: ......... ......... ......... .....

Each fragment is gonna be:

          01234567 01234567 01234567
    Data: 00101001 100..... ...ppppp
          rrrddwwf ff012345 670

          01234567 01234567 01234567
    Data: 00101001 01...... ...ppppp
          rrrddwwf ff123456 701

          01234567 01234567 01234567
    Data: 00101001 00...... ...ppppp
          rrrddwwf ff234567 012

          01234567 01234567 01234567 01234567 01234567 01234567 
    Data: 00101001 11mmmmmm mmmmmmmm mmmmmmmm mmmmmmmm mm.....s
          rrrddwwf ff|<------------  MIC -------------->|34567

To calculate the MIC is required to align the byte boundary,
the input data of the MIC calculation is gonna be:

          012345678 012345678 012345678 01234567
    Data: ......... ......... ......... .....saa
          012345670 123456701 234567012 34567

No problem.

##

The All-1 fragment and the FCN=0 (All-0) fragment will not happen in same window.

If there was a FCN=0 fragment,
it means that at least, more than one tile was remained.
In this case, the right most bit always represents the tile of FCN=0.
If there was the All-1 fragment,
the right most bit always represents the tile of FCN=0.

##

> 8.3.1.1.  Regular SCHC Fragment
> 
>    The Fragment Payload of a SCHC Fragment with FCN == 0 (called an
>    All-0 SCHC Fragment) MUST be at least the size of an L2 Word.  The
>    rationale is that, even in the presence of padding, an All-0 SCHC
>    Fragment needs to be distinguishable from the SCHC ACK REQ message,
>    which has the same header but has no payload (see Section 8.3.3).

If the size of the last tile of a SCHC packet is less than L2 word
AND the last tile number is zero,
AND it doesn't fit into the All-1 fragment,
then, the last tile is carried by the next window.

## Bitmap in the last window

Assumed flow could be:

            Sender             Receiver
             |-----W=0, FCN=6----->|
             |-----W=0, FCN=5----->|
             |-----W=0, FCN=4----->|
             |-----W=0, FCN=3----->|
             |-----W=0, FCN=2----->|
             |-----W=0, FCN=1----->|
            A|-----W=0, FCN=0----->|
             |-----W=1, FCN=6----->|
             |- W=1, FCN=7+MIC --->|
             |<-- ACK, W=1, C=1 ---|

If the message A was lost, the bitmap would be 1111110.

            Sender             Receiver
             |-----W=0, FCN=6----->|
             |-----W=0, FCN=5----->|
             |-----W=0, FCN=4----->|
             |-----W=0, FCN=3----->|
             |-----W=0, FCN=2----->|
             |-----W=0, FCN=1----->|
            B|- W=0, FCN=7+MIC --->| containing the last tile.
             |<-- ACK, W=0, C=1 ---|

If the message B was lost, the bitmap would be 1111110.

## the index of rule

My scenario is like below:

      Node A                    Node B
      Dev                       APP
      DevIID(A)                 AppIID(B)
                 SCHC packet
               ---- rid:1 --->

                 SCHC frag
               ---- rid:2 --->

                 SCHC frag
               <--- rid:3 ----

A set of rules at Node A would be:

    "ruleID": 1,
    "DevIID": "A"
    "AppIID": "B"
    "compression": {...}

    "ruleID": 2,
    "localID": "A"
    "remoteID": "B"
    "fragmentation": {...}

    "ruleID": 3,
    "localID": "B"
    "remoteID": "A"
    "fragmentation": {...}

If we use DevIID/AppIID as the key in a fragmentation rule,
the rules are like below:

    "ruleID": 2,
    "DevIID": "A"
    "AppIID": "B"
    "fragmentation": {...}

    "ruleID": 3,
    "DevIID": "A"
    "AppIID": "B"
    "fragmentation": {...}

When Node A initiates, it can not know which rule should be taken.

rule set at Node A

    "ruleID": 1,
    "DevIID": "A"
    "AppIID": "B"
    "compression": {...}

    "ruleID": 2,
    "DevIID": "A"
    "AppIID": "B"
    "fragmentation": {...}

    "ruleID": 3,
    "DevIID": "A"
    "AppIID": "B"
    "fragmentation": {...}

The answer is:

At the sender side, FR rules don't need to have any DevIID/AppIID, localID/remoteID whatever.
After compression, if the frame is larger than the L2 MTU.  Fragmentation will be done.

When a device sends an IPv6 packet, AppIID in the destination field of IPv6 header can be used to find a CD rule.  And, when the device receives a message from the L2, the L2 Address of the device can be used to find a FR/CD rule if needed.  However, typically, the device can takes a rule ID without search the rules.

When a middle box in the network decides whether a packet needs to do CD/FR, DevIID in the destination field of IPv6 header can be used.  And, when the middle box needs to find a FR/CD rule, L2 address of the device can be used.

Now, the configuration could be:

    Context:
    "L2Addr": "A"
    "dstIID": "B"

    "ruleID": 1,
    "compression": {...}

    "ruleID": 2,
    "fragmentation": {...}

    "ruleID": 3,
    "fragmentation": {...}

dstIID is used to find a rule for outgoing packet.
L2Addr is used to find a rule for incoming packet.
This can work both sides.

      Dev                     CD/FR Node       App
      DevIID(A)                                AppIID(B)
                 SCHC packet
               ---- rid:1 --->          <---->

                 SCHC frag
               ---- rid:2 --->

                 SCHC frag
               <--- rid:3 ----

When Node A receives packets; one is an ACK message which was initiated by A, another is new SCHC fragment initiated by B.

XXX
On the Network side, since there is one Context per Device, a Context is associated to a DevID, but the DevID is not part of that Context, strictly speaking.
Context is a term that means the "list of Rules for the communication on one LPWAN link".
Therefore, on the Device there is one and only one Context active at any one time. On the Network side, there is one and only one Context active per Device at any one time.


