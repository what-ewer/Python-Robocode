import torch
import torch.nn as nn
import torch.nn.functional as F



class FCDQN(nn.Module):
    """ Fully Connected Deep Q-Network"""
    
    def __init__(self, input_size, output_size, hidden_sizes, **kw):
        super().__init__()
        
        if len(hidden_sizes) < 1:
            raise ValueError("No hidden layers given.")
        
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(input_size, hidden_sizes[0]))
        for i in range(len(hidden_sizes)-1):
            self.layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i+1]))
        self.layers.append(nn.Linear(hidden_sizes[-1], output_size))

        self._hp = {
            'name': self.__class__.__name__,
            'input_size': input_size,
            'output_size': output_size,
            'hidden_sizes': hidden_sizes
        }
        
    
    def forward(self, x):
        for i in range(len(self.layers)-1):
            x = F.relu(self.layers[i](x))
        out = self.layers[-1](x)
        return out


    def hiperparams(self):
        return self._hp



if __name__=='__main__':
    dqn = FCDQN(2,4,hidden_sizes=[8])
    print(dqn(torch.rand(size=(2,))))
    print(dqn.hiperparams())