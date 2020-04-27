import copy
import random
from math import sqrt
class StateManager:

    def __init__(self, game, mapper,verbose = False):
        self.game = game
        self.verbose=verbose
        self.game.set_verbose(verbose)
        # player1: wants to maximize reward, player2: wants to minimize reward
        self.stats = {1: 0, 2: 0}
        self.player_turn = 1
        self.last_player = 1
        self.optimization_strategy = 'max'

        # need a way to map anet output to
        self.mapper = mapper



    def summary(self):
        num_games = sum(list(self.stats.values()))
        print()
        print("\t" + "Player1 win ratio: " +str(self.stats[1])+
              "/"+str(num_games)+" ("+str(round(self.stats[1]*100/num_games, 2)) +"%)")
        print("\t" + "Player2 win ratio: " + str(self.stats[2]) +
              "/" + str(num_games) + " ("+str(round(self.stats[2]*100/num_games, 2)) +"%)")
        print()

    def increment_stats(self, player):
        self.stats[player] +=1

    def all_actions(self):
        return self.game.all_moves()

    def get_current_player(self):
        return self.player_turn

    def get_current_state(self):
        return self.game.get_state()

    def get_current_state_mask(self):
        return self.game.get_state_mask()

    def get_succ_state(self, action):
        cloned_game = self.clone_game()
        cloned_game.set_verbose(False)

        cloned_game.take_action(action, self.player_turn)
        return cloned_game.get_state()

    def clone_game(self):
        # clone current game
        cloned_game = copy.deepcopy(self.game)
        cloned_game.set_verbose(False)
        return cloned_game

    def clone_state_manager(self):
        cloned_manager = copy.deepcopy(self)
        cloned_manager.game.set_verbose(False)
        cloned_manager.verbose = False
        return cloned_manager

    def get_legal_actions(self):
        return self.game.get_legal_actions()

    def get_random_action(self):
        return random.choice(self.get_legal_actions())

    def take_action(self, action):
        self.last_state = self.clone_game()
        self.game.take_action(action, player=self.player_turn)
        self.last_player = self.player_turn
        self.alternate_player()
        # change strategy
        self.optimization_strategy = "min" if self.optimization_strategy=="max" else "max"
        if self.verbose:
            s = "Player " + str(self.last_player) + " put a piece on " + str(action)
            self.game.draw_board(title=s)
            print(s)



    def alternate_player(self):
        if self.player_turn == 1:
            self.player_turn = 2
        else:
            self.player_turn = 1

    def is_winning_state(self, player):
        return self.game.is_winning_state(player)

    def is_terminal_state(self):
        return self.game.is_terminal_state()

    def game_is_on(self):
        if (self.is_winning_state(self.last_player) or self.is_terminal_state()):
            return False
        else: return True

    def get_reward(self):
        reward = 1
        punish = 0
        if self.is_winning_state(self.last_player):
            if self.verbose:
                print("Player", self.last_player, "won")
            return reward+punish if self.last_player == 1 else -reward-punish
        else:
            if self.verbose:
                print("Draw...")
            return 0

    def reset_game(self):
        self.game.reset_game()
        self.optimization_strategy = 'max'
        self.player_turn = 1
        self.last_player = 1