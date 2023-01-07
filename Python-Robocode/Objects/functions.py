import torch
import numpy as np



# functions that map values to probabilities

def linear_dist(values: np.ndarray, min_possible: float = 0) -> np.ndarray:
    values = values - min_possible
    return values / values.sum()

def softmax(values: np.ndarray) -> np.ndarray:
    values = values - values.min()
    exps = np.exp(values)
    return exps / exps.sum()

def hardmax(values: np.ndarray, T: float) -> np.ndarray:
    if np.all(values == values[0]): 
        return softmax(values)
    values = values - values.min()
    values = values / values.max()
    values = values * T
    return softmax(values)


# tensor functions

def exptuples2tensors(exp_tuples, device):
    states, actions, rewards, next_states, dones = [], [], [], [], []
    
    for exp in exp_tuples:
        states.append(exp[0])
        actions.append(exp[1])
        rewards.append(exp[2])
        next_states.append(exp[3])
        dones.append(exp[4])
    
    states = torch.FloatTensor(np.array(states, copy=False, dtype=np.float64)).to(device)
    actions = torch.LongTensor(np.array(actions, copy=False, dtype=np.int64)).to(device)
    rewards = torch.FloatTensor(np.array(rewards, copy=False, dtype=np.float64)).to(device)
    next_states = torch.FloatTensor(np.array(next_states, copy=False, dtype=np.float64)).to(device)
    dones = torch.BoolTensor(np.array(dones, copy=False, dtype=bool)).to(device)
    
    return states, actions, rewards, next_states, dones


# misc

def rollavg(a: np.ndarray, n: int = 21) -> np.ndarray:
    """ Rolling average
    Args:
        a (np.ndarray): array of values
        n (int, optional): window length (should be odd). Defaults to 21.
    Returns:
        np.ndarray: array with averaged values
    """
    if n%2 == 0: n += 1
    N = len(a)
    cumsum_vec = np.cumsum(np.insert(np.pad(a,(n-1,n-1),'constant'), 0, 0)) 
    d = np.hstack((np.arange(n//2+1,n),np.ones(N-n)*n,np.arange(n,n//2,-1)))  
    return (cumsum_vec[n+n//2:-n//2+1] - cumsum_vec[n//2:-n-n//2]) / d