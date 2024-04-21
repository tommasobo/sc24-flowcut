import os
import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from pathlib import Path    
from datetime import datetime

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

directory = "output/dragonfly_flowcut_mpr"
output_dir = "output/dragonfly_flowcut_mpr/results"

data = list()
current_list = list()
x_label_list = list()
y_label_list = list()
last_ele = 1
first_ele = 1
y_label_ele_base = 10007
divide_by = 1000
for index, filename in enumerate(sorted(os.listdir(directory))):
    #print("{0:02d}. {1}".format(index + 1, filename))
    time_drain = list()
    if (has_numbers(filename) == False):
        continue
    with open(directory + "/" + filename) as fp:
        Lines = fp.readlines()
        match = re.search("(\d+).(\d+)_(\w+)_(\d+)", filename)
        num1 = (int(match.group(1)))
        num = (int(match.group(2)))
        ratio = (int(match.group(4)))

        y_label_ele = float(match.group(1) + "." + match.group(2))

        if (y_label_ele != y_label_ele_base):
            y_label_list.append(y_label_ele)
            y_label_ele_base = y_label_ele

        if (last_ele != num):
            current_list = [x / divide_by for x in current_list]
            data.append(current_list)
            current_list = list()
            last_ele = num

        if (first_ele == num):
            x_label_list.append(ratio)

        for line in Lines:
            match = re.search("Simulation is complete, simulated time: (\d+).(\d+)", line)
            if match:
                time_integer = (int(match.group(1)))
                time_decimal = (int(match.group(2)))
                current_list.append(float(match.group(1) + "." + match.group(2)))
                print("File {} ({}) - Time {}.{}".format(filename, num, time_integer, time_decimal))

            match = re.search("Total Time in Draining NIC (\d+) is (\d+) ", line)
            if match and (int(match.group(2))) != 0:
                time_drain.append((int(match.group(2)) / divide_by))

    if (len(time_drain) > 0):
        print("Total Time Draining {} - Avg {} - Max {}".format(int(sum(time_drain)), int(sum(time_drain) / len(time_drain)), int(max(time_drain))))
        
current_list = [x / divide_by for x in current_list]
data.append(current_list)
matrix = [[52, 47, 50.3, 49, 49.7],
[47.5, 44.8, 50.90, 46.3, 51],
[46.1, 44.7, 56.1, 50.4, 56.236],
[47.2, 54.1, 49.4, 46.49, 55.1],
[54.6, 51.1, 51.5, 50.2, 51.6]]

matrix = data
print(data)

matrix_t = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
print(matrix_t)
print(x_label_list)
print(y_label_list)


labels_x = x_label_list
labels_y = y_label_list
df_cm = pd.DataFrame(matrix, index = labels_y,
                  columns = labels_x)

ax = sns.heatmap(df_cm, linewidth=0.5, annot=True, cmap="YlGnBu") 
plt.xlabel('Max Ratio RTT')
plt.ylabel('Exponential Average Alpha Value')
plt.title('Random Permutation (Random Distribution) - Runtime (ms)')
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("heatmap") + file_name))
plt.savefig(Path("plots/pdf") / (str("heatmap") + file_name + ".pdf"))
plt.show()