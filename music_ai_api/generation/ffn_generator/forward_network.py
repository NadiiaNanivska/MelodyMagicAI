import torch
import torch.nn as nn
import torch.nn.functional as F
import utils.ffn_utils.constants as constants

class ForwardNetwork(nn.Module):
    def __init__(self):
        super(ForwardNetwork, self).__init__()

        self.input = nn.Linear(constants.SEQUENCE_LENGTH * 22, 128)
        self.bn1 = nn.BatchNorm1d(128)

        self.hidden1 = nn.Linear(128, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.activation = nn.ELU()
        self.dropout1 = nn.Dropout(0.35)

        self.hidden2 = nn.Linear(128, 128)
        self.dropout2 = nn.Dropout(0.35)

        self.forward_alto = nn.Linear(128, constants.SEQUENCE_LENGTH * 22)
        self.forward_tenor = nn.Linear(128, constants.SEQUENCE_LENGTH * 22)
        self.forward_bass = nn.Linear(128, constants.SEQUENCE_LENGTH * 29)

        self.apply(self.init_weights)

    def init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            nn.init.zeros_(m.bias)

    def forward(self, x):
        x = torch.flatten(x, start_dim=1)

        x = self.input(x)
        x = self.bn1(x)
        x = self.activation(x)
        x = self.dropout1(x)

        x = self.hidden1(x)
        x = self.bn2(x)
        x = self.activation(x)
        x = self.dropout1(x)

        x = self.hidden2(x)
        x = self.activation(x)
        x = self.dropout2(x)

        x_alto = F.log_softmax(self.forward_alto(x).reshape(constants.BATCH_SIZE, 22, constants.SEQUENCE_LENGTH), dim=1)
        x_tenor = F.log_softmax(self.forward_tenor(x).reshape(constants.BATCH_SIZE, 22, constants.SEQUENCE_LENGTH), dim=1)
        x_bass = F.log_softmax(self.forward_bass(x).reshape(constants.BATCH_SIZE, 29, constants.SEQUENCE_LENGTH), dim=1)

        return x_alto, x_tenor, x_bass