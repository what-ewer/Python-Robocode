import dill
import matplotlib.pyplot as plt
import numpy as np

# Load the scores from the dill file
with open('scores.dill', 'rb') as f:
    scores = dill.load(f)

# Calculate the moving average of the scores
window_size = 20
moving_average = np.convolve(scores, np.ones(window_size)/window_size, mode='valid')

# Plot the scores and moving average
plt.plot(scores, label='Scores')
plt.plot(moving_average, label='Moving Average')
plt.legend()
plt.show()
