import matplotlib.pyplot as plt

# number of nodes, avg time, total time
# data = [[1, 387.78, 387.78], [10, 329, 85, 3298.5], [32, 329.92, 10557.49]]
no_nodes = ["1", "10", "32"]
avg_time = [387.78, 329.85, 329.92]
overall_time = [387.78, 3298.5, 10557.49]

fig, ax = plt.subplots(1, 2, layout="constrained", figsize=(12, 8))

ax[0].set_title("Average time to issue credential to a node")
ax[0].bar(no_nodes, avg_time, color="skyblue", width=0.5)
ax[0].plot(no_nodes, avg_time, color="red")
ax[0].set_xlabel("Number of Nodes")
ax[0].set_ylabel("Time taken in Milliseconds (ms)")

ax[1].set_title("Overall time to issue credential to nodes")
ax[1].bar(no_nodes, overall_time, color="skyblue", width=0.5)
ax[1].plot(no_nodes, overall_time, color="red")
ax[1].set_xlabel("Number of Nodes")
ax[1].set_ylabel("Time taken in Milliseconds (ms)")

fig.suptitle("Issuing Credentials", fontsize=16)

plt.savefig("graphs/issuing_creds_overview.png", format="png", dpi=300)
plt.show()
