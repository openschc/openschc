"""
statsct.py: Statistics Collector for openSCHC
Collects data related to: number of fragments in tx and rx, time on air, number of bytes per fragment
window size, tile size, size of the acks
Centralize the information for analysis
The stats are write to a file
"""
#import collections.defaultdict as defaultdict
from collections import defaultdict
from base_import import *  # used for now for differing modules in py/upy
import utime
import sys
from .toa_calculator import get_toa

class Statsct(object):
    src_id = None
    dst_id = None
    results = dict()
    sender_packets = dict()
    receiver_packets = dict()
    SF = 8

    @staticmethod
    def initialize():
        """Class to initializa the static class
        creates the file to write and the instance of the class """
        print('Init statsct module')
        Statsct.results['init_time'] = utime.time()
        Statsct.results['packet_list'] = []
        Statsct.sender_packets['packet_list'] = []
        Statsct.receiver_packets['packet_list'] = []
    @staticmethod
    def log(message):
        print("[statsct] "+ message)
    
    @staticmethod
    def setSourceAddress(schcSenderAddress):
        """Set the source address in the results dict
        :param schcSenderAddress: Address of the sender """
        Statsct.src_id = schcSenderAddress
        print("src_id -> {}".format(Statsct.src_id))
        Statsct.results['src_id'] = Statsct.src_id
        print(str(Statsct.results))


    @staticmethod
    def setDestinationAddress(schcDestinationAddress):
        """Set the destination address in the results dict
        :param schcDestinationAddress: Address of the receiver"""
        Statsct.dst_id = schcDestinationAddress
        print("dst_id -> {}".format(Statsct.dst_id))
        Statsct.results['dst_id'] = Statsct.dst_id 
        print(str(Statsct.results))
 

    @staticmethod    
    def addInfo(key, value):
        print("{}, {}".format(key,value))
        Statsct.results[key] = value
        print(str(Statsct.results))
        

    @staticmethod
    def print_results():
        print("Results")
        for key in Statsct.results:
            print("{}, {}".format(key,Statsct.results[key]))
        print("sender_packets")
        for key in Statsct.sender_packets:
            print("{}, {}".format(key,Statsct.sender_packets[key]))
        print("receiver_packets")
        for key in Statsct.receiver_packets:
            print("{}, {}".format(key,Statsct.receiver_packets[key]))
    
    @staticmethod
    def add_packet_info(packet,src_dev_id,dst_dev_id, status):
        """ Add the information of the packet to the results dict 
        :param packet: packet send
        :param src_dev_id: device source id
        :param dst_dev_id: device destination id
        :param status: if the message was send successful (True) or not (False) """
        packet_info = dict()
        packet_info['time'] = utime.time()
        packet_info['src_dev_id'] = src_dev_id
        packet_info['dst_dev_id'] = dst_dev_id
        packet_info['packet'] = packet
        packet_info['status'] = status
        packet_info['packet_length'] = len(packet)
        packet_info['toa_calculator'] = get_toa(len(packet), Statsct.SF)
        packet_info['toa_packet'] = packet_info['toa_calculator']['t_packet'] 
        print(packet_info)
        Statsct.results['packet_list'].append(packet_info)
        print(str(Statsct.results))
        if src_dev_id == Statsct.src_id:
            Statsct.sender_packets['packet_list'].append(packet_info)
            print(Statsct.sender_packets)
        else:
            Statsct.receiver_packets['packet_list'].append(packet_info)
            print(Statsct.receiver_packets)



    # @staticmethod
    # def log(self, name, message):
    #     self.system.log(name, message)
