SCHC Gateway Sample
===================

SCHC GW implementation.

## Requirement

- Python 3.7
- requests
- aiohttp
- [pypcap][https://github.com/pynetwork/pypcap#installation-from-sources]
- You may need to install libpcap.

## export OPENSCHCDIR

`export OPENSCHCDIR=<path_to_openschc_folder>`

## export PYTHONPATH

`export PYTHONPATH=$OPENSCHCDIR/src:$PYTHONPATH`

## Example with two gateways.

- ACK-on-Error with 

You need 3 terminals.

```
./schcgw.py -c testgw1-config.json
./schcgw.py -c testgw2-config.json
./packet_picker.py --untrust -f icmpv6.dmp 'https://[::1]:51225/dl'
```

## 

```
curl -X POST -k -H 'Content-Type: application/json' -d '{"data":"60123456001e111efe800000000000000000000000000001fe80000000000000000000000000000216321633001e0000410200010ab3666f6f0362617206414243443d3d466b3d65746830ff8401822020264568656c6c6f","DevAddr":"0011223344"}' https://localhost:51226/dl
```

## Create your certificates.

e.g. the below command will create a file named "testgw2-cert.pem"
containing the certificate and private key in PEM format for "testgw2".
    
    openssl req -new -x509 -newkey rsa:2048 -days 7300 -nodes \
        -out testgw2-cert.pem \
        -keyout testgw2-cert.pem \
        -subj "/CN=testgw2"

---

Trouble Shooting
================

## BPF device, Permission denied.

```
OSError: Activateing packet capture failed. Error returned by packet capture library was b'(cannot open BPF device) /dev/bpf0: Permission denied'
```

It needs to add both read and write permission to the device,
which is /dev/bpf0 for example.

