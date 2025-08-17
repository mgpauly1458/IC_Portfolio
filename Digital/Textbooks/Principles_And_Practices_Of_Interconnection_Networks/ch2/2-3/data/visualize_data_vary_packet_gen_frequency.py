import matplotlib.pyplot as plt
import pandas as pd

# read in random_traffic_results.csv
df = pd.read_csv("random_traffic_results_constant_number_of_cycles.csv")

# plot average dropped packets against total packets generated
plt.figure(figsize=(10, 6))
plt.plot(df["Total Packets Generated"], df["Average Dropped Packets"], marker='o', linestyle='-', color='m')
plt.title("Average Dropped Packets vs Total Packets Generated (Constant Number of Cycles)", fontsize=20)
plt.xlabel("Total Packets Generated", fontsize=16)
plt.ylabel("Average Dropped Packets", fontsize=16)
plt.grid()
plt.savefig("average_dropped_packets_vs_total_packets_generated.png")
plt.show()

# plot the ratio of dropped packets against the generation frequency
plt.figure(figsize=(10, 6))
plt.plot(df["Packet Generation Frequency"], df["Ratio of Dropped Packets to Packet Generation Frequency"], marker='o', linestyle='-', color='y')
plt.title("Ratio of Dropped Packets vs Packet Generation Frequency", fontsize=20)
plt.xlabel("Packet Generation Frequency", fontsize=16)
plt.ylabel("Ratio of Dropped Packets", fontsize=16)
plt.grid()
plt.savefig("ratio_dropped_packets_vs_packet_generation_frequency.png")
plt.show()

# plot total packets generated against the packet generation frequency
plt.figure(figsize=(10, 6))
plt.plot(df["Packet Generation Frequency"], df["Total Packets Generated"], marker='o', linestyle='-', color='c')
plt.title("Total Packets Generated vs Packet Generation Frequency", fontsize=20)
plt.xlabel("Packet Generation Frequency", fontsize=16)
plt.ylabel("Total Packets Generated", fontsize=16)
plt.grid()
plt.savefig("total_packets_generated_vs_packet_generation_frequency.png")
plt.show()

# plot average dropped packets per port against packet generation frequency
plt.figure(figsize=(10, 6))
# Plot all 4 ports
plt.plot(df["Packet Generation Frequency"], df["Average 0 Packets Dropped"], marker='o', linestyle='-', color='orange', label='Port 0')
plt.plot(df["Packet Generation Frequency"], df["Average 1 Packets Dropped"], marker='o', linestyle='-', color='blue', label='Port 1')
plt.plot(df["Packet Generation Frequency"], df["Average 2 Packets Dropped"], marker='o', linestyle='-', color='green', label='Port 2')
plt.plot(df["Packet Generation Frequency"], df["Average 3 Packets Dropped"], marker='o', linestyle='-', color='red', label='Port 3')
plt.title("Average Dropped Packets per Port vs Packet Generation Frequency", fontsize=20)
plt.xlabel("Packet Generation Frequency", fontsize=16)
plt.ylabel("Average Dropped Packets per Port", fontsize=16)
plt.grid()
plt.legend()
plt.savefig("average_dropped_packets_per_port_vs_packet_generation_frequency.png")
plt.show()

# plot standard deviation of dropped packets against packet generation frequency
plt.figure(figsize=(10, 6))
plt.plot(df["Packet Generation Frequency"], df["Standard Deviation Dropped Packets"], marker='o', linestyle='-', color='purple')
plt.title("Standard Deviation of Dropped Packets vs Packet Generation Frequency", fontsize=20)
plt.xlabel("Packet Generation Frequency", fontsize=16)
plt.ylabel("Standard Deviation of Dropped Packets", fontsize=16)
plt.grid()
plt.savefig("standard_deviation_dropped_packets_vs_packet_generation_frequency.png")
plt.show()

# plot total packets generated against frequency of packet generation
plt.figure(figsize=(10, 6))
plt.plot(df["Packet Generation Frequency"], df["Total Packets Generated"], marker='o', linestyle='-', color='c')
plt.title("Total Packets Generated vs Packet Generation Frequency", fontsize=20)
plt.xlabel("Packet Generation Frequency", fontsize=16)
plt.ylabel("Total Packets Generated", fontsize=16)
plt.grid()
plt.savefig("total_packets_generated_vs_packet_generation_frequency.png")
plt.show()
