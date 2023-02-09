
STATE_END = "END"

# TODO: handle action case-insensitive


class SsmAction:

    # do() is always executed before goto()
    # several do() chained ?

    def __init__(self, name):
        self.name = name
        self.methods = []   # do()
        self.state = None   # goto()

    def do(self, method):
        self.methods.append(method)
        return self

    def goto(self, state):
        self.state = state
        return self

    def execute_all(self):
        new_state = None
        for m in self.methods:
            new_state = m(self.name)
        if new_state:
            return new_state
        else:
            return self.state


class SsmState:

    def __init__(self, name):
        self.name = name
        self.actions = {}
        self._cur_act = None

    def when(self, action):
        if action not in self.actions:
            self.actions[action] = SsmAction(action)
        self._cur_act = action
        return self

    def do(self, method):
        self.actions[self._cur_act].do(method)
        return self

    def goto(self, state, enter_state_method=None):
        if enter_state_method:
            self.actions[self._cur_act].do(enter_state_method)
        self.actions[self._cur_act].goto(state)
        return self

    def execute_action(self, action):
        """returns the next state if the action is goto()"""
        if action not in self.actions:
            # print("execute_action action not found in current state", action)
            return
        # the called method is passed the action, so the method can react differently depending on the action
        s = self.actions[action].execute_all()
        return s


class SimpleStateMachine:

    def __init__(self):
        self.action = None
        self._state = None
        self.states = {}

    def state(self, state):
        if state not in self.states:
            self.states[state] = SsmState(state)
        return self.states[state]

    def any_state(self):
        if "ANY" not in self.states:
            self.states["ANY"] = SsmState("ANY")
        return self.states["ANY"]

    def in_state(self, state):
        return state == self._state

    def get_state(self):
        return self._state

    def do_action(self, action):
        self.action = action

    def start(self, state):
        if state not in self.states:
            # TODO: throw exception
            return
        self._state = state

    def execute(self):
        if self.action:
            if self._state == STATE_END:
                return
            if "ANY" in self.states:
                print("execute ANY", self.action)
                self.states["ANY"].execute_action(self.action)
            if self._state in self.states:
                next_state = self.states[self._state].execute_action(self.action)
                if next_state:
                    self._state = next_state
            # elif "ANY" in self.states:
            #     print("execute ANY", self.action)
            #     self.states["ANY"].execute_action(self.action)
            self.action = None