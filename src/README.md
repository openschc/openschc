
## example with the simulator

- No-ACK example

    % python test_newschc.py --data-file test/icmpv6.dmp

- ACK-on-Error example

    % python test_newschc.py --context example/context-100.json --rule-comp example/comp-rule-100.json --rule-fragin example/frag-rule-101.json --rule-fragout example/frag-rule-102.json --data-file test/icmpv6.dmp --loss-mode list --loss-param 1,2

## example with two gateways.

- ACK-on-Error with 

You need 3 terminals.

    % ./schcgw.py -c example/testgw2-config.json
    % ./schcgw.py -c example/testgw2-config.json
    % ./packet_picker.py --untrust -f test/icmpv6.dmp 'https://[::1]:51225/dl'

## create your certificates.

e.g. the below command will create a file named "testgw2-cert.pem"
containing the certificate and private key in PEM format for "testgw2".

    openssl req -new -x509 -newkey rsa:2048 -days 7300 -nodes \
        -out testgw2-cert.pem \
        -keyout testgw2-cert.pem \
        -subj "/CN=testgw2"

