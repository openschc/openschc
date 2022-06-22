# to save as a pcap: sudo tcpdump -i en0 -w test.pcap

# python3.9 -m pip install scapy
import os
os.sys.path.append('/usr/bin/')
from scapy.all import * 

import binascii



sequence = rdpcap("data.pcap")
ip_dns = 0
udp_dns = 0
data_dns = 0

for pkt in sequence:
    #hexdump(pkt)
    #pkt.show()

    if pkt.haslayer(IP):
#        print(pkt[IP].fields['src'], '--->', pkt[IP].fields['dst'])

        if pkt[IP].fields["proto"]  == 17:
#            print ("UDP")
            if pkt[UDP].fields["dport"] == 53:
#                print ("DNS")
#                pkt.show()

                ip_dns += pkt[IP].ihl*4
                udp_dns += 8
                data_dns += pkt[IP].len - (pkt[IP].ihl+2)*4

                print (ip_dns, udp_dns, data_dns, pkt[DNS].qd.qname)
        elif pkt[IP].fields["proto"] == 6:
            print ("TCP")
            if pkt[TCP].dport == 443 or pkt[TCP].sport == 443:
                if Raw in pkt:
                    tcp_data = bytes(pkt[Raw])
                    length = int.from_bytes(tcp_data[3:5], byteorder="big")
                    
                    print (pkt[TCP].sport, "-->", pkt[TCP].dport, ":", length)

    
