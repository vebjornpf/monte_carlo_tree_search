import config
import torch.nn as nn                     # neural networks
import torch.nn.functional as F           # layers, activations and more
import random
import torch

class ANET_NN_GENERAL(nn.Module):

    def __init__(self, input_size, output_size, hidden_layers, activation, name=None):
        super(ANET_NN_GENERAL, self).__init__()

        self.name =name
        self.input_size = input_size
        self.output_size = output_size

        modules = []

        # add input layer
        modules.append(nn.Linear(self.input_size+1, hidden_layers[0]))
        modules.append(config.ACTIVATIONS[activation]())

        for l in range(0, len(hidden_layers) - 1):
            modules.append(nn.Linear(hidden_layers[l], hidden_layers[l+1]))
            modules.append(config.ACTIVATIONS[activation]())

        modules.append(torch.nn.Linear(hidden_layers[-1], output_size))

        self.net = nn.Sequential(*modules)

    def forward(self, x):
        x = self.net(x)
        D = F.softmax(x, dim=1)
        return D


class ANET_NN_SIMPLE(nn.Module):

    def __init__(self, input_size, output_size, name=None):
        super(ANET_NN_SIMPLE, self).__init__()

        self.name = name

        self.input_size = input_size
        self.output_size = output_size

        # +1 represent player id
        self.fc1 = nn.Linear(input_size+1, 64)
        self.fc2 = nn.Linear(64, 64)

        self.out = nn.Linear(64, self.output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = ((self.out(x)))
        D = F.softmax(x, dim=1)
        return D

class ANET_NN_COMPLEX(nn.Module):

    def __init__(self, input_size, output_size, name=None):
        super(ANET_NN_COMPLEX, self).__init__()
        self.name = name
        self.input_size = input_size
        self.output_size = output_size

        # +1 represent player id
        self.fc1 = nn.Linear(input_size+1, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 128)
        self.fc4 = nn.Linear(128, 64)
        self.out = nn.Linear(64, self.output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = ((self.out(x)))
        D = F.softmax(x, dim=1)
        return D

class ANET_MODEL:

    def __init__(self, anet_model, max_cases_in_buffer = 1000):
        self.model = anet_model
        self.rbuf_old_features = []
        self.rbuf_old_targets = []

        self.rbuf_new_features = []
        self.rbuf_new_targets = []

        self.seen_state = {}

        self.max_cases = max_cases_in_buffer

    def add_case_to_rbuf(self, feature, target):
        self.rbuf_new_features.append(feature)
        self.rbuf_new_targets.append(target)

    def reset_rbuf(self):
        # add new data to old buffer
        self.rbuf_old_features += self.rbuf_new_features
        self.rbuf_old_targets += self.rbuf_new_targets

        if len(self.rbuf_old_targets) > self.max_cases:
            number_to_remove = len(self.rbuf_old_targets)-self.max_cases
            self.rbuf_old_features = self.rbuf_old_features[number_to_remove:]
            self.rbuf_old_targets = self.rbuf_old_targets[number_to_remove:]
        # reset new buffer
        self.rbuf_new_features = []
        self.rbuf_new_targets = []

    def forward(self, x):
        x = self.model(x)
        return x

    def train_model(self, optimizer, criterion=None, minibatch_size = 64):
        if len(self.rbuf_new_targets) + len(self.rbuf_old_targets) >= minibatch_size:
            num_from_old_buffer = minibatch_size - len(self.rbuf_new_targets)
            random_indexes = random.sample(range(0, len(self.rbuf_old_targets)), num_from_old_buffer)
            features = self.rbuf_new_features + [self.rbuf_old_features[i] for i in random_indexes]
            targets = self.rbuf_new_targets + [self.rbuf_old_targets[i] for i in random_indexes]
            self.model.train()
            optimizer.zero_grad()
            features = torch.tensor(features).float()
            targets = torch.tensor(targets).float()

            for x in range(1):
                for r in range(len(targets)):
                    feature = features[r].reshape((1,-1))
                    feature.requires_grad = True
                    """
                    feature_str = str(feature.tolist())
                    if feature_str not in self.seen_state:
                        self.seen_state[feature_str] = 0
                    else:
                        self.seen_state[feature_str] += 1
                    """
                    target = targets[r].reshape((1,-1))
                    pred = self.model(feature)
                    loss = self.cross_entropy(pred, target)
                    loss.backward()
                    optimizer.step()
            self.model.eval()

    def cross_entropy(self,pred, soft_targets):
        logsoftmax = nn.LogSoftmax(dim=1)
        return torch.mean(torch.sum(- soft_targets * logsoftmax(pred), 1))