
def default_logger(*arg):
    pass

class fragment_state:

    '''
    state_dict: state dict.  e.g. { "state_name": state, ... }
        both state_name and state must be unique.
    '''
    def __init__(self, state_dict, logger=default_logger):
        self.state_dict = state_dict
        self.logger = logger
        self.state = None
        self.state_prev = None

    def pprint(self, s1=None, s2=None):
        if s1 != None and s2 != None:
            return "state: %s -> %s" % (self.resolv(s1), self.resolv(s2))
        elif s2 != None:
            return "state: None -> %s" % self.resolv(s2)
        elif s1 != None:
            return "state=%s" % self.resolv(s1)
        else:
            return self.resolv(self.state)

    def resolv(self, state):
        '''
        resolv the state_name by the state.
        '''
        for k,v in self.state_dict.items():
            if v == state:
                return k
        return None

    def set(self, new_state=None, new_name=None):
        if new_state == None and new_name != None:
            new_state = self.state_dict[new_name]
        if self.state != new_state:
            # if the state is not changed, do nothing.
            self.state_prev = self.state
            self.state = new_state
            self.logger(1, self.pprint(self.state_prev, self.state))
        return self.state

    def back(self):
        self.state = self.state_prev
        self.state_prev = None
        self.logger(1, self.pprint(self.state, self.state_prev))
        return self.state

    def get(self):
        return self.state

    def get_prev(self):
        return self.state_prev

if __name__ == "__main__" :
    state_dict = {"A":0, "B":1, "C":2, "Z":99}
    s = fragment_state(state_dict, logger=print)
    s.set(new_name="A")
    s.set(1)
    s.set(2)
    print(s.pprint(2, 99))
    print(s.pprint())

