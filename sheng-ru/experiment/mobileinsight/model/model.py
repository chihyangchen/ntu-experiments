import torch
from torch import nn

class RNN_Classifier(nn.Module):
  
    def __init__(self, num_layers, input_size, hidden_size, num_classes=2, rnn='LSTM'):
        super().__init__()
        self.input_size = input_size
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.num_classes = num_classes

        # input_size: num of features; hidden_size: num of hidden state h
        # num_layers: number of recurrent layer, i.e. seq; batch_first: batch first than seq
        if rnn == 'LSTM':
            self.rnn= nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        elif rnn == 'GRU':
            self.rnn= nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, 1) # For binary classification


    def forward(self,batch_input):
        out,_ = self.rnn(batch_input)
        out = self.linear(out[:,-1, :]).squeeze()  #Extract outout of lasttime step (N, L, Hout) -> (Batch, time_seq, output)
        out = torch.sigmoid(out) # Binary Classifier

        return out

class RNN_Regression(nn.Module):

    def __init__(self, num_layers, input_size, hidden_size, label_dim, rnn='LSTM'):
        super().__init__()
        self.input_size = input_size
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.label_dim = label_dim

        # input_size: num of features; hidden_size: num of hidden state h
        # num_layers: number of recurrent layer, i.e. seq; batch_first: batch first than seq
        if rnn == 'LSTM':
            self.rnn= nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        elif rnn == 'GRU':
            self.rnn= nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, label_dim)

    def forward(self,batch_input):
        out,_ = self.rnn(batch_input)
        out = self.linear(out[:,-1, :]).squeeze()  #Extract outout of lasttime step (N, L, Hout) -> (Batch, time_seq, output)

        return out
        
class RNN_Forecaster(nn.Module):
  
    def __init__(self, num_layers, input_size, hidden_size, dropout, num_classes=2, rnn='LSTM'):
        
        super().__init__()
        self.input_size = input_size
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.num_classes = num_classes

        # input_size: num of features; hidden_size: num of hidden state h
        # num_layers: number of recurrent layer, i.e. seq; batch_first: batch first than seq
        if rnn == 'LSTM':
            self.rnn= nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        elif rnn == 'GRU':
            self.rnn= nn.GRU(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.linear = nn.Linear(hidden_size, num_classes) # For binary classification

    def forward(self,batch_input):
        
        out,_ = self.rnn(batch_input)
        out = self.linear(out[:,-1, :]).squeeze()  #Extract out of lasttime step (N, L, Hout) -> (Batch, time_seq, output)

        return out
