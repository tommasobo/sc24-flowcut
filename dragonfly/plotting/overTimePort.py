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

def create_subplot(subplot_name, row, y_values, plot_title, portsInfo, runtime):

    for i in range(len(y_values)):
        for j in range(len(y_values[0])):
        #print("Positive {} out of {}".format(sum(np.array(ports[i])>0), len(ports[i])))
            if (i <= 15):
                mycolor = sharedValues.color_background_traffic
                myalpaha = 0.75
                mywidth = 7
            elif (i >= 16 and i <= 31):
                myalpaha = 0.70
                mycolor = sharedValues.color_main_traffic
                mywidth = 5
            elif (i >= 32 and i <= 47):
                mycolor = "#9767BA"#"#90564C"
                myalpaha = 0.42
                mywidth = 3
            else:
                mycolor = sharedValues.color_host_ports
                myalpaha = 0.2
                mywidth = 1.30
            if 1==1:
                subplot_name.plot(y_values[i][j], color=mycolor, alpha=myalpaha, linewidth=mywidth)
            else:
                subplot_name.plot(y_values[i][j], color=mycolor, alpha=myalpaha)
    subplot_name.set_ylim(top=101)
    x_label_text = np.linspace(0.0,runtime,6)
    x_pos_label = np.linspace(0.0,len(y_values[0][0]),6)
    x_label_text = [int(item) for item in x_label_text]
    x_pos_label = [(item) for item in x_pos_label]

    subplot_name.set_xticks(x_pos_label)
    subplot_name.set_xticklabels(x_label_text)
    if (row == 0):
        #subplot_name.set_xlabel(plot_title)
        #subplot_name.set_ylabel('Utilization (%)')
        subplot_name.set_title(plot_title,
                weight = 'bold',
                horizontalalignment = 'left',
                x = 0,
                y = 1.065
            )
        
        # legend
        legend_dict = {'First Group' : sharedValues.color_background_traffic, 'Second Group' : sharedValues.color_main_traffic, 'Third Group' : "#9767BA", 'Fourth Group' : sharedValues.color_host_ports}
        patchList = []
        for key in legend_dict:
                data_key = mpatches.Patch(color=legend_dict[key], label=key)
                patchList.append(data_key)

        my_lgd = subplot_name.legend(handles=patchList, loc='upper right')
        my_lgd.legendHandles[0].set_linewidth(2.0)
        my_lgd.legendHandles[1].set_linewidth(1.0)
        my_lgd.legendHandles[2].set_linewidth(0.5)
        my_lgd.legendHandles[3].set_linewidth(0.25)

    # Average
    sum = [0] * 4
    count = [0] * 4
    list_final = [[] for i in range(4)]
    list_alpha = [0.80, 0.60, 0.40, 0.20]
    list_style = ["--", ':', '-.' , '--']
    list_color = [sharedValues.color_background_traffic, sharedValues.color_main_traffic, "#9767BA", sharedValues.color_host_ports]
    for i in range(len(y_values[0][0])):
        for j in range(len(y_values)):
            for k in range(len(y_values[0])):
                if (j < 16):
                    sum[0] += y_values[j][k][i]
                    count[0] += 1
                elif (j >= 16 and j <= 31):
                    sum[1] += y_values[j][k][i]
                    count[1] += 1
                elif (j >= 32 and j <= 47):
                    sum[2] += y_values[j][k][i]
                    count[2] += 1
                else:
                    sum[3] += y_values[j][k][i]
                    count[3] += 1

        for i in range(4):
            list_final[i].append(sum[i] / count[i])
            count[i] = 0
            sum[i] = 0

    #for i in range(4):
        #subplot_name.plot(list_final[i], color=list_color[i], alpha=0.9, linewidth = 4, linestyle=list_style[i])


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
                        ports = [None] * 64
                        hostports = [None] * 64
                        intraports = [None] * 64
                        for i in range(0,64):
                            ports[i] = [None] * 3
                            hostports[i] = [None] * 16
                            intraports[i] = [None] * 15

                        for i in range(0,64):
                            for j in range(0,3):
                                ports[i][j] = []
                            for k in range (0,16):
                                hostports[i][k] = []
                                if (k != 15):
                                    intraports[i][k] = []
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

                    match = re.search('Runtime: (\d+)', line)
                    if match:
                        runtime = (int(match.group(1)))

                    match = re.search("Total Cycle - (\d+) : (\d+)", line)
                    if match:
                        total_cycles[int(match.group(1))] = int(match.group(2))

                    match = re.search("Busy Port - (\d+) - (\d+) : (\d+)", line)
                    if match:
                        routers_data[int(match.group(1))][int(match.group(2))] = int(match.group(3))

                    match = re.search("Port Utilization is (\d+) (\d+) (\d+)", line)
                    if match and int(match.group(2)) >= 31:
                        ports[int(match.group(1))][int(match.group(2)) - 31].append(int(match.group(3)) / 100)
                    elif match and int(match.group(2)) <= 15:
                        hostports[int(match.group(1))][int(match.group(2))].append(int(match.group(3)) / 100)
                    elif match and int(match.group(2)) <= 30 and int(match.group(2)) >= 16:
                        intraports[int(match.group(1))][int(match.group(2)) - 16].append(int(match.group(3)) / 100)


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

    return list_ports_global, list_ports_hosts, list_ports_intra, portsInfo, ports, hostports, intraports, runtime


parser = argparse.ArgumentParser()
parser.add_argument('--title', required=False, default="Global Links Port Occupancy per Switch")
parser.add_argument('--type', required=False, default="global")
parser.add_argument('--without_bg', required=False, default="False")
args = parser.parse_args()
    
plot_type = str(args.type)

# Style Plot
plt.rc('font', size=11.6)          # controls default text sizes
plt.rc('axes', titlesize=12.0)     # fontsize of the axes title
plt.rc('figure', titlesize=15.5)     # fontsize of the axes title
plt.rc('axes', labelsize=11.6)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=10.5)    # legend fontsize


#list_ports, list_algo = get_data_from_files("input_for_plots/parsed_csv/", plot_type)
list_ports_global, list_ports_hosts, list_intra, portsInfo, ports, hostports, intraports, runtime = get_data_from_files("input_for_plots/parse/", "min", plot_type)
list_ports_global_ugal, list_ports_hosts_ugal, list_intra_ugal, portsInfo, ports_ugal, hostports_ugal, intraports_ugal, runtime2 = get_data_from_files("input_for_plots/parse/", "aries", plot_type)
list_ports_global_valiant, list_ports_hosts_valiant, list_intra_valiant, portsInfo, ports_3, hostports_3, intraports_3, runtime3 = get_data_from_files("input_for_plots/parse/", "flow2", plot_type)
list_ports_global_sling, list_ports_hosts_sling, list_intra_sling, portsInfo, ports_sling, hostports_sling, intraports_sling, runtimesling = get_data_from_files("input_for_plots/parse/", "sling", plot_type)


gs = gridspec.GridSpec(4, 3)
ax1 = plt.subplot(gs[0, 0])
ax2 = plt.subplot(gs[0, 1])
ax3 = plt.subplot(gs[0, 2])

ax4 = plt.subplot(gs[1, 0])
ax5 = plt.subplot(gs[1, 1])
ax6 = plt.subplot(gs[1, 2])

ax7 = plt.subplot(gs[2, 0])
ax8 = plt.subplot(gs[2, 1])
ax9 = plt.subplot(gs[2, 2])

ax10 = plt.subplot(gs[3, 0])
ax11 = plt.subplot(gs[3, 1])
ax12 = plt.subplot(gs[3, 2])

plt.suptitle("Ports Occupancy Over Time - Uniform Traffic motif (4 MiB)", weight = 'bold')
ax_lst = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12]

#Minimal
create_subplot(ax_lst[0], 0, ports, "Global Links Port Occupancy by Group", portsInfo, runtime)   
create_subplot(ax_lst[1], 0, hostports, "Host-Switch Links Port Occupancy by Group", portsInfo, runtime) 
create_subplot(ax_lst[2], 0, intraports, "Intra-Group Links Port Occupancy by Group", portsInfo, runtime) 

#Valiant
create_subplot(ax_lst[3], 1, ports_ugal, "", portsInfo, runtime2)   
create_subplot(ax_lst[4], 1, hostports_ugal, "", portsInfo, runtime2) 
create_subplot(ax_lst[5], 1, intraports_ugal, "", portsInfo, runtime2) 

#UGAL
create_subplot(ax_lst[6], 2, ports_3, "", portsInfo, runtime3)   
create_subplot(ax_lst[7], 2, hostports_3, "", portsInfo, runtime3) 
create_subplot(ax_lst[8], 2, intraports_3, "", portsInfo, runtime3) 

#SLING
create_subplot(ax_lst[9], 2, ports_sling, "", portsInfo, runtimesling)   
create_subplot(ax_lst[10], 2, hostports_sling, "", portsInfo, runtimesling) 
create_subplot(ax_lst[11], 2, intraports_sling, "", portsInfo, runtimesling) 

plt.gcf().set_size_inches(15, 10)

for idx, subplot in enumerate(ax_lst):
    subplot.set_facecolor(sharedValues.color_background_plot)

    subplot.set_ylim(bottom=0)
    subplot.set_ylim(top=101)

    # xlabel
    if (idx >= 9):
        subplot.set_xlabel(
            "Program Time (μs)",
        )
    if (idx <= 2):
        # ylabel
        subplot.set_ylabel(
            "Port Occupancy (%)",
            horizontalalignment='left',
            rotation = 0,
        )
        subplot.yaxis.set_label_coords(0, 1.01)

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

    subplot.xaxis.set_tick_params(labelsize=11.6)
    subplot.yaxis.set_tick_params(labelsize=11.6)
    

ax3.text(len(ports[0][0]) + 0.02,46.5,"ECMP", size=17,
                           verticalalignment='center', rotation=270)
ax6.text(len(ports_ugal[0][0]) + 0.09,46.5,"UGAL-4", size=17,
                           verticalalignment='center', rotation=270)
ax9.text(len(ports_3[0][0]) + 0.1,46.5,"Flowlet Balanced", size=14.5,
                           verticalalignment='center', rotation=270)
ax12.text(len(ports_sling[0][0]) + 0.1,46.5,"Slingshot", size=17,
                           verticalalignment='center', rotation=270)


plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
# Finally Show the plot
plt.show()