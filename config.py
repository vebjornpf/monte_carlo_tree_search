import torch

# HEX
BOARD_SIZE = 6

FOLDER_RESULTS = "boardsize_6_700_0.0007"

VISUALIZE_MOVES = False
NUM_EPISODES = 2000
NUM_SIMULATIONS = 700
EXPLORATION_BONUS = 1.5
SAVE_EVERY = 50

HIDDEN_LAYERS = [96, 96]
LEARNING_RATE = 0.0007
ACTIVATION = 'relu'  #'sigmoid', 'tanh', 'relu', 'linaer'
OPTIMIZER = 'adam'  #adagrad, sgd, rmsprop, 'adam'

REPLAY_BUFFER_MAX_SIZE = 2000
REPLAY_BUFFER_MINIBATCH_SIZE = 64

M_GAMES_TO_PLAY_IN_TOPP = 100

ACTIVATIONS = {
    'linear': torch.nn.Identity,
    'sigmoid': torch.nn.Sigmoid,
    'tanh': torch.nn.Tanh,
    'relu': torch.nn.ReLU
}

OPTIMIZERS = {
    'adam': torch.optim.Adam,
    'sgd': torch.optim.SGD,
    'adagrad': torch.optim.Adagrad,
    'rmsprop': torch.optim.RMSprop
}
