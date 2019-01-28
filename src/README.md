
## example

- No-ACK example

% python3 test_newschc.py --data-file test/icmpv6.dmp

- ACK-on-Error example

% python3 test_newschc.py --context example/context-100.json --rule-comp example/comp-rule-100.json --rule-fragin example/frag-rule-101.json --rule-fragout example/frag-rule-102.json --data-file test/icmpv6.dmp --loss-mode list --loss-param 1,2

- Same example, but with everything in one file:

% python3 test_frag.py
