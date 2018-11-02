Implementation memo
===================

## NOTE

- Rule ID (RID) and the length of this field must be negotiated
  between the nodes in out-of-band before they start communication.

- There is a padding between the SCHC fragment header and the payload.
  This should be removed in the future.

- Rule ID is not changed while all fragments of a message are sent
  to the receiver.

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
    T4 is recommended to be a bit bigger than T3.
    T5 is recommended to be bigger than T3.
    i.e. 2*T1 =< T2 =< T3 < T4 <= T5

- WINDOW mode

            .----<------------------------------------------------------.
            |                                                           |
            |                      .-------->--------.                  |
            |                      |                 |                  |
            |   .------<---.       S-<- RETRY_ALL0 <-+-<-.              |
            |   |          |       |                     |              |
    INIT ->-+-+-+-> CONT --S->-+->-+--> SEND_ALL0 ---B---R--> WIN_DONE -'
              |                |                     |                  
              |--<-------------'                   T2'---> FAIL         
              |          All-1      T2.---> FAIL   
              |                       |                                 
              '-->--+--> SEND_ALL1 ---B----R--->------> DONE
                    |                      |  
                    S-<- RETRY_ALL1 -<-+-<-' 
                    |                  |
                    '---------->-------'

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

    INIT --> CONT --> CHECKING --> COLLECTED --> SERVED --> DEAD

    INIT     : initial state.
    CONT     : receiving the fragments.
    CHECKING : received ALL-1 fragment.
    COLLECTED: finised to receive the fragments. ready to show the message.
    SERVED   : showed the message, : waiting for the response from the sender.
    DEAD     : ready to purge the holder.

### state machine of the receiver.

The state is mainteined in each window.

XXX When the fragment receiver (FR) sends an ack to the fragent sender (FS) ?
XXX it should only happen immediately after FR receives all-x fragment ?
XXX or, plus, whenever FR receves any fragment retransmitted ?

                    
             .-->- CONT_ALL0 ->-.
             |                  |  ACK
         .-<-R----B-----------<-+-<-S-<-.
         |        |                     |
         |      T3'-> FAIL          ALL0_NG
         |                              |             empty ACK0
    .-->-+----->-- CHECK_ALL0 --------+-'   .----------<---R
    |                                 |     |              |
    |                             ALL0_OK   |              |
    |                                 |     |              |T4
    '------------------------.        +--->-S---------->---B->-.
                             |        |    ACK                 |
             .-<- CONT <-.   |        |                        |
             |           |   |All-0   |  ACK-ON-ERROR          |
    INIT -->-+-----B-----R->-'        '--->--------------------+-> WIN_DONE
                   |     |                                        
        FAIL <-----' T1  |                                           T5
                         |                 ACK
    .------------------<-' All-1      .--->-S-> SEND_ACK1 -B-----> DONE
    |                                 |     |              |T4
    |                             ALL1_OK   |              |
    |                                 |     |              |
    '-->-+----->-- CHECK_ALL1 --------+-+   '----------<---R
         |                              |             empty ACK1
         |       T3.-> FAIL         ALL1_NG   
         |         |                    |   
         '-<-R-----B----------<-+-<-S-<-'
             |                  |  ACK
             '-->- CONT_ALL1 ->-'

In NO-ACK mode, the state transition is:

             .-<- CONT <-.
             |           |
    INIT -->-+-----B-----R------> CHECK_ALL1 --+-> ALL1_OK --> DONE
                   |      All-1                |
        FAIL <-----' T1                        '-> ALL1_NG --> FAIL

- CHECK_ALL0 and CHECK_ALL1

check the MIC and set the ACK payload.  Then, if the MIC is correct, the state will be changed into ALL0_OK (or ALL1_OK in CHECK_ALL1)

- CONT_ALL0 and CONT_ALL1

if the receiver gets an empty ALL0 (or ALL1 in CONT_ALL1), the state will be changed into CHECK_ALL0.

## Abort message

XXX draft-09 doesn't define well.

## Abort Policy

the fragment receiver receives:

- a message of which the MIC is not matched third times.
- a message which is not of the maximum value of FCN. i.e. (2**fcn_size)-2.

