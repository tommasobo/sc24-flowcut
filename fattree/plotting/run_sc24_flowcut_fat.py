import os
import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from pathlib import Path    
from datetime import datetime
from statistics import mean 



def getTotOOO():
    return 1

def getAvgCompletionTime(name_file_to_use):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Flow Completion time is (\d+.\d+) - Flow Finishing Time (\d+) - Flow Start Time (\d+) - Size Finished Flow (\d+)", line)
            if result:
                actual = float(result.group(1))
                temp_list.append(actual)
    return mean(temp_list)

def getMaxCompletionTime(name_file_to_use):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Flow Completion time is (\d+.\d+) - Flow Finishing Time (\d+) - Flow Start Time (\d+) - Size Finished Flow (\d+)", line)
            if result:
                actual = float(result.group(1))
                temp_list.append(actual)
    return max(temp_list)

data = list()
current_list = list()
x_label_list = list()
y_label_list = list()
last_ele = 1
first_ele = 1
y_label_ele_base = 10007
divide_by = 1000
possible_alphas = [1/2, 1/4, 1/8, 1/16, 1/32]
possible_ratio = [1, 1.5, 2, 2.5, 3, 4, 5, 10]

possible_alphas = [1/4, 1/8, 1/16, 1/32]
possible_ratio = [1, 2, 3, 5, 10]

for alpha in possible_alphas:
    y_label_list.append(alpha)
    for rtt_ratio in possible_ratio:
        to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/test_web.txt -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowcut -cwnd 2500000 -alpha_flowcut {} -rtt_ratio {} > out3.tmp".format(alpha, rtt_ratio)
        print(to_run)
        os.system(to_run)
        
        current_list.append(getAvgCompletionTime("out3.tmp"))
    data.append(current_list)
    current_list = list()



# Random
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc random -cwnd 2500000 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)

# ECMP
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc ecmp -cwnd 2500000 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)

# Flowlet
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowlet -cwnd 2500000 -flowlet_value 10550000 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)

# Flowcut
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowcut -cwnd 2500000 -rtt_ratio 3 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)

x_label_list = possible_ratio

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
plt.title('Random Permutation (Web-search) - Runtime (ms)')
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
#plt.savefig(Path("plots/png") / (str("heatmap") + file_name))
#plt.savefig(Path("plots/pdf") / (str("heatmap") + file_name + ".pdf"))
plt.show()