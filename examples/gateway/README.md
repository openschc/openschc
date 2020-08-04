SCHC Gateway Sample
===================

SCHC GW implementation.

schcgw.py is a translate a SCHC packet into an IP packet and vice versa.

packet_picker.py can be used to send a downlink packet.
It watches an interface.  And, if a packet is matched with the filter,
it submits the packet to the gateway.

## Requirement

- Python 3.7 or newer
- aiohttp
- [pypcap][https://github.com/pynetwork/pypcap#installation-from-sources]
- You may need to install libpcap.

packet_picker requires the requests.

## Preparation

export OPENSCHCDIR

```
export OPENSCHCDIR=<path_to_openschc_folder>
```

export PYTHONPATH

```
export PYTHONPATH=$OPENSCHCDIR/src:$PYTHONPATH
```

Create your certificates.

e.g. below command will create a file named "testgw2-cert.pem"
containing the certificate and private key in PEM format for "testgw2".

```
openssl req -new -x509 -newkey rsa:2048 -days 7300 -nodes \
    -out testgw2-cert.pem \
    -keyout testgw2-cert.pem \
    -subj "/CN=testgw2"
```

## Example with two gateways.

You need 3 terminals.  Run below command in each terminal of two.

At Terminal 1:
```
./schcgw.py -c testgw1-config.json -d
```

At Terminal 2:
```
./schcgw.py -c test/testgw2-config.json -d
```

In the remained terminal, you can choose:

- for No-ack

At Terminal 3:
```
./packet_picker.py --untrust 'https://[::1]:51225/dl' -f icmpv6-to-a234.dmp
```

- for ACK-on-Error

At Terminal 3:
```
./packet_picker.py --untrust 'https://[::1]:51225/dl' -f icmpv6-to-b234.dmp
```

## capture packets for downlink

You can use packet_picker.py to capture the packets to be sent to the network server.

The following command will captures the packet for 2405:6580:c740:1b00::0002 of the device address.

Example.

```
./packet_picker.py -i en0 https://localhost:51226/dl --untrust -d -F 'dst 2405:6580:c740:1b00::0002'
```

## REST interface for uplink.

Example.

```
curl -X POST -k -H 'Content-Type: text/json' -d '{"data":"60123456001e111efe800000000000000000000000000001fe80000000000000000000000000000216321633001e0000410200010ab3666f6f0362617206414243443d3d466b3d65746830ff8401822020264568656c6c6f","DevAddr":"0011223344"}' https://localhost:51226/up
```

---
Protocol
========

## From Non-LPWAN to LPWAN

End point: /dl

- Raw IP format

The content is hex string of IPv6 packet.

e.g.
```
Content-type: application/x-rawip-hex

6005b9b200103a40...(snip)...6578616d706c65
```

- JSON format

e.g.
```
content-type: text/json 

{ "hexIPData": "6005b9b200103a40...(snip)...6578616d706c65" }
```

## From LPWAN to Non-LPWAN

Assuming that a request comes from a NS adaptor.

End point: /ul

e.g.
```
content-type: text/json 

{
  "hexSCHCData": "6578616d706c65",
  "devL2Addr": "A2345678"
}
```

## From GW to NS adaptor

Assuming that a request goes into a NS adaptor.
It's same format to the one from LPWAN to Non-LPWAN.

e.g.
```
content-type: text/json 

{
  "hexSCHCData": "6578616d706c65",
  "devL2Addr": "A2345678"
}

---

Trouble Shooting
================

## BPF device, Permission denied.

```
OSError: Activateing packet capture failed. Error returned by packet capture library was b'(cannot open BPF device) /dev/bpf0: Permission denied'
```

It needs to add both read and write permission to the device,
which is /dev/bpf0 for example.

