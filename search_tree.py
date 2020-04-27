from Node import Node
import operator
import torch
import numpy as np
import random
class SearchTree:

    def __init__(self, initial_state, exploration_bonus):
        self.root = Node(state=initial_state, parent=None, action_from_parent = None)
        self.exploration_bonus = exploration_bonus

    def expand_tree(self, state_manager, node):
        legal_actions = state_manager.get_legal_actions()
        for action in legal_actions:
            succ_state = state_manager.get_succ_state(action)
            child = Node(state=succ_state, parent=node, action_from_parent = action)
            node.add_child(action, child)

    def reset_node(self):
        self.children = {}
        self.action_count = {}
        self.possible_value = {}


    def simulate_games_and_find_action(self, number_of_simulations, state_manager, anet):

        # expand search from root
        self.expand_tree(state_manager, self.root)

        strategy = state_manager.optimization_strategy

        for simulation in range(number_of_simulations):
            cloned_state_manager = state_manager.clone_state_manager()

            # run tree policy from current root to a leaf node
            leaf_node = self.tree_policy(self.root, cloned_state_manager)
            # if not leaf_node is a terminal state, aexpand the tree
            #if not(cloned_state_manager.is_winning_state(cloned_state_manager.last_player) or
            #                                        cloned_state_manager.is_terminal_state()):
            #    self.expand_tree(cloned_state_manager, leaf_node)


            random_exploratory = random.uniform(0,1)
            reward = self.default_policy(cloned_state_manager, anet, exploratory=random_exploratory)
            self.backprop(reward, leaf_node)


        # This is the distribution used for training the neural network
        action_D = self.root.visit_count_distribution()
        all_actions = state_manager.all_actions()

        for action in all_actions:
            if action not in action_D.keys():
                action_D[action] = 0.0

        sorted_action_D = {}
        for k in sorted(action_D):
            sorted_action_D[k] = action_D[k]


        target = list(sorted_action_D.values())
        max_index = target.index(max(target))
        # add to anet buffer
        player_id = state_manager.player_turn
        current_state = state_manager.get_current_state()
        current_state.append(player_id)

        anet.add_case_to_rbuf(current_state, target)


        #print("visit_count_distribution",sorted_action_D)
        #print("action_count:",self.root.action_count)
        #print("action_value:",self.root.action_value)

        best_action = max(sorted_action_D.items(), key=operator.itemgetter(1))[0]

        self.root = self.root.get_child(best_action)
        self.root.reset_node()
        return best_action



    def tree_policy(self, node, state_manager):
        current_node = node
        while current_node.num_children() != 0: # while not a leaf node
            # iterate down the tree
            best_action = current_node.get_values_with_bonus(self.exploration_bonus, state_manager.optimization_strategy)
            #best_actions= current_node.evaluate_actions(self.exploration_bonus)
            #best_action = best_actions[0] if state_manager.optimization_strategy=="max" else best_actions[1]
            # also make the copied statemanager run the action
            state_manager.take_action(best_action)
            next_node = current_node.get_child(best_action)
            current_node = next_node
        return current_node

    def default_policy(self, state_manager, anet, exploratory=0.0):
        if exploratory < 0.5:
            while state_manager.game_is_on():
                action = state_manager.get_random_action()
                state_manager.take_action(action)
            return state_manager.get_reward()
        else:
            while state_manager.game_is_on():

                # feed into the network
                player_id = state_manager.player_turn
                current_state = state_manager.get_current_state()
                current_state.append(player_id)
                state = torch.tensor([current_state]).float()
                mask = torch.tensor(state_manager.get_current_state_mask()).float()
               # print(state.shape)
               # print(mask.shape)

                anet_D = anet.forward(state)
                anet_D = anet_D.reshape((-1))


                legal_moves = (anet_D*mask).tolist()
                sum_legal_moves = sum(legal_moves)

                legal_moves = [d/sum_legal_moves for d in legal_moves]
                indexes = [x for x in range(len(legal_moves))]

                index_high = np.random.choice(indexes, p=legal_moves)

                # this index correspond to aciton
                action = state_manager.mapper.int_to_action[index_high]
                if action not in state_manager.get_legal_actions():
                    action = state_manager.get_random_action()
                state_manager.take_action(action)
            # when terminal state is reached, get the reward
            return state_manager.get_reward()

    def backprop(self, reward, leaf_node):

        child = leaf_node
        parent = leaf_node.get_parent()

        while not parent == None:

            action_from_parent = child.action_from_parent
            parent.increment_action_value(action_from_parent, reward)
            parent.increment_action_count(action_from_parent)
            child.increment_visit_count()

            child = parent
            parent = child.get_parent()
        child.increment_visit_count()