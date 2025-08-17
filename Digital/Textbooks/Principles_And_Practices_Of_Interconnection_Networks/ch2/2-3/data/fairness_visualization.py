import pandas as pd
import matplotlib.pyplot as plt
import scipy

# file names
fairness_file = "fairness_random_traffic_results_constant_packet_gen_frequency.csv"
random_file = "random_traffic_results_constant_packet_gen_frequency.csv"

# figure save path
save_path = "fairness_comparison/"

# read in data
fairness_df = pd.read_csv(fairness_file)
random_df = pd.read_csv(random_file)

# grab data from 1000 - 5000 cycles
fairness_df = fairness_df[(fairness_df["Number of Cycles"] >= 1000) & (fairness_df["Number of Cycles"] <= 5000)]
random_df = random_df[(random_df["Number of Cycles"] >= 1000) & (random_df["Number of Cycles"] <= 5000)]

# plot all port average dropped packets against number of cycles
plt.figure(figsize=(10, 6))
plt.plot(fairness_df["Number of Cycles"], fairness_df["Average 0 Packets Dropped"], marker='o', linestyle='-', color='orange', label='Fairness Port 0')
plt.plot(fairness_df["Number of Cycles"], fairness_df["Average 1 Packets Dropped"], marker='o', linestyle='-', color='blue', label='Fairness Port 1')
plt.plot(fairness_df["Number of Cycles"], fairness_df["Average 2 Packets Dropped"], marker='o', linestyle='-', color='green', label='Fairness Port 2')
plt.plot(fairness_df["Number of Cycles"], fairness_df["Average 3 Packets Dropped"], marker='o', linestyle='-', color='red', label='Fairness Port 3')
plt.plot(random_df["Number of Cycles"], random_df["Average 0 Packets Dropped"], marker='x', linestyle='--', color='orange', label='Random Port 0')
plt.plot(random_df["Number of Cycles"], random_df["Average 1 Packets Dropped"], marker='x', linestyle='--', color='blue', label='Random Port 1')
plt.plot(random_df["Number of Cycles"], random_df["Average 2 Packets Dropped"], marker='x', linestyle='--', color='green', label='Random Port 2')
plt.plot(random_df["Number of Cycles"], random_df["Average 3 Packets Dropped"], marker='x', linestyle='--', color='red', label='Random Port 3')
plt.title("Average Dropped Packets per Port vs Number of Cycles", fontsize=20)
plt.xlabel("Number of Cycles", fontsize=16)
plt.ylabel("Average Dropped Packets per Port", fontsize=16)
plt.grid()
plt.legend()
plt.savefig(save_path + "average_dropped_packets_per_port_vs_cycles_comparison.png")
plt.show()

# train linear line of best fit for each port from both files
slope_fairness0, intercept_fairness0, r_value_fairness0, p_value_fairness0, std_err_fairness0 = scipy.stats.linregress(fairness_df["Number of Cycles"], fairness_df["Average 0 Packets Dropped"])
slope_fairness1, intercept_fairness1, r_value_fairness1, p_value_fairness1, std_err_fairness1 = scipy.stats.linregress(fairness_df["Number of Cycles"], fairness_df["Average 1 Packets Dropped"])
slope_fairness2, intercept_fairness2, r_value_fairness2, p_value_fairness2, std_err_fairness2 = scipy.stats.linregress(fairness_df["Number of Cycles"], fairness_df["Average 2 Packets Dropped"])
slope_fairness3, intercept_fairness3, r_value_fairness3, p_value_fairness3, std_err_fairness3 = scipy.stats.linregress(fairness_df["Number of Cycles"], fairness_df["Average 3 Packets Dropped"])
slope_random0, intercept_random0, r_value_random0, p_value_random0, std_err_random0 = scipy.stats.linregress(random_df["Number of Cycles"], random_df["Average 0 Packets Dropped"])
slope_random1, intercept_random1, r_value_random1, p_value_random1, std_err_random1 = scipy.stats.linregress(random_df["Number of Cycles"], random_df["Average 1 Packets Dropped"])
slope_random2, intercept_random2, r_value_random2, p_value_random2, std_err_random2 = scipy.stats.linregress(random_df["Number of Cycles"], random_df["Average 2 Packets Dropped"])
slope_random3, intercept_random3, r_value_random3, p_value_random3, std_err_random3 = scipy.stats.linregress(random_df["Number of Cycles"], random_df["Average 3 Packets Dropped"])

# plot the linear lines of best fit
plt.figure(figsize=(10, 6))
x_values = range(1000, 5001, 100)
plt.plot(x_values, [slope_fairness0 * x + intercept_fairness0 for x in x_values], linestyle='-', color='orange', label='Fairness Port 0 Fit')
plt.plot(x_values, [slope_fairness1 * x + intercept_fairness1 for x in x_values], linestyle='-', color='blue', label='Fairness Port 1 Fit')
plt.plot(x_values, [slope_fairness2 * x + intercept_fairness2 for x in x_values], linestyle='-', color='green', label='Fairness Port 2 Fit')
plt.plot(x_values, [slope_fairness3 * x + intercept_fairness3 for x in x_values], linestyle='-', color='red', label='Fairness Port 3 Fit')
plt.plot(x_values, [slope_random0 * x + intercept_random0 for x in x_values], linestyle='--', color='orange', label='Random Port 0 Fit')
plt.plot(x_values, [slope_random1 * x + intercept_random1 for x in x_values], linestyle='--', color='blue', label='Random Port 1 Fit')
plt.plot(x_values, [slope_random2 * x + intercept_random2 for x in x_values], linestyle='--', color='green', label='Random Port 2 Fit')
plt.plot(x_values, [slope_random3 * x + intercept_random3 for x in x_values], linestyle='--', color='red', label='Random Port 3 Fit')
plt.title("Linear Fit of Average Dropped Packets per Port vs Number of Cycles", fontsize=20)
plt.xlabel("Number of Cycles", fontsize=16)
plt.ylabel("Average Dropped Packets per Port", fontsize=16)
plt.grid()
plt.legend()
plt.savefig(save_path + "linear_fit_average_dropped_packets_per_port_vs_cycles_comparison.png")
plt.show()

# print standard deviation of slopes for fairness and random
standard_deviation_fairness = scipy.stats.tstd([slope_fairness0, slope_fairness1, slope_fairness2, slope_fairness3])
standard_deviation_random = scipy.stats.tstd([slope_random0, slope_random1, slope_random2, slope_random3])
print(f"Standard Deviation of Fairness Slopes: {standard_deviation_fairness}")
print(f"Standard Deviation of Random Slopes: {standard_deviation_random}")
