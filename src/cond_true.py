"""
.. module:: comp_true 
   :platform: Python, Micropython
"""
from base_import import *

#---------------------------------------------------------------------------

def cond_random(rate):
    if sys.implementation.name == "micropython":
        #print("micropython")
        random_num = urandom.getrandbits(8)/256
        print("1000*random_num -> {} < 10 *rate  -> {}".format(random_num*1000,10*rate))
        #if random.randint(0,1000) <= (1000 * FER)
        #if random.randint(0,1000) <= FER_RANDOM * 10
        if random_num * 1000 < rate * 10:
        #if urandom.getrandbits(8)/256 * 100 < rate:
            return True
        else:
            return False
    else:
        random_num = random.random()
        print("random_num -> {}, rate -> {}".format(random_num,rate))
        return random_num < rate
        #return random.random() * 100 < rate

class ConditionalTrue:
    """ It returns True in a condition of 3 modes.
    """

    def __init__(self, mode="cycle", cycle=0, count_num=None):
        """
        mode: "list", "cycle", or "rate"

        list mode:
            count_num: a list of numbers of counter that return true.
            cycle: option.
        cycle mode:
            cycle: the cycle in which true is returned.
        rate mode:
            cycle: the rate in which true is returned.  i.e. 1 / cycle
        """
        self.count_in_cycle = 0
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
        else:
            raise ValueError("mode must be list, cycle, or rante.")

    def check(self):
        self.count_in_cycle += 1
        is_true = self.check_func()
        if self.count_in_cycle == self.cycle:
            self.count_in_cycle = 0
        return is_true

    def __cond_check_list(self):
        return self.count_in_cycle in self.count_num

    def __cond_check_cycle(self):
        if self.cycle == 0:
            return False
        return self.count_in_cycle % self.cycle == 0

    def __cond_check_rate(self):
        return cond_random(self.cycle)

if __name__ == "__main__":
    def test(config):
        print(config["cond"])
        cond = ConditionalTrue(**config["cond"])
        for i in range(1, 21):
            print(i, cond.check())

    test({ "cond": { "mode": "rate", "cycle": 5 } })
    test({ "cond": { "mode": "cycle", "cycle": 3 } })
    test({ "cond": { "mode": "list", "count_num": [ 2,3 ] } })
    test({ "cond": { "mode": "list", "count_num": [ 2,3 ], "cycle": 5 } })
    test({ "cond": { "mode": "rate", "cycle": 10 } })
#---------------------------------------------------------------------------
