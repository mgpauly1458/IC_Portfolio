import matplotlib.pyplot as plt
import pandas as pd

# read in random_traffic_results.csv
df = pd.read_csv("random_traffic_results_constant_packet_gen_frequency.csv")

# plot average dropped packets against total packets generated
plt.figure(figsize=(10, 6))
plt.plot(df["Total Packets Generated"], df["Average Dropped Packets"], marker='o', linestyle='-', color='m')
plt.title("Average Dropped Packets vs Total Packets Generated (Constant Packet Generation Frequency)", fontsize=20)
plt.xlabel("Total Packets Generated", fontsize=16)
plt.ylabel("Average Dropped Packets", fontsize=16)
plt.grid()
plt.savefig("average_dropped_packets_vs_total_packets_generated.png")
plt.show()

######################## Cycle variance only ##########################################
# Plot the average number of dropped packets against the number of cycles
plt.figure(figsize=(10, 6))
plt.plot(df["Number of Cycles"], df["Average Dropped Packets"], marker='o', linestyle='-', color='b')
plt.title("Average Dropped Packets vs Number of Cycles", fontsize=20)
plt.xlabel("Number of Cycles", fontsize=16)
plt.ylabel("Average Dropped Packets", fontsize=16)
plt.grid()
plt.savefig("average_dropped_packets_vs_cycles.png")
plt.show()

# plot the ratio of dropped packets against the number of cycles
plt.figure(figsize=(10, 6))
plt.plot(df["Number of Cycles"], df["Ratio of Dropped Packets to Total Cycles"], marker='o', linestyle='-', color='r')
plt.title("Ratio of Dropped Packets vs Number of Cycles", fontsize=20)
plt.xlabel("Number of Cycles", fontsize=16)
plt.ylabel("Ratio of Dropped Packets", fontsize=16)
plt.grid()
plt.savefig("ratio_dropped_packets_vs_cycles.png")
plt.show()

# plot total packets generated against number of cycles
plt.figure(figsize=(10, 6))
plt.plot(df["Number of Cycles"], df["Total Packets Generated"], marker='o', linestyle='-', color='g')
plt.title("Total Packets Generated vs Number of Cycles", fontsize=20)
plt.xlabel("Number of Cycles", fontsize=16)
plt.ylabel("Total Packets Generated", fontsize=16)
plt.grid()
plt.savefig("total_packets_generated_vs_cycles.png")
plt.show()

# plot average dropped packets per port against number of cycles
plt.figure(figsize=(10, 6))
# Plot all 4 ports
plt.plot(df["Number of Cycles"], df["Average 0 Packets Dropped"], marker='o', linestyle='-', color='orange', label='Port 0')
plt.plot(df["Number of Cycles"], df["Average 1 Packets Dropped"], marker='o', linestyle='-', color='blue', label='Port 1')
plt.plot(df["Number of Cycles"], df["Average 2 Packets Dropped"], marker='o', linestyle='-', color='green', label='Port 2')
plt.plot(df["Number of Cycles"], df["Average 3 Packets Dropped"], marker='o', linestyle='-', color='red', label='Port 3')
plt.title("Average Dropped Packets per Port vs Number of Cycles", fontsize=20)
plt.xlabel("Number of Cycles", fontsize=16)
plt.ylabel("Average Dropped Packets per Port", fontsize=16)
plt.grid()
plt.savefig("average_dropped_packets_per_port_vs_cycles.png")
plt.show()

# plot standard deviation of all port dropped packets against number of cycles
plt.figure(figsize=(10, 6))
plt.plot(df["Number of Cycles"], df["Standard Deviation Dropped Packets"], marker='o', linestyle='-', color='purple')
plt.title("Standard Deviation of Dropped Packets vs Number of Cycles", fontsize=20)
plt.xlabel("Number of Cycles", fontsize=16)
plt.ylabel("Standard Deviation of Dropped Packets", fontsize=16)
plt.grid()
plt.savefig("standard_deviation_dropped_packets_vs_cycles.png")
plt.show()
