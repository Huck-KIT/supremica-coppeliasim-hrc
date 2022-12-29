import numpy as np
import matplotlib.pyplot as plt

# X = ['Scenario A','Scenario B','Scenario C']
# N_twolayer = [21.2,38.1,6.7]
# N_MCTS = [4.7,16.9,3.5]
# N_Random = [0.4,24.2,2]
#
# X_axis = np.arange(len(X))
#
# plt_1 = plt.figure(figsize=(3.5, 5), dpi=300)
#
# plt.bar(X_axis - 0.2, N_twolayer, 0.2, label = 'Two-Layer',color="lightskyblue")
# plt.bar(X_axis, N_MCTS, 0.2, label = 'MCTS',color="steelblue")
# plt.bar(X_axis + 0.2, N_Random, 0.2, label = 'Random',color="slategrey")
#
#
# plt.xticks(X_axis, X)
# # plt.xlabel("Groups")
# plt.ylabel("N")
# plt.title("Average number of unsafe\n sequences found per test run")
# plt.grid(True)
# plt.legend()
# plt.show()

'''--------------------------------------------------------------------------'''

X = ['Scenario A','Scenario B','Scenario C']
N_twolayer = [3.93,7.44,28.31]
N_MCTS = [4.05,6.33,29.4]
N_Random = [3.70,4.07,31.8]

X_axis = np.arange(len(X))

plt_1 = plt.figure(figsize=(3.5, 5), dpi=300)

plt.bar(X_axis - 0.2, N_twolayer, 0.2, label = 'Two-Layer',color="lightpink")
plt.bar(X_axis, N_MCTS, 0.2, label = 'MCTS',color="palevioletred")
plt.bar(X_axis + 0.2, N_Random, 0.2, label = 'Random',color="slategrey")


plt.xticks(X_axis, X)
# plt.xlabel("Groups")
plt.ylabel("r")
plt.title("Average risk of unsafe sequences")
plt.grid(True)
plt.legend()

plt.show()

# '''--------------------------------------------------------------------------'''


# X = ['No light curtain','400ms','300ms','200ms','100ms']
# # N_twolayer = [21.2,38.1]
# N_MCTS = [16.9,9.3,3.9,2.8,3.5]
# N_Random = [24.2,13,4.3,1.9,2]
#
# N_Rel = list()
# for i in range(len(N_MCTS)):
#     N_Rel.append(100*(N_MCTS[i]/N_Random[i]-1))
# X_axis = np.arange(len(X))
#
# # plt.bar(X_axis - 0.2, N_twolayer, 0.2, label = 'Two-Layer',color="lightskyblue")
# # plt.bar(X_axis, N_MCTS, 0.2, label = 'MCTS',color="steelblue")
# # plt.bar(X_axis + 0.2, N_Random, 0.2, label = 'Random',color="slategrey")
# plt.bar(X_axis, N_Rel, 0.2,color="red")
#
#
#
# plt.xticks(X_axis, X)
# plt.xlabel("Light Curtain Response Time")
# plt.ylabel("Number of unsafe sequences found\n by MCTS compared to Random, in %")
# plt.title("Relative Performance of Risk-guided Search\n in Comparison to Random Sampling")
# plt.grid(True)
# # plt.legend()
# plt.show()
