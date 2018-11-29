#---------------------------------------------------------------------------

from random import random

#---------------------------------------------------------------------------

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
                self.cycle = 1 / cycle
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
        return random() < self.cycle

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

#---------------------------------------------------------------------------
