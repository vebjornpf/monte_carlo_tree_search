from HexBoard import HexBoard
from StateManager import StateManager
from Mapper import Mapper
from anet import ANET_MODEL, ANET_NN_COMPLEX, ANET_NN_SIMPLE, ANET_NN_GENERAL
from search_tree import SearchTree
import config
import utils

import time
import random
import torch




if __name__ == "__main__":
    board_size = config.BOARD_SIZE
    exploration_bonus = config.EXPLORATION_BONUS
    num_simulations = config.NUM_SIMULATIONS
    num_episodes = config.NUM_EPISODES
    save_every = config.SAVE_EVERY
    folder_results = config.FOLDER_RESULTS
    lr = config.LEARNING_RATE

    utils.create_directory(folder_results)

    time_start = time.time()
    board = HexBoard(board_size)
    mapper = Mapper(board_size = board_size)
    state_manager = StateManager(board,mapper, verbose=config.VISUALIZE_MOVES)

    #anet_nn = ANET_NN_COMPLEX(input_size=board_size*board_size, output_size = board_size*board_size).float()
    anet_nn = ANET_NN_GENERAL(input_size = board_size*board_size, output_size = board_size*board_size,
                              hidden_layers=config.HIDDEN_LAYERS, activation = config.ACTIVATION) .float()

    anet = ANET_MODEL(anet_nn, max_cases_in_buffer = config.REPLAY_BUFFER_MAX_SIZE)
    optimizer = config.OPTIMIZERS[config.OPTIMIZER](anet_nn.parameters(), lr=lr)

    for episode in range(num_episodes):
        while state_manager.game_is_on():
            random_number = random.uniform(0, 1)
            if random_number < 0.3:
                action = state_manager.get_random_action()
            else:
                search_tree = SearchTree(state_manager.get_current_state(), exploration_bonus)
                action = search_tree.simulate_games_and_find_action(num_simulations, state_manager, anet)
            state_manager.take_action(action)


        # --------- LOGGING THE TIME MODELS USE TO RAIN --------------
        time_finished = time.time()
        time_passed = str(round((time_finished - time_start) / 60, 2))

        log_string = l = str(episode) + " of " + str(
            num_episodes) + " finished. TIME PASSED (minutes): " + time_passed
        utils.logging(folder_results, log_string)
        # ------------------------------------------------------------

        anet.train_model(optimizer, minibatch_size = config.REPLAY_BUFFER_MINIBATCH_SIZE)
        anet.reset_rbuf()

        if episode % save_every == 0:
            torch.save(anet_nn.state_dict(), folder_results+ "/model_" + str(episode)+".pt")

        reward = state_manager.get_reward()

        if reward != 0:
            state_manager.increment_stats(state_manager.last_player)
        state_manager.reset_game()