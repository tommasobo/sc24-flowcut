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

class PortsInfo(object):
    num_hosts_per_router = 0
    num_routers = 0
    num_groups = 0
    num_intralink_ports = 0
    num_global_links = 0

    # The class "constructor" - It's actually an initializer 
    def __init__(self, num_hosts_per_router, num_routers, num_groups, num_intralink_ports,num_global_links):
        self.num_hosts_per_router = num_hosts_per_router
        self.num_routers = num_routers
        self.num_groups = num_groups
        self.num_intralink_ports = num_intralink_ports
        self.num_global_links = num_global_links

def create_subplot(subplot_name, type_plot, y_values, x_values, plot_title, portsInfo):
    if plot_title != "":
        subplot_name.set_title(
            label = plot_title,
            weight = 'bold',
            horizontalalignment = 'left',
            x = 0,
            y = 1.04
        )
    if type_plot == "global":
        subplot_name.bar(x_values - 0.6666, y_values[0], width=0.66667, edgecolor='black', color=sharedValues.color_global_ports[0] , linewidth=0.0) # offset of -0.4
        subplot_name.bar(x_values, y_values[1], width=0.66667, edgecolor='black', color=sharedValues.color_global_ports[1] , linewidth=0.0) # offset of  0.4
        subplot_name.bar(x_values + 0.6666, y_values[2], width=0.66667, edgecolor='black', color=sharedValues.color_global_ports[2] , linewidth=0.0) # offset of  0.4
    elif type_plot == "host":
        center_label_pos = np.linspace(3.2,204.8,64)
        sub_pos = np.linspace(0.1,3.3,17)
        sub_pos = sub_pos[:-1]
        sub_pos = sub_pos[::-1]
        for i in range (0, len(y_values)):
            minus = float(sub_pos[i])
            subplot_name.bar(center_label_pos - minus, y_values[i], color=sharedValues.color_host_ports, width=0.2, linewidth=0.0) # offset of -0.4
    if type_plot == "intra":
        center_label_pos = np.linspace(3,192,64)
        sub_pos = np.linspace(0.1,3.1,16)
        sub_pos = sub_pos[:-1]
        sub_pos = sub_pos[::-1]
        print(center_label_pos)
        print(sub_pos)
        for i in range (0, len(y_values)):
            minus = float(sub_pos[i])
            subplot_name.bar(center_label_pos - minus, y_values[i], color=sharedValues.color_intra_ports, width=0.2, linewidth=0.0) # offset of -0.4

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

                    match = re.search("Total Altenrative Cycle - (\d+) : (\d+)", line)
                    if match:
                        total_cycles[int(match.group(1))] = int(match.group(2))

                    match = re.search("Busy Alternative Port - (\d+) - (\d+) : (\d+)", line)
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
            
            list_ports = [None] * tot_ports
            for i in range (0, tot_ports):
                list_ports[i] = [None] * num_routers  

            for idx, val in enumerate(total_cycles):
                for j, port in enumerate(routers_data[idx]):
                    if int(total_cycles[idx]) == 0:
                        value = 0
                    else:
                        value = (routers_data[idx][j] / float(total_cycles[idx])) * 100
                    list_ports[j][idx] = value

            list_ports_global = list_ports[start_global:]
            list_ports_hosts = list_ports[:start_intra]
            list_ports_intra= list_ports[start_intra:start_global]

            portsInfo = PortsInfo(int(start_intra), int(num_routers), int(num_groups), int(tot_ports - start_global), int(start_global - start_intra))

    return list_ports_global, list_ports_hosts, list_ports_intra, portsInfo


parser = argparse.ArgumentParser()
parser.add_argument('--title', required=False, default="Global Links Port Occupancy per Switch")
parser.add_argument('--type', required=False, default="global")
parser.add_argument('--without_bg', required=False, default="False")
args = parser.parse_args()
    
plot_type = str(args.type)

# Style Plot
plt.rc('font', size=11.0)          # controls default text sizes
plt.rc('axes', titlesize=9.0)     # fontsize of the axes title
plt.rc('axes', labelsize=9)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=7)    # fontsize of the tick labels
plt.rc('legend', fontsize=7)    # legend fontsize
plt.rc('figure', titlesize=9)  # fontsize of the figure title


#list_ports, list_algo = get_data_from_files("input_for_plots/parsed_csv/", plot_type)
list_ports_global, list_ports_hosts, list_intra, portsInfo = get_data_from_files("input_for_plots/parse/", "min", plot_type)
list_ports_global_ugal, list_ports_hosts_ugal, list_intra_ugal, portsInfo = get_data_from_files("input_for_plots/parse/", "ugal", plot_type)
list_ports_global_valiant, list_ports_hosts_valiant, list_intra_valiant, portsInfo = get_data_from_files("input_for_plots/parse/", "sling", plot_type)

x_l = []
print(portsInfo.num_routers)
for i in range(0, portsInfo.num_routers * 2):
    if (i % 2 == 0):
        x_l.append(i + 1)
print(x_l)
X = np.array(x_l)

labels = []
for i in range(0, portsInfo.num_routers):
    labels.append("R {}".format(str(i)))

gs = gridspec.GridSpec(3, 3)
ax1 = plt.subplot(gs[0, 0])
ax2 = plt.subplot(gs[0, 1])
ax3 = plt.subplot(gs[0, 2])

ax4 = plt.subplot(gs[1, 0])
ax5 = plt.subplot(gs[1, 1])
ax6 = plt.subplot(gs[1, 2])

ax7 = plt.subplot(gs[2, 0])
ax8 = plt.subplot(gs[2, 1])
ax9 = plt.subplot(gs[2, 2])

plt.suptitle("Ports Occupancy Adversarial Traffic", weight = 'bold')
ax_lst = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]

#Minimal
create_subplot(ax_lst[0], "global", list_ports_global, X, "Global Links Port Occupancy per Switch", portsInfo)   
create_subplot(ax_lst[1], "host", list_ports_hosts, X, "Host-Switch Links Port Occupancy per Switch", portsInfo) 
create_subplot(ax_lst[2], "intra", list_intra, X, "Intra-Group Links Port Occupancy per Switch", portsInfo) 

#Valiant
create_subplot(ax_lst[3], "global", list_ports_global_valiant, X, "", portsInfo)   
create_subplot(ax_lst[4], "host", list_ports_hosts_valiant, X, "", portsInfo) 
create_subplot(ax_lst[5], "intra", list_intra_valiant, X, "", portsInfo) 

#UGAL
create_subplot(ax_lst[6], "global", list_ports_global_ugal, X, "", portsInfo)   
create_subplot(ax_lst[7], "host", list_ports_hosts_ugal, X, "", portsInfo) 
create_subplot(ax_lst[8], "intra", list_intra_ugal, X, "", portsInfo) 

plt.gcf().set_size_inches(16, 9.8)

for idx, subplot in enumerate(ax_lst):
    subplot.set_facecolor(sharedValues.color_background_plot)

    subplot.set_ylim(bottom=0)
    subplot.set_ylim(top=100)
    if idx == 0:
        # legend
        legend_dict = {'First Global Port' : sharedValues.color_global_ports[0], 'Second Global Port' : sharedValues.color_global_ports[1], 'Third Global Port' : sharedValues.color_global_ports[2]}
        patchList = []
        for key in legend_dict:
                data_key = mpatches.Patch(color=legend_dict[key], label=key)
                patchList.append(data_key)

        subplot.legend(handles=patchList)

    # xlabel
    if (idx >= 6):
        subplot.set_xlabel(
            "Switch",
        )
    if (idx <= 2):
        # ylabel
        subplot.set_ylabel(
            "Number of cycles a given port was busy (%)",
            horizontalalignment='left',
            rotation = 0,
        )
        subplot.yaxis.set_label_coords(0, 1.01)

    # Host Graphs
    if idx == 1 or idx == 4 or idx == 7:
        width_one_router = 3.2
        subplot.axvline(x=width_one_router * 16 * 1, color='grey', ls=':', alpha=0.5)
        subplot.axvline(x=width_one_router * 16 * 2, color='grey', ls=':', alpha=0.5)
        subplot.axvline(x=width_one_router * 16 * 3, color='grey', ls=':', alpha=0.5)
        half_size = 3.2 * 16 / 2
        full_size = 3.2 * 16
        x_pos_label = [half_size, half_size+full_size, half_size+(full_size * 2), half_size+(full_size * 3)]
        x_label_text = []
        for i in range (1, 5, 1):
            x_label_text.append("Switches Group {}".format(i))

        subplot.set_xticks(x_pos_label)
        subplot.set_xticklabels(x_label_text)
        #subplot.set_ylim(top=10)
        subplot.set_xlim(left=0)
        subplot.set_xlim(right=205)

    # Intra Graphs
    if idx == 2 or idx == 5 or idx == 8:
        subplot.axvline(x=48 * 1, color='grey', ls=':', alpha=0.5)
        subplot.axvline(x=48 * 2, color='grey', ls=':', alpha=0.5)
        subplot.axvline(x=48 * 3, color='grey', ls=':', alpha=0.5)
        half_size = 3 * 16 / 2
        full_size = 3 * 16
        x_pos_label = [half_size, half_size+full_size, half_size+(full_size * 2), half_size+(full_size * 3)]
        x_label_text = []
        for i in range (1, 5, 1):
            x_label_text.append("Switches Group {}".format(i))

        subplot.set_xticks(x_pos_label)
        subplot.set_xticklabels(x_label_text)
        #subplot.set_ylim(top=30)
        subplot.set_xlim(left=0)
        subplot.set_xlim(right=192)

    # Global Graphs
    if idx == 0 or idx == 3 or idx == 6:
        subplot.axvline(x=32 * 1, color='grey', ls=':', alpha=0.88)
        subplot.axvline(x=32 * 2, color='grey', ls=':', alpha=0.88)
        subplot.axvline(x=32 * 3, color='grey', ls=':', alpha=0.88)
        subplot.set_xlim(left=0)
        subplot.set_xlim(right=128)
        x_pos_label = [16, 16+32, 16+64, 16+96]
        x_label_text = []
        for i in range (1, 5, 1):
            x_label_text.append("Switches Group {}".format(i))

        subplot.set_xticks(x_pos_label)
        subplot.set_xticklabels(x_label_text)
        subplot.set_ylim(top=100)

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
        
'''
ax3.text(194.5,16.5,"Minimal", size=16,
                           verticalalignment='center', rotation=270)
ax6.text(194.5,16.5,"Valiant", size=16,
                           verticalalignment='center', rotation=270)
ax9.text(194.5,16.5,"UGAL", size=16,
                           verticalalignment='center', rotation=270)

'''
ax3.text(194.5,16.5,"Minimal", size=16,
                           verticalalignment='center', rotation=270)
ax6.text(194.5,16.5,"UGAL-L + Slingshot", size=16,
                           verticalalignment='center', rotation=270)
ax9.text(194.5,16.5,"UGAL-L", size=16,
                           verticalalignment='center', rotation=270)


plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
# Finally Show the plot
plt.show()