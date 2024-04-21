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
from datetime import datetime
import matplotlib.patches as mpatches
from more_itertools import sort_together
import numpy
from matplotlib.pyplot import figure
import sharedValues


def fix_names(tmp):
    for idx, item in enumerate(tmp):
        if item == "default minimal":
            tmp[idx] = "ECMP" 
        elif item == "default ugal":
            tmp[idx] = "Default" 
        elif item == "default valiant":
            tmp[idx] = "Default" 
        elif item == "default adaptive":
            tmp[idx] = "Default" 
        elif item == "flowlet ugal":
            tmp[idx] = "Flowlet Switching" 
        elif item == "flowlet valiant":
            tmp[idx] = "Flowlet Switching" 
        elif item == "flowlet adaptive":
            tmp[idx] = "Flowlet Switching" 
        elif item == "slingshot ugal":
            tmp[idx] = "Slingshot" 
        elif item == "slingshot valiant":
            tmp[idx] = "Slingshot" 
        elif item == "slingshot adaptive":
            tmp[idx] = "Slingshot" 

def create_subplot(subplot_name, subplot_title, list_minimal, list_minimal_name, list_data_algo, list_name_algo, color):
    #Plot Minimal + UGAL - Aries
    subplot_name.set_title(label = str(subplot_title))
    subplot_name.set_xticks(range(1,len(list_data_algo) + 2))
    tmp_list = []
    tmp_list.extend(list_minimal)
    tmp_list.extend(list_data_algo)
    tmp_list_name = []
    tmp_list_name.extend(list_minimal_name)
    tmp_list_name.extend(list_name_algo)
    list_quantiles = []
    for ele in tmp_list_name:
        list_quantiles.append([0.99])
    violin_parts = subplot_name.violinplot(tmp_list, showmedians=True, points=500, quantiles=list_quantiles)
    for idx, vp in enumerate(violin_parts['bodies']):
        if (idx == 0):
            vp.set_facecolor("#9b59b6")
            vp.set_edgecolor("#9b59b6")
            vp.set_alpha(0.6)
        else:
            vp.set_facecolor(color)
            vp.set_edgecolor(color)
            vp.set_alpha(0.6)
    fix_names(tmp_list_name)
    # Make the violin body blue with a red border:
    for partname in ('cbars','cmins','cmaxes','cmedians','cquantiles'):
        vp = violin_parts[partname]
        vp.set_edgecolor(sharedValues.color_violin_symbols)
        vp.set_linewidth(1.6)
        vp.set_alpha(0.75)
    subplot_name.set_xticklabels(tmp_list_name)   

def main():
    for root, dirs, files in os.walk("input_for_plots/parse_dist_bg/"):
        list_algo = []
        violin_data = list()
        for file in sorted(files):
            list_latencies = []
            list_hops = []
            num_pkts = 0
            num_ooo = 0

            data = []
            num_ports = 22
            total_cycles = [None] * 1000
            routers_data = [None] * 1000
            for i in range(0,1000):
                routers_data[i] = [None] * 1000

            port_utilization = list()
            routing_scheme = ""
            routing_algo = ""
            with open("input_for_plots/parse_dist_bg/" + file) as fp:
                Lines = fp.readlines()
                for line in Lines:

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

            list_algo.append(routing_scheme + " " + routing_algo)
            total_cycles = list(filter(None.__ne__, total_cycles))
            routers_data = list(filter(None.__ne__, routers_data))
            for i in range(0,len(routers_data)):
                routers_data[i] = list(filter(None.__ne__, routers_data[i]))
            
            port_utilization = [None] * len(total_cycles)

            temp_list = []

            for idx, val in enumerate(total_cycles):
                port_utilization[idx] = list()
                for j, port in enumerate(routers_data[idx]):
                    value = (routers_data[idx][j] / float(total_cycles[idx])) * 100
                    port_utilization[idx].append(value)
                    temp_list.append(value)


            violin_data.append(temp_list)

    #size
    plt.rc('font', size=11.0)          # controls default text sizes
    plt.rc('axes', titlesize=11.0)     # fontsize of the axes title
    plt.rc('axes', labelsize=11)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
    plt.rc('legend', fontsize=8.8)    # legend fontsize
    plt.rc('figure', titlesize=9)  # fontsize of the figure title

    # parse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=False, default="Performance of different routing algorithms in ResNet 320 Nodes + No Background Traffic")
    parser.add_argument('--csv', required=False)
    parser.add_argument('--out', required=False)
    parser.add_argument('--showplot', action='store_const', const=True)
    parser.add_argument('--type', required=False, default="latency")
    args = parser.parse_args()
    # init

    list_ugal = []
    list_ugal_name = []

    list_ugal_aries = []
    list_ugal_name_aries = []

    list_valiant = []
    list_name_valiant = []

    list_minimal = []
    list_minimal_name = []

    for idx, ele in enumerate(list_algo):
        if ("ugal" in ele):
            list_ugal_name.append(ele)
            list_ugal.append(violin_data[idx])
        elif ("valiant" in ele):
            list_name_valiant.append(ele)
            list_valiant.append(violin_data[idx])
        elif ("adaptive" in ele):
            list_ugal_name_aries.append(ele)
            list_ugal_aries.append(violin_data[idx])
        elif ("minimal" in ele):
            list_minimal_name.append(ele)
            list_minimal.append(violin_data[idx])


    # Create Grid for subplots
    gs = gridspec.GridSpec(2, 4)
    ax1 = plt.subplot(gs[0, 0:2])
    ax2 = plt.subplot(gs[0,2:])
    ax3 = plt.subplot(gs[1,1:3])
    plt.suptitle("Occupancy per port", fontsize="x-large", weight = 'bold')
    ax_lst = [ax1,ax2,ax3]
    flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e"]
    minimal_color = "#2ecc71"

    #Plot Minimal + Valiant
    create_subplot(ax_lst[0], "Valiant routing with ECMP baseline", list_minimal, list_minimal_name, list_valiant, list_name_valiant, "#3498db")   
    #Plot Minimal + UGAL
    create_subplot(ax_lst[1], "UGAL routing with ECMP baseline", list_minimal, list_minimal_name, list_ugal, list_ugal_name, "#2ecc71") 
    #Plot Minimal + UGAL - Aries
    create_subplot(ax_lst[2], "UGAL-Aries routing with ECMP baseline", list_minimal, list_minimal_name, list_ugal_aries, list_ugal_name_aries, "#e74c3c") 

    #Set figure size to be large
    plt.gcf().set_size_inches(14, 8)

    for subplot in ax_lst:
        subplot.set_facecolor(sharedValues.color_background_plot)
        # info
        title = "?"
        xlabel = "?"
        ylabel = "?"

        # Title and Labels
        title = subplot.get_title()
        subplot.set_title(
            label = str(title),
            weight = 'bold',
            horizontalalignment = 'left',
            x = 0,
            y = 1.06
        )
        # xlabel
        subplot.set_xlabel(
            "Routing Scheme",
        )
        # ylabel
        subplot.set_ylabel(
            "Ports Occupancy (%)",
            horizontalalignment='left',
            rotation = 0,
        )
        subplot.yaxis.set_label_coords(0, 1.02)
        subplot.grid(axis='y', color='w', linewidth=2, linestyle='-')
        subplot.set_axisbelow(True)
        # hide ticks y-axis
        subplot.tick_params(axis='y', left=False, right=False)
        # spines
        subplot.spines["top"].set_visible(False)
        subplot.spines["right"].set_visible(False)
        subplot.spines["left"].set_visible(False)
        # For Runtime Graphs
        subplot.set_yscale('linear')
        subplot.yaxis.set_tick_params(labelsize=9)
        subplot.xaxis.set_tick_params(labelsize=9)

        subplot.set_ylim(bottom=0)
        subplot.set_ylim(top=100)
    plt.minorticks_off()

    # Save Plot to folder giving it a custom name based on input and timestamp
    plt.tight_layout()
    Path("plots/png").mkdir(parents=True, exist_ok=True)
    Path("plots/pdf").mkdir(parents=True, exist_ok=True)
    file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
    plt.savefig(Path("plots/png") / (str("Distribution Occupancy") + file_name))
    plt.savefig(Path("plots/pdf") / (str("Distribution Occupancy") + file_name + ".pdf"))
    # Finally Show the plot
    plt.show()

if __name__ == "__main__":
    main()