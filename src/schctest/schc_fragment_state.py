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
            return "state: %s -> %s" % (s1.name, s2.name)
        elif s2 != None:
            return "state: None -> %s" % s2.name
        elif s1 != None:
            return "state=%s" % s1.name
        else:
            return self.state.name

    def set(self, new_state):
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
    import micro_enum
    state = micro_enum.enum(
        A = 1,
        B = 2,
        C = 3,
        Z = -1
        )
    print("%s"%state.A)
    s = fragment_state(state, logger=print)
    s.set(state.A)
    s.set(state.B)
    s.set(state.C)
    print(s.pprint(state.B, state.Z))
    print(s.pprint())

