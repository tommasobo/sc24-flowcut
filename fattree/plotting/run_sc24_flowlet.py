import os
import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from pathlib import Path    
from datetime import datetime
from statistics import mean 

def getTotOOO(name_file_to_use):
    seen = 0
    ooo = 0
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Packets Seen (\d+) - Packets OOO (\d+)", line)
            if result:
                seen += int(result.group(1))
                ooo += int(result.group(2))
    return ooo / seen * 100

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

to_plot1 = "python3 performance_complete.py"
to_plot2 = "python3 performance_rate.py"

os_ratio = 1
exp_name = "test_web.txt"
exp_name = "test_mining.txt"
exp_name = "perm_128_t"
exp_name = "test_ali_200.txt"

# Random
print()
value_flowlet = 18000000
to_run = "../sim/datacenter/htsim_ndp_entry_modern -failure_link 80 -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowlet -cwnd 2500000 -flowlet_value {} > out.tmp".format(exp_name, value_flowlet)
os.system(to_run)
avg_fct = getAvgCompletionTime("out.tmp")
num_ooo = getTotOOO("out.tmp")
print("flowlet gap {}".format(value_flowlet))
print(avg_fct)
print(num_ooo)

# ECMP
print()
value_flowlet = 16000000
to_run = "../sim/datacenter/htsim_ndp_entry_modern -failure_link 80 -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowlet -cwnd 2500000 -flowlet_value {} > out.tmp".format(exp_name, value_flowlet)
os.system(to_run)
avg_fct = getAvgCompletionTime("out.tmp")
num_ooo = getTotOOO("out.tmp")
print("flowlet gap {}".format(value_flowlet))
print(avg_fct)
print(num_ooo)

# Flowlet
print()
value_flowlet = 14000000
to_run = "../sim/datacenter/htsim_ndp_entry_modern -failure_link 80 -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowlet -cwnd 2500000 -flowlet_value {} > out.tmp".format(exp_name, value_flowlet)
os.system(to_run)
avg_fct = getAvgCompletionTime("out.tmp")
num_ooo = getTotOOO("out.tmp")
print("flowlet gap {}".format(value_flowlet))
print(avg_fct)
print(num_ooo)

# Flowcut
print()
value_flowlet = 12000000
to_run = "../sim/datacenter/htsim_ndp_entry_modern -failure_link 80 -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowlet -cwnd 2500000 -flowlet_value {} > out.tmp".format(exp_name, value_flowlet)
os.system(to_run)
avg_fct = getAvgCompletionTime("out.tmp")
num_ooo = getTotOOO("out.tmp")
print("flowlet gap {}".format(value_flowlet))
print(avg_fct)
print(num_ooo)
