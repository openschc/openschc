
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

