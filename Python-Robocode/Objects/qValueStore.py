import torch
import torch.nn as nn

import json
import time
import numpy as np

from pathlib import Path

from nnmodels import FCDQN
from functions import hardmax, rollavg, exptuples2tensors


np.random.seed(7)
torch.manual_seed(7)


GAMMA = 0.5
DEVICE = "cpu"
BATCH_SIZE = 32

# Qnet params
NUM_ACTIONS = 14
NET_CLASS = FCDQN
NET_PARAMS = {
    'output_size': NUM_ACTIONS,
    'hidden_sizes': [64]
}
OPTIMIZER_CLASS = torch.optim.Adam
OPTIMIZER_PARAMS = {
    'lr': 0.3, 
    # 'alpha': 0.95, 
    # 'momentum': 0.95, 
    # 'eps': 0.01
}
QNET_CHECKPOINT_FREQ = 1000

LOSS_CLASS = nn.HuberLoss

START_TIME = int(time.time())
MODEL_DIR = Path(f'saved_models/{START_TIME}')
MODEL_DIR.mkdir(parents=True, exist_ok=True)
(MODEL_DIR / 'checkpoints').mkdir(parents=True, exist_ok=True)
print(MODEL_DIR.absolute())


STATE_SHAPE = 9


def map2prob(qvalues: np.ndarray) -> np.ndarray:
    return hardmax(values=qvalues, T=10)

class QValueStore():

    def __init__(self):
        self.buildModel()

    def buildModel(self,):
        self.Qnet = NET_CLASS(input_size=STATE_SHAPE, **NET_PARAMS).to(DEVICE)
        self.optimizer = OPTIMIZER_CLASS(params=self.Qnet.parameters(), **OPTIMIZER_PARAMS)
        self.loss = LOSS_CLASS()

    def loadModel(self, model_name :str):
        #TODO
        pass


    def update(self, aggregate_data):
            
        self.optimizer.zero_grad()

        _states, _actions, _rewards, _next_states, _dones = exptuples2tensors(exp_tuples=aggregate_data, device=DEVICE)
        
        _qvalues_all = self.Qnet(_states)

        subaction_ranges = [0,3,6,9,12,14]

        with torch.no_grad():
            _qvalues_next_all = self.Qnet(_next_states)

        losses = []
        for i in range(_actions.shape[1]):
            _action = _actions[:,i]

            _qvalues_actions = _qvalues_all[np.arange(_actions.shape[0]), _action]
            with torch.no_grad():
                ss = subaction_ranges[i-1]
                se = subaction_ranges[i]
                _qvalues_next_max = torch.max(_qvalues_next_all[:,ss:se], axis=1)[0]
                _qvalues_next_max[_dones] = 0

                _qvalues_expected = _rewards + GAMMA * _qvalues_next_max
            
            _loss = self.loss(_qvalues_expected, _qvalues_actions)
            losses.append(_loss)
        _losses = torch.sum(losses)
        _losses.backward()
        self.optimizer.step()


    def get_q(self,state):
        with torch.no_grad():
            qvalues = self.Qnet(torch.Tensor(state).to(DEVICE)).numpy()
            # p = map2prob(qvalues=qvalues)
        return qvalues

        
                    
            
    


# -------------------------------------------------------------------------------------
# saving


# avg_episode_loss = avg_episode_loss[:episode]
# run_episode_length = run_episode_length[:episode]
# avg_episode_reward = avg_episode_reward[:episode]


# hiperparams = {
#     'environment': env.__class__.__name__,
#     'algorithm': 'ddql_rb',
#     'num_episodes': NUM_EPISODES,
#     'batch_size': BATCH_SIZE,
#     'gamma': GAMMA,
#     'device': DEVICE
# }
# hiperparams['model'] = Qnet.hiperparams()
# hiperparams['optimizer'] = {
#     'name': optimizer.__class__.__name__, 
#     'params': OPTIMIZER_PARAMS
# }
# hiperparams['loss'] = loss.__class__.__name__

# hiperparams["learning_duration [s]"] = int(time.time() - START_TIME)
# hiperparams["learning_duration [episodes]"] = episode + 1

# print(f'learning duration: {hiperparams["learning_duration [s]"]} [s]')

# with open(MODEL_DIR / 'hiperparams.json', 'w') as f:
#     json.dump(hiperparams, f, indent=2)


# np.save(MODEL_DIR / 'avg_episode_loss.npy', avg_episode_loss)
# np.save(MODEL_DIR / 'episode_length.npy', run_episode_length)
# np.save(MODEL_DIR / 'avg_episode_reward.npy', avg_episode_reward)

# torch.save(Qnet.state_dict(), MODEL_DIR / 'checkpoints' / 'Qnet.pt')

