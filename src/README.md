Client-Server Simulation
========================

Introduction
------------

This first version consists of four new modules:

- ClientServerSimul.py
- ClientConnection.py
- ServerConnection.py
- ClientThread.py
- SchcConfig.py
- ClientSend.py

This second version implements the Socket library to perform the communication between a client and a server, using the localhost
address 127.0.0.1, port 1234, TCP protocol and threads on the server to allow communication **from several clients to a server**.

At the end of a successful communication, the simulation records the time in seconds at that instant in the text file
client_server_simulation.txt, and restarts sending the same message from the client to the server.

How to run this simulation
--------------------------

- Run Server

    ```
    python3 ClientServerSimul.py --role server
    ```

- Run Client

    ```
    python3 ClientServerSimul.py --role client
    ```

Rulemanager Test
=====================

## Example with the simulator

- First Rulemanager test

    ```
    python3 test_frag_new.py
    ```
## Example without the simulator

- First Rulemanager test

    ```
    python3 test_compress.py
    ```
Simulator
=========

## Example with the simulator

- No-ACK example

    ```
    python3 test_newschc.py --data-file test/icmpv6.dmp
    ```

- First ACK-on-Error example

    ```
    python3 test_newschc.py --context example/context-100.json --rule-comp example/comp-rule-100.json --rule-fragin example/frag-rule-101.json --rule-fragout example/frag-rule-102.json --data-file test/icmpv6.dmp --loss-mode list --loss-param 1,2
    ```

- Second ACK-on-Error example (example with everything in one file):

    ```
    python3 test_frag.py
    ```
- Third AC-on-Error example (statistics and packet loss included)

    ```
    python3 test_statsct.py
    ```

## How to check the F/R with unstable link.

You can define three mode of unstable link with the --loss-mode option.

- cycle: a frame will drop once in number times specified in the param. 

    e.g.
    
    ``` 
    --loss-mode cycle --loss-param 5     
    ```

    It causes a frame will drop once in 5 times.

- list: the frames specified in the param will be draopped. 

    e.g.
      
    ```
    --loss-mode list --loss-param 3,6
    ```

    It causes the 3th and 6th frames will drop.

- rate: the frames of the rate will be draopped. 
    
    e.g.

    ```
     --loss-mode rate --loss-param 10
    ```

    It causes the 10% framges will drop.

----

