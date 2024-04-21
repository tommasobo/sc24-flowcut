import os
import re 
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
from  matplotlib.ticker import FuncFormatter
import random
import seaborn as sns
import pandas as pd
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FormatStrFormatter

# Constants
rateo = 8
link_speed = 100000 * rateo
hops = 12
size_1 = 4160
tot_capacity = (((12 * 1000) + (6*4160*8/(link_speed/1000))) * (link_speed/1000)) / 8

paths = 128
fi_gain = 0.25 * rateo
fd_gain = 0.8
md_gain = 1 * 2
mi_gain = 2 * (rateo / 2)
bonus_drop = 0.85
ecn_min = int(tot_capacity/size_1/5)
ecn_max = int(tot_capacity/size_1/5*4)
queue_size = int(tot_capacity/size_1)
initial_cwnd = int(tot_capacity/size_1*1.25)

os_ratio = 1
eqds_cwnd = 100000
inter_dc_delay = 500000
phantom_size = 6500000
custom_queue_size = 95000000
phantom_slowdown = 5

show_plots = False

def getCompletionTime(name_file_to_use, min_size=0, max_size=999999999, algo=None):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Flow Completion time is (\d+.\d+) - Flow Finishing Time (\d+) - Flow Start Time (\d+) - Size Finished Flow (\d+)", line)
            if result:
                actual = int(result.group(2))
                temp_list.append(actual/1000)
    return max(temp_list)

def getListFCT(name_file_to_use, min_size=0, max_size=999999999, algo=None):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Flow Completion time is (\d+.\d+) - Flow Finishing Time (\d+) - Flow Start Time (\d+) - Size Finished Flow (\d+)", line)
            if result:
                actual = float(result.group(1))
                size_flow = int(result.group(4))
                if (size_flow < max_size and size_flow > min_size):
                    temp_list.append(actual)
    return temp_list

def getList99FCT(name_file_to_use, algo=None):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Flow Completion time is (\d+.\d+)", line)
            if result:
                actual = float(result.group(1))
                temp_list.append(actual)
    return temp_list

def getNumTrimmed(name_file_to_use, algo=None):
    num_nack = 0
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Total NACKs: (\d+)", line)
            if result:
                num_nack += int(result.group(1))
    return num_nack

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

def run_experiment(experiment_name, experiment_cm, topo_name, name_title, msg_size):
    
    os.system("rm -rf experiments/{}".format(experiment_name))
    os.system("mkdir experiments/{}".format(experiment_name))

    # PhantomCC
    out_name = "experiments/{}/out.txt".format(experiment_name)
    string_to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/{} -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size {} -interdc_delay 500000 -routing_sc random -cwnd 2500000 > {}".format(topo_name, experiment_cm, custom_queue_size, out_name)
    print(string_to_run)
    os.system(string_to_run)
    
    list_phantombts = getListFCT(out_name)
    list_phantombts_small = getListFCT(out_name, min_size=0, max_size=100000)
    list_phantombts_large = getListFCT(out_name, min_size=1000000, max_size=1000000000)
    num_nack_phantombts = getTotOOO(out_name)
    print("Spraying Completion Time {}\n".format(getCompletionTime(out_name)))
    print("PhantomCCBTS: Flow Diff {} - Total {}".format(max(list_phantombts) - min(list_phantombts), max(list_phantombts)))
    if (show_plots):
        os.system("python3 performance_complete.py --name {}{}".format(experiment_cm, "__PhantomCCBTS"))

    # PhantomCC
    out_name = "experiments/{}/out.txt".format(experiment_name)
    string_to_run = "../sim/datacenter/htsim_uec_entry_modern -o uec_entry -k 1 -topo ../sim/datacenter/topologies/{} -algorithm intersmartt_test -nodes 128 -q 4452000 -strat ecmp_host_random2_ecn -number_entropies 1024 -kmin 2 -kmax 80 -use_fast_increase 1 -use_super_fast_increase 1 -fast_drop 1 -linkspeed 200000 -mtu 4096 -seed 15 -queue_type composite -hop_latency 1000 -switch_latency 0 -reuse_entropy 1 -os_border {} -tm ../sim/datacenter/connection_matrices/{} -x_gain 4 -y_gain 0 -w_gain 0 -z_gain 4 -bonus_drop 1.0 -collect_data 0 -use_pacing 1 -use_phantom 1 -phantom_slowdown 5 -phantom_size {} -decrease_on_nack 0 -topology interdc -max_queue_size {} -interdc_delay {} -phantom_both_queues > {}".format(topo_name, os_ratio, experiment_cm,phantom_size, custom_queue_size,inter_dc_delay, out_name)
    string_to_run = "../sim/datacenter/htsim_uec_entry_modern -o uec_entry -k 1 -topo ../sim/datacenter/topologies/{} -algorithm intersmartt_test -nodes 128 -q 4452000 -strat ecmp_host_random2_ecn -number_entropies 1024 -kmin 2 -kmax 80 -use_fast_increase 1 -use_super_fast_increase 1 -fast_drop 1 -linkspeed 200000 -mtu 4096 -seed 15 -queue_type composite -hop_latency 1000 -switch_latency 0 -reuse_entropy 1 -os_border {} -tm ../sim/datacenter/connection_matrices/{} -x_gain 4 -y_gain 0 -w_gain 0 -z_gain 4 -bonus_drop 1.0 -collect_data 0 -use_pacing 1 -use_phantom 1 -phantom_slowdown 5 -phantom_size {} -decrease_on_nack 1 -phantom_in_series -topology interdc -max_queue_size {} -interdc_delay {} -phantom_both_queues > {}".format(topo_name, os_ratio, experiment_cm,phantom_size, custom_queue_size,inter_dc_delay, out_name)
    string_to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/{} -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size {} -interdc_delay 500000 -routing_sc ecmp -cwnd 2500000 > {}".format(topo_name, experiment_cm, custom_queue_size, out_name)

    print(string_to_run)
    os.system(string_to_run)
    print("ECMP Completion Time {}\n".format(getCompletionTime(out_name)))
    list_phantom = getListFCT(out_name)
    list_phantom_small = getListFCT(out_name, min_size=0, max_size=100000)
    list_phantom_large = getListFCT(out_name, min_size=1000000, max_size=1000000000)
    num_nack_phantom_simple = getTotOOO(out_name)
    print("PhantomCCSimple: Flow Diff {} - Total {}".format(max(list_phantom) - min(list_phantom), max(list_phantom)))
    if (show_plots):
        os.system("python3 performance_complete.py --name {}{}".format(experiment_cm, "__PhantomCCSimple"))

    # MPRDMA
    out_name = "experiments/{}/out.txt".format(experiment_name)
    string_to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/{} -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size {} -interdc_delay 500000 -routing_sc flowlet -flowlet_value 1590000 -cwnd 2500000 > {}".format(topo_name, experiment_cm, custom_queue_size, out_name)
    os.system(string_to_run)
    print(string_to_run)
    list_smartt2 = getListFCT(out_name)
    
    num_nack_mprdma = getTotOOO(out_name)
    print("Flowlet1 Completion Time {}\n".format(getCompletionTime(out_name)))
    list_dctcp_small = getListFCT(out_name, min_size=0, max_size=100000)
    list_dctcp_large = getListFCT(out_name, min_size=1000000, max_size=1000000000)
    print("MPRDMA: Flow Diff {} - Total {}".format(max(list_smartt2) - min(list_smartt2), max(list_smartt2)))
    if (show_plots):
        os.system("python3 performance_complete.py --name {}{}".format(experiment_cm, "__MPRDMA"))

    # MPRDMA2
    out_name = "experiments/{}/out.txt".format(experiment_name)
    string_to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/{} -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size {} -interdc_delay 500000 -routing_sc flowlet -flowlet_value 82080000 -cwnd 2500000 > {}".format(topo_name, experiment_cm, custom_queue_size, out_name)
    os.system(string_to_run)
    print(string_to_run)
    print("Flowlet2 Completion Time {}\n".format(getCompletionTime(out_name)))
    list_bbr = getListFCT(out_name)
    list_bbr_small = getListFCT(out_name, min_size=0, max_size=100000)
    list_bbr_large = getListFCT(out_name, min_size=1000000, max_size=10000000)
    num_nack_bbr = getTotOOO(out_name)
    if (show_plots):
        os.system("python3 performance_complete.py --name {}{}".format(experiment_cm, "__MPRDMA2")) 

    # Flowlet Balanced
    out_name = "experiments/{}/out.txt".format(experiment_name)
    string_to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/{} -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size {} -interdc_delay 500000 -routing_sc flowlet -flowlet_value 42080000 -cwnd 2500000 > {}".format(topo_name, experiment_cm, custom_queue_size, out_name)
    os.system(string_to_run)
    print(string_to_run)
    list_balanced = getListFCT(out_name)
    list_balanced_small = getListFCT(out_name, min_size=0, max_size=100000)
    list_balanced_large = getListFCT(out_name, min_size=1000000, max_size=10000000)
    num_nack_balanced = getTotOOO(out_name)
    print("Flowlet3 Completion Time {}\n".format(getCompletionTime(out_name)))
    if (show_plots):
        os.system("python3 performance_complete.py --name {}{}".format(experiment_cm, "__MPRDMA2")) 

    # EQDS
    out_name = "experiments/{}/out.txt".format(experiment_name)
    string_to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/{} -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 200000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/{} -collect_data 0 -topology interdc -max_queue_size {} -interdc_delay 500000 -routing_sc flowcut -rtt_ratio 4 -cwnd 2500000 > {}".format(topo_name, experiment_cm, custom_queue_size, out_name)
    os.system(string_to_run)
    print(string_to_run)
    print("Flowcut Completion Time {}\n".format(getCompletionTime(out_name)))
    list_smartt3 = getListFCT(out_name)
    list_eqds_small = getListFCT(out_name, min_size=0, max_size=100000)
    list_eqds_large = getListFCT(out_name, min_size=1000000, max_size=1000000000)
    num_nack_eqds = getTotOOO(out_name)
    print("EQDS: Flow Diff {} - Total {}".format(max(list_smartt3) - min(list_smartt3), max(list_smartt3)))
    if (show_plots):
        os.system("python3 performance_complete.py --name {}{}".format(experiment_cm, "__EQDS"))

    # Combine all data into a list of lists
    list_smartt2 = [x / 1000 for x in list_smartt2]
    list_smartt3 = [x / 1000 for x in list_smartt3]
    list_phantom = [x / 1000 for x in list_phantom]
    list_balanced = [x / 1000 for x in list_balanced]
    list_bbr = [x / 1000 for x in list_bbr]
    list_phantombts = [x / 1000 for x in list_phantombts]

    all_data = [list_phantom, list_phantombts, list_smartt2, list_balanced, list_bbr, list_smartt3]


    # Create a list of labels for each dataset
    labels = ['ECMP', 'Spraying', 'Flowlet\nBest\nPerf.', 'Flowlet\nBalanced\nPerf.', 'Flowlet\nLowest\nOOO', 'Flowcut']

    plt.figure(figsize=(6, 4.5))
    # Calculate the average value and 95% confidence interval for each list
    averages = [sum(lst) / len(lst) for lst in all_data]

    # Create a bar plot using Seaborn
    colors = ['#3274a1', '#e1812c', '#3a923a', '#c03d3e', '#9372b2']
    colors = ["#53b280"] * 10

    ax = sns.barplot(x=labels, y=averages, ci=None, palette=colors)  # Setting ci=None disables the default error bars

    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())
    ax.tick_params(labelsize=12.2)
    ax.set_yticklabels([str(round(i,1)) for i in ax.get_yticks()], fontsize = 15)

    # Set labels and title
    plt.ylabel('Flow Completion Time ({})'.format("ms"),fontsize=15)
    #plt.xlabel('Congestion Control Algorithm',fontsize=17.5)

    plt.grid()  #just add this
    plt.legend([],[], frameon=False)
    ax.set_axisbelow(True)

    # Show the plot
    plt.tight_layout()
    plt.savefig("experiments/{}/avg_fct.svg".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/avg_fct.png".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/avg_fct.pdf".format(experiment_name), bbox_inches='tight')
    plt.close()

    # PLOT 4 BARPLOT
    plt.figure(figsize=(6, 4.5))
    # Calculate the average value and 95% confidence interval for each list
    all_data = [list_phantom, list_phantombts, list_smartt2, list_balanced, list_bbr, list_smartt3]
    percentiles_99 = [np.percentile(lst, 99) for lst in all_data]

    # Create a new list of lists containing only values above the 99th percentile for each inner list
    above_99th_percentile_lists = [[x for x in lst if x > percentile] for lst, percentile in zip(all_data, percentiles_99)]
    averages = [sum(lst) / len(lst) for lst in above_99th_percentile_lists]

    # Create a bar plot using Seaborn
    ax = sns.barplot(x=labels, y=averages, ci=None, palette=colors)  # Setting ci=None disables the default error bars
    
    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())
    ax.tick_params(labelsize=12.2)
    ax.set_yticklabels([str(round(i,1)) for i in ax.get_yticks()], fontsize = 15)

    # Set labels and title
    plt.ylabel('FCT 99th Tail ({})'.format("ms"),fontsize=15)
    #plt.xlabel('Congestion Control Algorithm',fontsize=17.5)

    plt.grid()  #just add this
    plt.legend([],[], frameon=False)
    ax.set_axisbelow(True)

    # Show the plot
    plt.tight_layout()
    plt.savefig("experiments/{}/avg99_fct.svg".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/avg99_fct.png".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/avg99_fct.pdf".format(experiment_name), bbox_inches='tight')
    plt.close()   

    # PLOT 2 (NACK)
    # Your list of 5 numbers and corresponding labels
    plt.figure(figsize=(6, 4.5))
    numbers = [num_nack_phantom_simple, num_nack_phantombts, num_nack_mprdma, num_nack_balanced, num_nack_bbr, num_nack_eqds]
    labels = ['ECMP', 'Spraying', 'Flowlet\nBest\nPerf.', 'Flowlet\nBalanced\nPerf.', 'Flowlet\nLowest\nOOO', 'Flowcut']


    # Create a DataFrame from the lists
    data = pd.DataFrame({'Packets Trimmed': numbers, 'Algorithm': labels})

    # Create a bar chart using Seaborn
    colors = ["#c0696c"] * 10
    ax3 = sns.barplot(x=labels, y=numbers, palette=colors)
    ax3.tick_params(labelsize=12.2)
    # Format y-axis tick labels without scientific notation
    
    ax3.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))# Shosw the plot
    ax3.set_xticks(ax3.get_xticks())
    ax3.set_yticks(ax3.get_yticks())
    ax.tick_params(labelsize=12.2)
    ax.set_yticklabels([str(round(i,1)) for i in ax.get_yticks()], fontsize = 15)

    # Set labels and title
    plt.ylabel('Packets out-of-order (%)',fontsize=15)    
    #plt.xlabel('',fontsize=0)
    #plt.title('{}'.format(name_title), fontsize=17.5)

    plt.grid()  #just add this
    plt.legend([],[], frameon=False)
    ax3.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig("experiments/{}/nack.svg".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/nack.png".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/nack.pdf".format(experiment_name), bbox_inches='tight')
    plt.close()


    # PLOT 4 (FLOW DISTR)
    # Your list of 5 numbers and corresponding labels
    plt.figure(figsize=(7, 4.5))

    combined_data = []
    hue_list = []
    for idx, names in enumerate(labels):
        combined_data += all_data[idx]
        hue_list += [labels[idx]] * len(all_data[idx])

    # Create the violin plot
    my = sns.violinplot(x=hue_list, y=combined_data, cut=0)
    my.tick_params(labelsize=9.5)

    my.set_yticks(my.get_yticks())
    my.tick_params(labelsize=11)
    my.set_yticklabels([str(round(i,1)) for i in my.get_yticks()], fontsize = 15)
    my.set_axisbelow(True)
    sns.set_context("paper", rc={"axes.labelsize":11})

    plt.xlabel('SMaRTT Version'.format("a"),fontsize=16)
    plt.ylabel('Flow Completion Time (ms)',fontsize=15.5)
    
    my.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    plt.grid()  #just add this

    plt.savefig("experiments/{}/violin_fct.svg".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/violin_fct.png".format(experiment_name), bbox_inches='tight')
    plt.savefig("experiments/{}/violin_fct.pdf".format(experiment_name), bbox_inches='tight')
    plt.close()
    

def main():
    # General Exp Settings
    list_title_names = ["Inter-DC Permutation 2MiB", "Mixed Permutation 2MiB", "Incast Inter-DC", "Incast Intra-DC", "Alibaba Load Mixed", "Alibaba Load Inter-DC", "Alibaba Load Intra-DC"]
    list_custom_names = ["PermInter", "PermMixed", "IncastInter", "IncastIntra", "AliMixed", "AliInter", "AliIntra"]
    list_exp = ["perm_128_glob", "perm_128_both", "paper_incast_inter_large", "paper_incast_intra_large", "ali_mixed_large.cm", "ali_inter_large.cm", "ali_intra_large.cm"]
    list_topo = ["fat_tree_128_4os.topo", "fat_tree_128_4os.topo", "fat_tree_128_4os.topo", "fat_tree_128_4os.topo", "fat_tree_128_4os.topo", "fat_tree_128_4os.topo", "fat_tree_128_4os.topo"] 
    msg_sizes = [2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25, 2**25]
    # Print me the len of the 5 previous lists
    list_title_names = ["WebSearch Load Mixed", "WebSearch Load Intra", "WebSearch Load Inter", "Alibaba Load Mixed", "Alibaba Load Inter-DC", "Alibaba Load Intra-DC", "WebSearch Load Mixed", "WebSearch Load Intra", "WebSearch Load Inter", "Alibaba Load Mixed", "Alibaba Load Inter-DC", "Alibaba Load Intra-DC"]
    list_custom_names = ["WebMixed", "WebIntra", "WebInter", "AliMixed", "AliInter", "AliIntra"]
    list_exp = ["web_mixed_large.cm", "web_intra_large.cm", "web_inter_large.cm", "ali_mixed_large.cm", "ali_inter_large.cm", "ali_intra_large.cm"]

    list_custom_names = ["Web1", "Web2"]
    list_exp = ["web_mixed_large.cm", "web_inter_large.cm"]

    list_custom_names = ["IncastPaper"]
    list_exp = ["paper_incast_inter_large"]

    list_custom_names = ["WebInraLarge"]
    list_exp = ["web_intra_large.cm"]

    list_custom_names = ["Flowcut_Perm", "Flowcut_Perm_Staggered", "Flowcut_Web", "Flowcut_Mining", "FlowcutOS_Perm", "FlowcutOS_Perm_Staggered", "FlowcutOS_Web", "FlowcutOS_Mining"]
    list_topo = ["fat_tree_128.topo", "fat_tree_128.topo", "fat_tree_128.topo", "fat_tree_128.topo", "fat_tree_128_2os.topo", "fat_tree_128_2os.topo", "fat_tree_128_2os.topo", "fat_tree_128_2os.topo"]
    list_exp = ["perm_128_2", "perm_128_t", "test_web.txt", "test_ali.txt", "perm_128_2", "perm_128_t", "test_web.txt", "test_ali.txt"]

    list_custom_names = ["Flowcut_Perm", "Flowcut_Perm_Staggered", "Flowcut_Web", "Flowcut_Mining", "FlowcutOS_Perm", "FlowcutOS_Perm_Staggered", "FlowcutOS_Web", "FlowcutOS_Mining"]
    list_topo = ["fat_tree_128.topo", "fat_tree_128.topo", "fat_tree_128.topo", "fat_tree_128.topo", "fat_tree_128_2os.topo", "fat_tree_128_2os.topo", "fat_tree_128_2os.topo", "fat_tree_128_2os.topo"]
    list_exp = ["perm_128_2", "perm_128_t", "test_web.txt", "test_ali.txt", "perm_128_2", "perm_128_t", "test_web.txt", "test_ali.txt"]
    

    list_custom_names = ["FlowcutPaperAllToAll"]
    list_topo = ["fat_tree_128.topo"]
    list_exp = ["alltoall128"]
    print(len(list_custom_names))
    print(len(list_exp))
    print(len(list_topo))
    print(len(list_title_names))
    print(len(msg_sizes))
    for idx, item in enumerate(list_exp):
        print("Running Experiment Named {}".format(list_custom_names[idx]))
        run_experiment(list_custom_names[idx], list_exp[idx],  list_topo[idx], list_title_names[idx], msg_sizes[idx])


if __name__ == "__main__":
    main()