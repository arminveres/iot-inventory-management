import re
import matplotlib.pyplot as plt
import numpy as np


# Parse the file and store the relevant data
file_path = ".agent_cache/time_log"
with open(file_path, "r") as file:
    contents = file.readlines()

data = []
for line in contents:
    # Extracting action, time, and node name
    match = re.search(r"(REVOCATION|UPDATE): time: (\d+), node: (.+)", line)
    if match:
        action, time, node = match.groups()
        data.append({"action": action, "time": int(time), "node": node})

# Sort the data based on node and action to ensure correct ordering
data.sort(key=lambda x: (x["node"], x["action"]))

# Calculate the time differences for updates after revocation for each node
update_times = []
nodes = []
prev_node = ""
prev_time = 0
no_nodes=0

for entry in data:
    if entry["node"] != prev_node and entry["action"] == "REVOCATION":
        prev_node = entry["node"]
        prev_time = entry["time"]
    elif entry["node"] == prev_node and entry["action"] == "UPDATE":
        # converting to a more readable unit, like seconds
        time_diff = (entry["time"] - prev_time) / 1e6
        update_times.append(time_diff)
        nodes.append(entry["node"])
        no_nodes+=1

# Calculate the average time taken
average_time = np.mean(update_times)

# Plotting the data with the average time
plt.figure(figsize=(12, 8))
plt.barh(nodes, update_times, color="skyblue")
plt.axvline(x=average_time, color="red", linestyle="--", label=f"Average Time: {average_time:.2f}")

plt.xlabel("Time to Update After Revocation (in miliseconds)")
plt.ylabel("Nodes")
plt.title("Time Taken to Update Each Node After Credential Revocation")
plt.legend()
plt.grid(axis="x")

plt.savefig(f'revocation_{no_nodes}_nodes.png')
plt.show()
