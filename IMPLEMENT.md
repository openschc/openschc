Implementation memo
===================

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

    S: sending something
    R: receiving something
    B: I/O Blocking
    T1: Timer of CONT* state in the fragment receiver.
    T2: Timer of SEND_ALL* state in the fragment sender.
    T3: Timer of CONT_ALL* state in the fragment receiver.
    T4: Timer of SEND_ACK* state in the fragment receiver.
    T5: Timer to wait for the next fragment from the sender
        after WIN_DONE in the fragment receiver.

    If the link is not stable, T1 should be bigger than you excepted.
    T2, T3 and T4 are recomended to be more than double of T1.
    This is because these are round-trip flow.
    T5 is recommended to be bigger than T2.
    i.e. 2*T1 =< T2 =< T3 =< T4 < T5

- WINDOW mode

            .----------------------------------------------------<----.
            |                                                         |
            |   .-----<---.          .-<- RETRY_ALL0 -.               |
            |   |         |          |                |R              |
            |   |         |          |                |               |
    INIT ->-+-+-+-> CONT -S-->-+--->-+--> SEND_ALL0 --B---> WIN_DONE -'
              |                |                      |                  
              |--<-------------'    T2                '---> FAIL         
              |          All-1       .---> FAIL      T2                  
              |                      |                                 
              '-->--+--> SEND_ALL1 --B--R--->---------> DONE
                    |                   |  
                    |                   | 
                    '-<- RETRY_ALL1 -<--' 

XXX should it send a all-0 when it finishes to send all packets of the retranmission every time ?
XXX ==> assuming No.  it will send ALL0 or ALL0 empty after retransmiting.

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

### the state of the message holder

    INIT --> CONT --> DONE --> DYING --> DEAD

      INIT: initial state.
      CONT: receiving the fragments.
      DONE: finised to receive the fragments. ready to show the message.
     DYING: waiting for the response from the sender.
            once the message is showed at DONE state,
            the stae is changed into DYING.
      DEAD: ready to purge the holder.

### state machine of the receiver.

The state is mainteined in each window.

XXX When the fragment receiver (FR) sends an ack to the fragent sender (FS) ?
XXX it should only happen immediately after FR receives all-x fragment ?
XXX or, plus, whenever FR receves any fragment retransmitted ?

                    
             .-->---------------.
             |                  |  ACK
         .-<-R--B-- CONT_ALL0 <-+-<-S-<-.
         |      |                       |
         |    T3'-> FAIL             NG |
         |                              |          Pull ACK0
    .-->-+----->-- CHECK_ALL0 --------+-'   .----------<---.
    |                                 |     |              |
    |                              OK |     |              |T4
    '------------------------.        +--->-S-> SEND_ACK0 -B->-.
                             |        |    ACK                 |
             .-<- CONT <-.   |        |                        |
             |           |   |All-0   |  ACK-ON-ERROR          |
    INIT -->-+-----B-----R->-'        '--->--------------------+-> WIN_DONE
                   |     |                                        
        FAIL <-----' T1  |                                        
                         |                 ACK
    .------------------<-' All-1        .->-S-> SEND_ACK1 -B->---> DONE
    |                                OK |   |              |T4
    |                                   |   |              |
    '-->-+----->-- CHECK_ALL1 ----------+   '----------<---'
         |                              |          Pull ACK1
         |    T3.-> FAIL             NG |   
         |      |                       |   
         '-<-R--B-- CONT_ALL1 <-+-<-S-<-'
             |                  |  ACK
             '-->---------------'

In NO-ACK mode, the state transition is:

             .-<- CONT <-.         
             |           |
    INIT -->-+-----B-----R------->---> CHECK_ALL1 --+-> DONE
                   |       All-1
        FAIL <-----' T1

- CONT_ALL0 and CONT_ALL1

if the receiver gets an empty ALL0 (or ALL1 in CONT_ALL1), the state will be changed into CHECK_ALL0.

## Abort message

XXX draft-09 doesn't define well.

## Abort Policy

the fragment receiver receives:

- a message of which the MIC is not matched third times.
- a message which is not of the maximum value of FCN. i.e. (2**fcn_size)-2.

