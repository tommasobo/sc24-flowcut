import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'flowcut.csv'  # Replace with your file path if needed
data = pd.read_csv(file_path)

# Split the single column into separate columns based on the ';;' delimiter
data_split = data.iloc[:, 0].str.split(';;', expand=True)
data_split.columns = ['Time', 'BW_Ordered', 'BW_Unordered']

# Convert columns to appropriate data types
data_split['Time'] = pd.to_numeric(data_split['Time'], errors='coerce')
data_split['BW_Ordered'] = pd.to_numeric(data_split['BW_Ordered'], errors='coerce')
data_split['BW_Unordered'] = pd.to_numeric(data_split['BW_Unordered'], errors='coerce')

# Drop rows with invalid data
data_cleaned = data_split.dropna()

# Create separate DataFrames for each line
data_ordered = data_cleaned[data_cleaned['BW_Ordered'] > 0]
data_unordered = data_cleaned[data_cleaned['BW_Unordered'] > 0]

# Plot the filtered data
# Plot the filtered data
fig, ax = plt.subplots(figsize=(6, 3.25))
ax.plot(data_ordered['Time'] * 1.176 / 1000, data_ordered['BW_Ordered'], label='BW Ordered', linestyle='-', alpha=0.9, linewidth=2.6, color="#53b280")
ax.plot(data_unordered['Time'] * 1.176 / 1000, data_unordered['BW_Unordered'], label='BW Unordered', linestyle='--', alpha=0.9, linewidth=2.6, color="#c0696c")

# Customize tick parameters and labels
ax.tick_params(labelsize=12)
ax.set_yticklabels([str(int(i)) for i in ax.get_yticks()], fontsize=12)

# Adding labels and legend
#plt.title("Bandwidth vs Time", fontsize=14)
plt.xlabel("Time (μs)", fontsize=13)
plt.ylabel("Throughput (Gbps)", fontsize=13)
#plt.legend(loc='best', fontsize=10)
plt.grid(alpha=0.5)
plt.tight_layout()

# Show the plot
plt.savefig("real.png", bbox_inches='tight')
plt.savefig("real.pdf", bbox_inches='tight')
plt.show()
