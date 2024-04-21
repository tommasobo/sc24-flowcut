import re
import os
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.gridspec as gridspec
from pathlib import Path    
from matplotlib.colors import ListedColormap
import seaborn as sns
import matplotlib.patches
from matplotlib.lines import Line2D
from datetime import datetime
import matplotlib.patches as mpatches
from more_itertools import sort_together
import numpy
from matplotlib.pyplot import figure
import sharedValues   


def subcategorybar(X, vals, width=0.8):
    n = len(vals)
    _X = np.arange(len(X))
    for i in range(n):
        plt.bar(_X - width/2. + i/float(n)*width, vals[i], 
                width=width/float(n), align="edge")   
    #plt.xticks(_X, X)

    
def get_data_from_files(path_dir, type_algo, type_port, is_bg=False):
    for root, dirs, files in os.walk(path_dir):
        list_algo = []
        violin_data = list()
        for file in sorted(files):
            if (type_algo not in file):
                continue
            data = []
            tot_ports = 0
            start_host = 0
            start_intra = 0
            start_global = 0
            routers_per_group = 0
            num_groups = 0
            num_routers = 0
            total_cycles = []
            routers_data = []
    
            port_utilization = list()
            routing_scheme = ""
            routing_algo = ""
            with open(path_dir + file) as fp:
                Lines = fp.readlines()
                for line in Lines:

                    match = re.search('Total Ports: (\d+)', line)
                    if match:
                        tot_ports = (int(match.group(1)))

                    match = re.search('Intra-Group Ports: (\d+)', line)
                    if match:
                        start_intra = (int(match.group(1)))

                    match = re.search('Global Ports: (\d+)', line)
                    if match:
                        start_global = (int(match.group(1)))

                    match = re.search('Routers per Group: (\d+)', line)
                    if match:
                        routers_per_group = (int(match.group(1)))
                        # Not the cleanest thing, could allocate custom number of ports, routers
                        num_routers = int(routers_per_group) * int(num_groups)
                        total_cycles = [None] * num_routers
                        routers_data = [None] * num_routers
                        for i in range(0,num_routers):
                            routers_data[i] = [None] * int(tot_ports)

                        time_slot = [None] * 10000 #10k time slots
                        for i in range(0, len(time_slot)):
                            time_slot[i] = list()

                    match = re.search('Number Groups: (\d+)', line)
                    if match:
                        num_groups = (int(match.group(1)))

                    match = re.search('routing=(\w+)', line)
                    if match:
                        routing_scheme = (str(match.group(1)))

                    match = re.search('defaultRouting=(\w+)', line)
                    if match:
                        routing_algo = (str(match.group(1)))

                    if (type_port == "host"):
                        match = re.search("Th: (\d+) (\d+) (\d+\.\d+)", line)
                        if match:
                            #routers_data[int(match.group(1))][int(match.group(2))] = int(match.group(3))
                            time_slot[int(match.group(1))].append(float(match.group(3)))
                    elif (type_port == "global"):
                        match = re.search("ThG Time, Port, Rtr: (\d+) (\d+) (\d+) (\d+\.\d+)", line)
                        if match:
                            #routers_data[int(match.group(1))][int(match.group(2))] = int(match.group(3))
                            time_slot[int(match.group(1))].append(float(match.group(4)))
                    elif (type_port == "intra"):
                        match = re.search("ThI Time, Port, Rtr: (\d+) (\d+) (\d+) (\d+\.\d+)", line)
                        if match:
                            #routers_data[int(match.group(1))][int(match.group(2))] = int(match.group(3))
                            time_slot[int(match.group(1))].append(float(match.group(4)))

            if is_bg:
                list_algo.append(routing_scheme + " " + routing_algo + str(1))
            else:
                list_algo.append(routing_scheme + " " + routing_algo)

            time_slot = list(filter(None.__ne__, time_slot))


            x_list = []
            y_list = []
            
            for idx, value in enumerate(time_slot):
                if (len(time_slot[idx]) > 0):
                    x_list.append(idx)
                    if routing_algo == "valiant" and (type_port == "global"):
                        print(time_slot[idx])
                    y_list.append(numpy.mean(time_slot[idx]))


    return x_list[1:-1], y_list[1:-1]


parser = argparse.ArgumentParser()
parser.add_argument('--title', required=False, default="Global Links Port Occupancy per Router")
parser.add_argument('--type', required=False, default="global")
parser.add_argument('--without_bg', required=False, default="False")
args = parser.parse_args()
    
plot_type = str(args.type)

# Style Plot
plt.rc('font', size=11.0)          # controls default text sizes
plt.rc('axes', titlesize=11.0)     # fontsize of the axes title
plt.rc('axes', labelsize=11)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('legend', fontsize=8.8)    # legend fontsize
plt.rc('figure', titlesize=13)  # fontsize of the figure title


#list_ports, list_algo = get_data_from_files("input_for_plots/parsed_csv/", plot_type)
#Hosts
list_x, list_y = get_data_from_files("input_for_plots/parse/", "minimal", "host")
list_x_ugal, list_y_ugal = get_data_from_files("input_for_plots/parse/", "ugal", "host")
list_x_ugaal, list_y_ugaal = get_data_from_files("input_for_plots/parse/", "adaptive", "host")
list_x_valiant, list_y_valiant = get_data_from_files("input_for_plots/parse/", "valiant", "host")


'''print(list_x)
print(list_y)

print(list_x_intra)
print(list_y_intra)

print(list_x_global)
print(list_y_global)'''

gs = gridspec.GridSpec(1, 1)
ax1 = plt.subplot(gs[0, 0])


ax1.set_title("Average Throughput Hosts -> Router | Shift+1 10 MB", weight = 'bold',
    horizontalalignment = 'left',
    x = 0,
    y = 1.04)


ax_lst = [ax1]

ax1.plot(list_x, list_y, label="Minimal") # offset of -0.4
ax1.plot(list_x_ugal, list_y_ugal, label="UGAL") # offset of -0.4
ax1.plot(list_x_ugaal, list_y_ugaal, label="UGAL-Aries") # offset of -0.4
ax1.plot(list_x_valiant, list_y_valiant, label="Valiant") # offset of -0.4

plt.gcf().set_size_inches(16, 8)

for subplot in ax_lst:
    subplot.set_facecolor(sharedValues.color_background_plot)

    # Title and Labels

    # xlabel
    subplot.set_xlabel(
        "Program Completion (%)",
    )
    # ylabel
    subplot.set_ylabel(
        "Average Throughput (Gb/s)",
        horizontalalignment='left',
        rotation = 0,
    )
    subplot.yaxis.set_label_coords(0, 1.02)

    # For Runtime Graphs
    subplot.set_yscale('linear')
    plt.minorticks_off()

    # y grid
    subplot.grid(axis='y', color='w', linewidth=2, linestyle='-')
    subplot.set_axisbelow(True)
    # hide ticks y-axis
    subplot.tick_params(axis='y', left=False, right=False)
    # spines
    subplot.spines["top"].set_visible(False)
    subplot.spines["right"].set_visible(False)
    subplot.spines["left"].set_visible(False)
    #subplot.set_xticks(X)
    #subplot.set_xticklabels(labels)
    subplot.set_ylim(bottom=0)
    subplot.set_ylim(top=10)

    max = 80
    subplot.set_xlim(left=0)
    '''subplot.set_xlim(right=300)
    ax1.xaxis.set_major_locator(plt.MaxNLocator(5))
    num_xticks = len(subplot.get_xticks())
    print(num_xticks)
    print(subplot.get_xticks())

    list_a = [0, 20, 40, 60, 80, 100]
    subplot.set_xticks(subplot.get_xticks())
    subplot.set_xticklabels(list_a)
    
    new_x = np.linspace(0, 100, num=max).tolist()'''

    '''subplot.set_xticks(new_x)
    new_x = [int(a) for a in new_x]
    xticks = subplot.get_xticklabels()
    for idx, value in enumerate(xticks):
        if (idx == 0):
             xticks[idx] = "0"
        elif (idx == len(xticks) - 1):
             xticks[idx] = "100"
        else:
            xticks[idx] = ""
    subplot.set_xticklabels(xticks)
    ax1.xaxis.set_major_locator(plt.MaxNLocator(3))'''



'''ax3.text(33.5,55.5,"Minimal", size=16,
                           verticalalignment='center', rotation=270)
ax6.text(33.5,55.5,"UGAL", size=16,
                           verticalalignment='center', rotation=270)'''
plt.legend(fontsize=11)
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
# Finally Show the plot
plt.show()


