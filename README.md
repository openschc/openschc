SCHC test
==========

This software is expected to run on MicroPython.
Only premitive python code and modules are used
so that this software can work on pycom.

## requirement

python2 or python3

## clone

some modules are included.  therefore, you need to clone recursively.

    git clone --recursive git://github.com/tanupoo/schc-fragment.git

or

    git clone git://github.com/tanupoo/schc-fragment.git
    cd schc-fragment
    git submodule update --init --recursive


----

MEMO

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

## fragment receiver

           A
           |
    +------------+
    | decompress |
    +------------+
    |  defagment |
    +------------+
           A
           |
      Lower Layer

the size of the rule id is defined in the context X.
therefore if you receive a packet, you can take the rule id.

    +---------------------
    | rule id | dtag | ...
    +---------------------

once you get the rule id, then you can know how to defragment and decompress.

## NO ACK mode

Any packets are from the fragment sender to the fragment receiver.
No packets are from the fragment receiver.

- Fragmentation Header for Fragments except the Last One, No ACK option

    <------------ R ---------->
                <--T--> <--N-->
    +-- ... --+- ...  -+- ... -+---...---+
    | Rule ID |  DTag  |  FCN  | payload |
    +-- ... --+- ...  -+- ... -+---...---+

- All-1 Fragmentation Header for the Last Fragment, No ACK option

    <------------- R ---------->
                  <- T -> <-N-><----- M ----->
    +---- ... ---+- ... -+-----+---- ... ----+---...---+
    |   Rule ID  | DTag  |  1  |     MIC     | payload |
    +---- ... ---+- ... -+-----+---- ... ----+---...---+

## Window mode

### Packets from the fragment sender to the fragment receiver.

- fragmentation header

    <------------ R ---------->
               <--T--> 1 <--N-->
    +-- ... --+- ... -+-+- ... -+---...---+
    | Rule ID | DTag  |W|  FCN  | payload |
    +-- ... --+- ... -+-+- ... -+---...---+

- All-1 Fragmentation Header for the Last Fragment

    <------------ R ------------>
               <- T -> 1 <- N -> <---- M ----->
    +-- ... --+- ... -+-+- ... -+---- ... ----+---...---+
    | Rule ID | DTag  |W| 11..1 |     MIC     | payload |
    +-- ... --+- ... -+-+- ... -+---- ... ----+---...---+
                          (FCN)

- All-1 for Retries format fragment also called All-1 empty

    <------------ R ------------>
               <- T -> 1 <- N -> <---- M ----->
    +-- ... --+- ... -+-+- ... -+---- ... ----+
    | Rule ID | DTag  |W|  1..1 |     MIC     | (no payload)  TODO
    +-- ... --+- ... -+-+- ... -+---- ... ----+
                          (FCN)

- All-1 for Abort format fragment

    <------------ R ------------>
               <- T -> 1 <- N ->
    +-- ... --+- ... -+-+- ... -+
    | Rule ID | DTag  |W| 11..1 | (no MIC and no payload)  TODO
    +-- ... --+- ... -+-+- ... -+

### Packets from the fragment receiver to the fragment sender.

    <--------  R  ------->
                <- T -> 1
    +---- ... --+-... -+-+----- ... ---+
    |  Rule ID  | DTag |W|   bitmap    |
    +---- ... --+-... -+-+----- ... ---+

- Example of the bitmap in Window mode, in any window unless
  the last one, for N=3)

    <-------   R  ------->
                <- T -> 1 6 5 4 3 2 1   0
    +---- ... --+-... -+-+-+-+-+-+-+-+-----+
    |  Rule ID  | DTag |W|1|0|1|1|0|1|all-0|   TODO
    +---- ... --+-... -+-+-+-+-+-+-+-+-----+

- Example of the bitmap in Window mode for the last window,
  for N=3) 

    <-------   R  ------->
                <- T -> 1 6 5 4 3 2 1   7
    +---- ... --+-... -+-+-+-+-+-+-+-+-----+
    |  Rule ID  | DTag |W|1|0|1|1|0|1|all-1|    TODO
    +---- ... --+-... -+-+-+-+-+-+-+-+-----+

- ACK Abort format fragment

    <----- Complete Byte ------><--- 1 byte --->
    <-------   R  ------->
                 <- T -> 1
    +---- ... --+-... -+-+-+-+-+-+-+-+-+-+-+-+-+
    |  Rule ID  | DTag |W| 1..1|      FF       |  TODO
    +---- ... --+-... -+-+-+-+-+-+-+-+-+-+-+-+-+

## XXX

     <------------ R ------------>
                <- T -> 1 <- N ->
     +-- ... --+- ... -+-+- ... -+--- ... ---+
     | Rule ID | DTag  |W|  0..0 |  payload  |  TODO
     +-- ... --+- ... -+-+- ... -+--- ... ---+
      Figure 12: All-0 format fragment

     <------------ R ------------>
                <- T -> 1 <- N ->
     +-- ... --+- ... -+-+- ... -+
     | Rule ID | DTag  |W|  0..0 |   TODO
     +-- ... --+- ... -+-+- ... -+
      Figure 13: All-0 empty format fragment
