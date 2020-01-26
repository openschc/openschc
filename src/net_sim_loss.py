"""
.. module:: comp_true 
   :platform: Python, Micropython
"""
from gen_base_import import *
from gen_utils import dprint

from stats.toa_calculator import get_toa
enable_statsct = True
if enable_statsct:
    from stats.statsct import Statsct
import math
#import machine

#---------------------------------------------------------------------------

def cond_random(rate): # XXX: simplify
    if sys.implementation.name == "micropython":
        #dprint("micropython")
        random_num = urandom.getrandbits(8)/256
        dprint("1000*random_num -> {} < 10 *rate  -> {}, Packet Loss Condition is -> {}".format(random_num*1000,10*rate,random_num * 1000 < rate * 10))
        #if random.randint(0,1000) <= (1000 * FER)
        #if random.randint(0,1000) <= FER_RANDOM * 10        
        #if urandom.getrandbits(8)/256 * 100 < rate:
        return random_num * 1000 < rate * 10
    else:
        random_num = random.getrandbits(8)/256
        dprint("1000*random_num -> {} < 10 *rate  -> {}, Packet Loss Condition is -> {}".format(random_num*1000,10*rate,random_num * 1000 < rate * 10))
        return random_num * 1000 < rate * 10


# XXX: if mode is "rate", another name than "cycle" should be used for rate

class PacketLossModel:
    """ It returns True in a condition of 3 modes.
    """

    def __init__(self, mode="cycle", cycle=0, count_num=None, G = None, background_frag_size = None):
        """
        mode: "list", "cycle", "rate" or "collision"

        list mode:
            count_num: a list of indices of lost packets, modulo `cycle`
        cycle mode:
            cycle: one packet is lost every `cycle` packets, the
            the last one in cycle. If `cycle` is 0, no packet is lost.
        rate mode:
            cycle: the rate in which true is returned. 
            i.e. % of losses Fragment Error Rate (e.g. 10 -> 10%)
        collision mode:
            G: percentage of occupation of the channel between 0 and 1
            background devices using the channel
        """
        self.background_traffic = []
        self.position = 0
        self.count_in_cycle = 0
        self.current_time =0
        if mode == "list":
            assert count_num is not None
            if cycle != 0 and cycle < max(count_num):
                raise ValueError("cycle is too small.")
            self.count_num = count_num
            self.cycle = cycle
            self.check_func = self.__cond_check_list
        elif mode == "cycle":
            assert cycle is not None
            self.cycle = cycle
            self.check_func = self.__cond_check_cycle
        elif mode == "rate":
            assert cycle is not None
            if cycle == 0:
                self.cycle = 1
            else:
                self.cycle = cycle
            self.check_func = self.__cond_check_rate
        elif mode == "collision":
            assert G is not None
            assert background_frag_size is not None
            self.cycle = 1
            self.G = G
            self.init_collision(G, background_frag_size)
            self.check_func = self.__cond_check_collision
            
        else:
            raise ValueError("mode must be list, cycle, or rate.")

    def init_collision(self,G, background_frag_size):
        """ Init the collision table"""
        if enable_statsct:
            if Statsct.get_background_traffic() is not None:
                self.background_traffic = Statsct.get_background_traffic()
            else:
                self.generate_background_traffic(G, background_frag_size)
            if Statsct.get_current_time is not None:
                self.current_time = Statsct.get_current_time()
            if Statsct.get_position is not None:
                self.position = Statsct.get_position()
        else:
            self.generate_background_traffic(G, background_frag_size)
        dprint("background_frag_size: {}".format(background_frag_size))
        #y = 0
        #calculate the background traffic, one packet each 5000ms of 500ms ToA
        #for i in range(10):
        #    self.background_traffic.append((y,y+500))
        #   y += 500000
        #The first fragment will be sent after a random time (10 seconds)
        #make sure the table is begin enough to transmitt the packet
        self.current_time = 10000 * urandom.getrandbits(8)/256
        input('')
 
    def generate_background_traffic(self, G, background_frag_size):
        self.background_traffic
        T = get_toa(background_frag_size, Statsct.SF)
        g = G / T['t_packet']
        dprint("g: {}, G:{}, T:{}".format(g,G,T['t_packet']))
        for i in range (1000):
            #aleatoire = machine.rng()
            #aleatoire2 = aleatoire/(2**24-1)
 
            aleatoire = urandom.getrandbits(8)/256
            aleatoire2 = aleatoire/(2**24-1)
            #dprint(aleatoire2)
            if aleatoire2 != 0:
                test = -1*math.log(aleatoire2) / 1/g
                self.background_traffic.append((test,test+T['t_packet']))
        if enable_statsct:
            Statsct.set_background_traffic(self.background_traffic)
            #print (tableau)
 
 
 
    def cond_collision(self, frag_size):
        """Calculates if there is a collision"""
        frag_ToA = get_toa(frag_size, Statsct.SF)
        #check if there is a collision at the start of the packet
        dprint("current time: {}, position: {}, ToA fragment: {}".format(self.current_time,self.position,frag_ToA['t_packet']))
        dprint("background_traffic: {}".format(self.background_traffic[self.position]))
        while self.position < len(self.background_traffic) and self.current_time > self.background_traffic[self.position][0]:           
            self.position += 1
        dprint("position: {}, ".format(self.position))
        
        if self.position != len(self.background_traffic):
            if self.current_time == self.background_traffic[self.position][0]:
                #special case when both packet start time is the same
                dprint("Collision! -> packet start at same time as the next")
                self.current_time += frag_ToA['t_packet'] + Statsct.dc_time_off(frag_ToA['t_packet'],Statsct.dc)
                return True
            elif self.position != 0 and self.current_time < self.background_traffic[self.position-1][1]:
                dprint("Collision! -> packet start before the end of previous packet")
                self.current_time += frag_ToA['t_packet'] + Statsct.dc_time_off(frag_ToA['t_packet'],Statsct.dc)
                return True
            else:
                if self.current_time + frag_ToA['t_packet'] > self.background_traffic[self.position][0]:
                    dprint("Collision!-> packet ends after next has start")
                    self.current_time += frag_ToA['t_packet'] + Statsct.dc_time_off(frag_ToA['t_packet'],Statsct.dc)
                    return True
        self.current_time += frag_ToA['t_packet'] + Statsct.dc_time_off(frag_ToA['t_packet'],Statsct.dc)
        input('')
        return False    

    def is_lost(self, packet_size):
        is_true = self.check_func(packet_size)
        self.count_in_cycle += 1
        if self.count_in_cycle == self.cycle:
            self.count_in_cycle = 0
        return is_true

    def __cond_check_list(self, packet_size=None):
        return self.count_in_cycle in self.count_num

    def __cond_check_cycle(self, packet_size=None):
        if self.cycle == 0:
            return False
        return self.count_in_cycle % self.cycle == 0

    def __cond_check_rate(self, packet_size=None):
        return cond_random(self.cycle)

    def __cond_check_collision(self, packet_size):
        return self.cond_collision(packet_size)

if __name__ == "__main__":
    packet_size = 10
    def test(config):
        print(config["cond"])
        loss_model = PacketLossModel(**config["cond"])
        for i in range(1, 21):
            print(i, loss_model.is_lost(packet_size))

    test({ "cond": { "mode": "rate", "cycle": 5 } })
    test({ "cond": { "mode": "cycle", "cycle": 3 } })
    test({ "cond": { "mode": "list", "count_num": [ 2,3 ] } })
    test({ "cond": { "mode": "list", "count_num": [ 2,3 ], "cycle": 5 } })
    test({ "cond": { "mode": "rate", "cycle": 10 } })
#---------------------------------------------------------------------------
