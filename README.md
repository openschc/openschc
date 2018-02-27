SCHC test
==========

An test implementation of LPWAN Static Context Header Compression (SCHC).

This is developed based on the SCHC draft-09.
Because the draft status is in progress.
Therefore, the unclear parts are implemented by my own understanding.

To understand this implementaion detail, see IMPLEMENTATION.md.

## Requirement

- python3 is required. not tested on python2.

This software is expected to run on MicroPython.
Only premitive python packageare is used
so that this software can work on pycom.

## TODO

- bitmap optimization is not implemented.

## How to get

some modules are included.  therefore, you need to clone recursively.

    git clone --recursive git://github.com/tanupoo/schc-fragment.git

or

    git clone git://github.com/tanupoo/schc-fragment.git
    cd schc-fragment
    git submodule update --init --recursive

## How to run

test-client-udp.py is a sample code for the fragment sender.
test-server-udp.py is for the fragment receiver.

You should prepare two consoles.

One is for the sender.

    ./test-client-udp.py 127.0.0.1 9999

The other is for the receiver.

    ./test-server-udp.py 9999

If you use the -d option, you can see many messages.
-dd or -ddd increase more.

### test-client

    usage: test-client-udp.py [-h] [-I MSG_FILE] [--interval INTERVAL]
                              [--timeout TIMEOUT] [--l2-size L2_SIZE]
                              [--rid RULE_ID] [--dtag DTAG]
                              [--loss-list LOSS_LIST] [--loss-rate LOSS_RATE]
                              [--loss-random] [-v] [-d] [--verbose]
                              [--debug DEBUG_LEVEL] [--version]
                              SERVER PORT
    
    a sample code for the fragment sender.
    
    positional arguments:
      SERVER                specify the ip address of the server.
      PORT                  specify the port number in the server.
    
    optional arguments:
      -h, --help            show this help message and exit
      -I MSG_FILE           NOTYET, specify the file name containing the message,
                            default is stdin.
      --interval INTERVAL   specify the interval for each sending.
      --timeout TIMEOUT     specify the number of time to wait for ACK.
      --l2-size L2_SIZE     specify the payload size of L2. default is 8.
      --rid RULE_ID         specify the rule id. default is 1
      --dtag DTAG           specify the DTag. default is 1
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

    usage: test-server-udp.py [-h] [--address SERVER_ADDRESS] [--timer TIMER_T1]
                              [--timer-t3 TIMER_T3] [--timer-t4 TIMER_T4]
                              [--timer-t5 TIMER_T5] [-v] [-d] [--verbose]
                              [--debug _DEBUG_LEVEL] [--version]
                              PORT
    
    a sample code for the fragment receiver.
    
    positional arguments:
      PORT                  specify the port number in the server.
    
    optional arguments:
      -h, --help            show this help message and exit
      --address SERVER_ADDRESS
                            specify the ip address of the server to be bind.
                            default is any.
      --timer TIMER_T1      specify the number of time to wait for messages.
      --timer-t3 TIMER_T3   specify the number of time to wait for messages.
      --timer-t4 TIMER_T4   specify the number of time to wait for messages.
      --timer-t5 TIMER_T5   specify the number of time to wait for messages.
      -v                    enable verbose mode.
      -d                    increase debug mode.
      --verbose             enable verbose mode.
      --debug _DEBUG_LEVEL  specify a debug level.
      --version             show program's version number and exit

