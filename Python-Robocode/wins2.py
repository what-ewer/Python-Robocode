import dill
import numpy as np
import matplotlib.pyplot as plt

# load the list of positions from the dill file
with open('positions.dill', 'rb') as file:
    positions = dill.load(file)

# divide the positions into 10 fragments
buckets = 10
num_races_per_fragment = len(positions) // buckets
fragments = np.array_split(positions, buckets)

# create a list to store the number of 1st, 2nd, 3rd, and 4th places for each fragment
num_places = [[0, 0, 0, 0] for _ in range(buckets)]

# count the number of 1st, 2nd, 3rd, and 4th places for each fragment
for i, fragment in enumerate(fragments):
    for place in fragment:
        num_places[i][place-1] += 1

# create a bar chart to plot the number of 1st, 2nd, 3rd, and 4th places for each fragment
x = np.arange(buckets)
fig, ax = plt.subplots()
ax.bar(x, [places[0] for places in num_places], 0.9, label='1st')
ax.bar(x, [places[1] for places in num_places], 0.9, bottom=[places[0] for places in num_places], label='2nd')
ax.bar(x, [places[2] for places in num_places], 0.9, bottom=[places[1]+places[0] for places in num_places], label='3rd')
ax.bar(x, [places[3] for places in num_places], 0.9, bottom=[places[2]+places[1]+places[0] for places in num_places], label='4th')

ax.set_xlabel('Fragment')
ax.set_ylabel('Number of Races')
ax.set_xticks(x)
ax.legend()

plt.show()
