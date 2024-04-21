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

def create_subplot(subplot_name, type_plot, y_values, x_values, plot_title):
    subplot_name.set_title(
        label = plot_title,
        weight = 'bold',
        horizontalalignment = 'left',
        x = 0,
        y = 1.04
    )
    if type_plot == "global":
        subplot_name.bar(x_values - 0.4, y_values[0], width=0.4, edgecolor='black', linewidth=0.5) # offset of -0.4
        subplot_name.bar(x_values, y_values[1], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4
        subplot_name.bar(x_values + 0.4, y_values[2], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4
    elif type_plot == "host":
        subplot_name.bar(x_values - 0.6, y_values[0], width=0.4, edgecolor='black', linewidth=0.5) # offset of -0.4
        subplot_name.bar(x_values - 0.2, y_values[1], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4
        subplot_name.bar(x_values + 0.2, y_values[2], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4
        subplot_name.bar(x_values + 0.6, y_values[3], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4  
    if type_plot == "intra":
        subplot_name.bar(x_values - 0.4, y_values[0], width=0.4, edgecolor='black', linewidth=0.5) # offset of -0.4
        subplot_name.bar(x_values, y_values[1], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4
        subplot_name.bar(x_values + 0.4, y_values[2], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4

def subcategorybar(X, vals, width=0.8):
    n = len(vals)
    _X = np.arange(len(X))
    for i in range(n):
        print(len(vals[i]))
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

                    match = re.search('Number Groups: (\d+)', line)
                    if match:
                        num_groups = (int(match.group(1)))

                    match = re.search('routing=(\w+)', line)
                    if match:
                        routing_scheme = (str(match.group(1)))

                    match = re.search('defaultRouting=(\w+)', line)
                    if match:
                        routing_algo = (str(match.group(1)))

                    match = re.search("Total Cycle - (\d+) : (\d+)", line)
                    if match:
                        total_cycles[int(match.group(1))] = int(match.group(2))

                    match = re.search("Busy Port - (\d+) - (\d+) : (\d+)", line)
                    if match:
                        routers_data[int(match.group(1))][int(match.group(2))] = int(match.group(3))

            if is_bg:
                list_algo.append(routing_scheme + " " + routing_algo + str(1))
            else:
                list_algo.append(routing_scheme + " " + routing_algo)
            total_cycles = list(filter(None.__ne__, total_cycles))
            routers_data = list(filter(None.__ne__, routers_data))
            for i in range(0,len(routers_data)):
                routers_data[i] = list(filter(None.__ne__, routers_data[i]))
            
            port_utilization = [None] * len(total_cycles)

            temp_list = []

            list_ports = [None] * tot_ports
            for i in range (0, tot_ports):
                list_ports[i] = [None] * num_routers  

            for idx, val in enumerate(total_cycles):
                port_utilization[idx] = list()
                for j, port in enumerate(routers_data[idx]):
                    if int(total_cycles[idx]) == 0:
                        value = 0
                    else:
                        value = (routers_data[idx][j] / float(total_cycles[idx])) * 100
                    list_ports[j][idx] = value

            '''if (type_port == "global"):
                list_ports_wanted = list_ports[start_global:]
            elif (type_port == "host"):
                list_ports_wanted = list_ports[:start_intra]'''

            list_ports_global = list_ports[start_global:]
            list_ports_hosts = list_ports[:start_intra]
            list_ports_intra= list_ports[start_intra:start_global]

    return list_ports_global, list_ports_hosts, list_ports_intra, num_routers


parser = argparse.ArgumentParser()
parser.add_argument('--title', required=False, default="Global Links Port Occupancy per Router")
parser.add_argument('--type', required=False, default="global")
parser.add_argument('--without_bg', required=False, default="False")
args = parser.parse_args()
    
plot_type = str(args.type)

# Style Plot
plt.rc('font', size=11.0)          # controls default text sizes
plt.rc('axes', titlesize=9.0)     # fontsize of the axes title
plt.rc('axes', labelsize=9)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=6.3)    # fontsize of the tick labels
plt.rc('ytick', labelsize=7)    # fontsize of the tick labels
plt.rc('legend', fontsize=8.8)    # legend fontsize
plt.rc('figure', titlesize=9)  # fontsize of the figure title


#list_ports, list_algo = get_data_from_files("input_for_plots/parsed_csv/", plot_type)
list_ports_global, list_ports_hosts, list_intra, num_r = get_data_from_files("input_for_plots/parse/", "minimal", plot_type)
list_ports_global_ugal, list_ports_hosts_ugal, list_intra_ugal, num_r = get_data_from_files("input_for_plots/parse/", "ugal", plot_type)

x_l = []
print(num_r)
for i in range(0, num_r * 2):
    if (i % 2 == 0):
        x_l.append(i + 1)
print(x_l)
X = np.array(x_l)

labels = []
for i in range(0, num_r):
    labels.append("R {}".format(str(i)))

gs = gridspec.GridSpec(2, 3)
ax1 = plt.subplot(gs[0, 0])
ax2 = plt.subplot(gs[0, 1])
ax3 = plt.subplot(gs[0, 2])

ax4 = plt.subplot(gs[1, 0])
ax5 = plt.subplot(gs[1, 1])
ax6 = plt.subplot(gs[1, 2])

plt.suptitle("Shift (no last group) - Small MSG 10MB", weight = 'bold')
ax_lst = [ax1, ax2, ax3, ax4, ax5, ax6]

#Plot Minimal + Valiant
create_subplot(ax_lst[0], "global", list_ports_global, X, "Global Links Port Occupancy per Router")   
create_subplot(ax_lst[1], "host", list_ports_hosts, X, "Host-Router Links Port Occupancy per Router") 
create_subplot(ax_lst[2], "intra", list_intra, X, "Intra-Group Links Port Occupancy per Router") 

create_subplot(ax_lst[3], "global", list_ports_global_ugal, X, "Global Links Port Occupancy per Router")   
create_subplot(ax_lst[4], "host", list_ports_hosts_ugal, X, "Host-Router Links Port Occupancy per Router") 
create_subplot(ax_lst[5], "intra", list_intra_ugal, X, "Intra-Group Links Port Occupancy per Router") 


'''if plot_type == "global":
    plt.bar(X - 0.4, list_ports[0], width=0.4, color="blue", edgecolor='black', linewidth=1) # offset of -0.4
    plt.bar(X, list_ports[1], width=0.4, color="blue", edgecolor='black', linewidth=1) # offset of  0.4
    plt.bar(X + 0.4, list_ports[2], width=0.4, color="blue", edgecolor='black', linewidth=1) # offset of  0.4
elif plot_type == "host":
    plt.bar(X - 0.6, list_ports[0], width=0.4, edgecolor='black', linewidth=0.5) # offset of -0.4
    plt.bar(X - 0.2, list_ports[1], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4
    plt.bar(X + 0.2, list_ports[2], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4
    plt.bar(X + 0.6, list_ports[3], width=0.4, edgecolor='black', linewidth=0.5) # offset of  0.4'''

plt.gcf().set_size_inches(16, 8)

for subplot in ax_lst:
    subplot.set_facecolor(sharedValues.color_background_plot)

    # Title and Labels

    # xlabel
    subplot.set_xlabel(
        "Router Number",
    )
    # ylabel
    subplot.set_ylabel(
        "Port Occupancy (%)",
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
    subplot.set_xticks(X)
    subplot.set_xticklabels(labels)
    subplot.set_ylim(bottom=0)
    subplot.set_ylim(top=100)

ax3.text(33.5,55.5,"Minimal", size=16,
                           verticalalignment='center', rotation=270)
ax6.text(33.5,55.5,"UGAL", size=16,
                           verticalalignment='center', rotation=270)

plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
# Finally Show the plot
plt.show()


