import matplotlib.pyplot as plt

# number of nodes, avg time, total time
# data = [[1, 387.78, 387.78], [10, 329, 85, 3298.5], [32, 329.92, 10557.49]]
no_nodes = ["1", "10", "32"]
avg_time = [7.62, 8.27, 9.08]
overall_time = [7.62, 82.72, 290.51]

fig, ax = plt.subplots(1, 2, layout="constrained", figsize=(12, 8))

ax[0].set_title("Average time to revoke credential from a node")
ax[0].bar(no_nodes, avg_time, color="skyblue", width=0.5)
ax[0].plot(no_nodes, avg_time, color="red")
ax[0].set_xlabel("Number of Nodes")
ax[0].set_ylabel("Time taken in Milliseconds (ms)")

ax[1].set_title("Overall time to revoke a credential from nodes")
ax[1].bar(no_nodes, overall_time, color="skyblue", width=0.5)
ax[1].plot(no_nodes, overall_time, color="red")
ax[1].set_xlabel("Number of Nodes")
ax[1].set_ylabel("Time taken in Milliseconds (ms)")

fig.suptitle("Revoking Credentials", fontsize=16)

plt.savefig("graphs/revoking_creds_overview.png", format="png", dpi=300)
plt.show()
