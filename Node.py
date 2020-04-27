from numpy import inf
from math import sqrt, log1p
import random

class Node:

    def __init__(self, state, parent, action_from_parent):

        # Which state is this node representing
        self.state = state
        # Number of times this node is visited
        self.visit_count = 0
        # save parent amd action from parent
        self.parent = parent
        self.action_from_parent = action_from_parent
        # dictionary of children, where key is the action to get to child
        # TODO: Can be used to get legal actions
        self.children = {}
        # dictionary containing number of times actions has been taken from this state
        self.action_count = {}
        # dictionary saying how strong an action is from this state
        # if value is positive the action led to more victories for playe1
        # if value is negative the action led to more vicotries for player2
        self.action_value = {}

    def get_state(self):
        return self.state

    def get_visit_count(self):
        return self.visit_count

    def get_parent(self):
        return self.parent

    def add_child(self, action, child_node):
        self.children[action] = child_node
        self.action_count[action] = 0
        self.action_value[action] = 0

    def reset_node(self):
        self.children = {}
        self.action_count = {}
        self.action_value = {}
        self.parent = None
        self.visit_count = 0

    def get_child(self, action):
        return self.children[action]

    def num_children(self):
        return len(self.children)

    def increment_visit_count(self):
        self.visit_count +=1

    def increment_action_count(self, action):
        self.action_count[action] += 1

    def increment_action_value(self, action, value):
        self.action_value[action] += value

    def visit_count_distribution(self):
        s = sum(self.action_count.values())
        D = {action: count/s for action,count in self.action_count.items()}
        return D

    def get_values_with_bonus(self, exploration_bonus, strategy):
        if strategy == "max":
            actions = {action: (value/(1+self.action_count[action]))+self.get_exploration_bonus(action, exploration_bonus) for action,value in self.action_value.items()}
            best_value = max(actions.values())
            keys_with_best_value = []
            for key, value in actions.items():
                if value == best_value:
                    keys_with_best_value.append(key)
            return random.choice(keys_with_best_value)
        else:
            actions = {action: (value/(1+self.action_count[action])) - self.get_exploration_bonus(action, exploration_bonus) for action, value in self.action_value.items()}
            best_value = min(actions.values())
            keys_with_best_value = []
            for key, value in actions.items():
                if value == best_value:
                    keys_with_best_value.append(key)
            return random.choice(keys_with_best_value)


    def get_exploration_bonus(self, action, exploration_bonus):
        return exploration_bonus * sqrt(log1p(self.visit_count) / (1 + self.action_count[action]))


    def evaluate_actions(self, exploration_bonus):

        best_max_action = None
        best_max_value = -inf

        best_min_action = None
        best_min_value = inf

        for action, value in self.action_value.items():
            # print(action, value, self.visit_count)
            val_max = value + self.get_exploration_bonus(action, exploration_bonus)
            val_min = value - self.get_exploration_bonus(action, exploration_bonus)

            if val_max >= best_max_value:
                if val_max == best_max_value:
                    rand_n = random.randint(0,1)
                    best_max_value = val_max if rand_n == 0 else best_max_value
                    best_max_action = action if rand_n == 0 else best_max_action
                else:
                    best_max_value = val_max
                    best_max_action = action

            if val_min <= best_min_value:
                if val_min == best_min_value:
                    rand_n = random.randint(0, 1)
                    best_min_value = val_min if rand_n == 0 else best_min_value
                    best_min_action = action if rand_n == 0 else best_min_action

                else:
                    best_min_value = val_min
                    best_min_action = action

        return best_max_action, best_min_action
