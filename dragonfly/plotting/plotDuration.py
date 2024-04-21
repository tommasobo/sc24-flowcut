import re
import os
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.gridspec as gridspec
from random import randint
from pathlib import Path    
from matplotlib.colors import ListedColormap
import seaborn as sns
import matplotlib.patches
from matplotlib.lines import Line2D
from datetime import datetime
import matplotlib.patches as mpatches
from more_itertools import sort_together
import numpy
import sharedValues
from matplotlib.pyplot import figure

def fix_names(tmp):
    for idx, item in enumerate(tmp):
        print(item)
        if item == "default minimal":
            tmp[idx] = "ECMP" 
        elif item == "default ugal":
            tmp[idx] = "UGAL" 
        elif item == "default valiant":
            tmp[idx] = "VAL" 
        elif item == "default adaptive":
            tmp[idx] = "Default" 
        elif item == "flowlet ugal":
            tmp[idx] = "Flowlet Switching + UGAL-L" 
        elif item == "flowlet valiant":
            tmp[idx] = "Flowlet Switching" 
        elif item == "flowlet adaptive":
            tmp[idx] = "Flowlet Switching + UGAL-Aries" 
        elif item == "slingshot ugal":
            tmp[idx] = "Slingshot" 
        elif item == "slingshot valiant":
            tmp[idx] = "Slingshot" 
        elif item == "slingshot adaptive":
            tmp[idx] = "Slingshot" 


def create_subplot(subplot_name, subplot_title, list_data_algo, list_name_algo, color, without_bg, type_plot):
    subplot_name.set_title(label = str(subplot_title))

    x_labels = []
    ele = 1 + len(list_data_algo)
    for i in range (1, ele):
        x_labels.append(i)
    subplot_name.set_xticks(x_labels)

    tmp_list = []
    tmp_list.extend(list_data_algo)

    #list_name_algo.extend(list_name_algo)
    list_quantiles = []
    for ele in list_name_algo:
        list_quantiles.append([0.97])

    print(len(list_data_algo[0]))
    print(len(list_data_algo))
    print(len(list_quantiles))
    violin_parts = subplot_name.violinplot(list_data_algo, showextrema=False, showmedians=True, showmeans=True, points=100, quantiles=list_quantiles)
    for idx, vp in enumerate(violin_parts['bodies']):
        if (idx != len(list_data_algo) - 1):
            vp.set_facecolor(sharedValues.color_main_traffic)
            vp.set_edgecolor(sharedValues.color_main_traffic)
            vp.set_alpha(sharedValues.alpha_violin_bodies)
        else:
            vp.set_facecolor(sharedValues.color_extent)
            vp.set_edgecolor(sharedValues.color_extent)
            vp.set_alpha(sharedValues.alpha_violin_bodies)
    # Make the violin body blue with a red border:
    for partname in ('cmeans','cquantiles', 'cmedians'): # 'cbars','cmins','cmaxes',
        vp = violin_parts[partname]
        vp.set_edgecolor(sharedValues.color_violin_symbols)
        vp.set_linewidth(1.6)
        vp.set_alpha(0.85)
    subplot_name.set_xticklabels(list_name_algo)   

    # Hacky way to get symbols with another plot for mean, meadian and 99th percentile
    # Average
    xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cmeans'].get_paths()])
    subplot_name.scatter(xy[:,0], xy[:,1],s=85, marker="o", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    # Median
    if (type_plot != "hops"):
        xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cmedians'].get_paths()])
        subplot_name.scatter(xy[:,0], xy[:,1],s=85, marker="P", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    # 99th percentile
    xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cquantiles'].get_paths()])
    subplot_name.scatter(xy[:,0], xy[:,1],s=62, marker="D", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    violin_parts['cmeans'].set_visible(False)
    violin_parts['cmedians'].set_visible(False)
    violin_parts['cquantiles'].set_visible(False)

def median(x):
    return np.median(np.array(x))

def get_data_from_files(path_dir, is_bg=False, type_plot="latency", file_name="min"):
    for root, dirs, files in os.walk(path_dir):
        list_algo = []
        runtime = []
        data_acquired = list()
        for file in sorted(files):
            if (file_name not in file):
                continue
            list_latencies = []
            list_hops = []
            list_duration_flow = []
            list_duration_sling = []
            list_latencies_with_penality = []
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
            with open(path_dir + file) as fp:
                Lines = fp.readlines()
                for line in Lines:
                    match = re.search('Latency is: (\d+)', line)
                    if match:
                        list_latencies.append(int(match.group(1)))
                        list_latencies_with_penality.append(int(match.group(1)))

                    match = re.search('Runtime: (\d+\.\d+)', line)
                    if match:
                        if (routing_algo == "adaptive" and routing_scheme == "slingshot"):
                            runtime.append(float(match.group(1)) - 600)
                        elif (routing_algo == "adaptive" or (routing_scheme=="default" and routing_algo=="minimal")):
                            runtime.append(float(match.group(1)))
                        

                    match = re.search('Latency OOO is: (\d+)', line)
                    if match:
                        list_latencies.append(int(match.group(1)))
                        list_latencies_with_penality.append(int(match.group(1)) * 2)

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

                    match = re.search('Num Hops: (\d+)', line)
                    if match:
                        list_hops.append(int(match.group(1)))

                    match = re.search('Duration Slingshot: (\d+)', line)
                    if match:
                        list_duration_sling.append(int(match.group(1)))

                    match = re.search('Duration Flowlet: (\d+)', line)
                    if match:
                        list_duration_flow.append(int(match.group(1)))

                    if "Packet Data Seen" in line:
                        num_pkts += 1

                    if "Packet Data OOO" in line:
                        num_ooo += 1

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

            for idx, val in enumerate(total_cycles):
                port_utilization[idx] = list()
                for j, port in enumerate(routers_data[idx]):
                    value = (routers_data[idx][j] / float(total_cycles[idx])) * 100
                    port_utilization[idx].append(value)
                    temp_list.append(value)

            if (type_plot == "duration"): 
                if (routing_scheme == "flowlet"):
                    data_acquired = list_duration_flow
                elif (routing_scheme == "slingshot"):
                    data_acquired = list_duration_sling


    title_y_axis = ""
    return data_acquired, list_algo, title_y_axis

def main():
    # parse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=False, default="Performance of different routing algorithms in ResNet 320 Nodes + No Background Traffic")
    parser.add_argument('--showplot', action='store_const', const=True)
    parser.add_argument('--type', required=False, default="duration")
    parser.add_argument('--without_bg', required=False, default="False")
    args = parser.parse_args()
    if (args.without_bg == "True"):
        args.without_bg = True
    else:
        args.without_bg = False

    flow1_latency, flow1_algo, title_y_axis = get_data_from_files("input_for_plots/parse/", type_plot=args.type, file_name="flow1")
    flow2_latency, flow2_algo, title_y_axis = get_data_from_files("input_for_plots/parse/", type_plot=args.type, file_name="flow2")
    flow3_latency, flow3_algo, title_y_axis = get_data_from_files("input_for_plots/parse/", type_plot=args.type, file_name="flow4")
    sling_latency, sling_algo, title_y_axis = get_data_from_files("input_for_plots/parse/", type_plot=args.type, file_name="sling")
    if args.without_bg is False:
        violin_data_bg, list_algo_bg, title_y_axis = get_data_from_files("input_for_plots/parse_dist_bg/", True, args.type)

    '''list_ugal = []
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
            if args.without_bg is False:
                list_ugal_name.append(list_algo_bg[idx])
                list_ugal.append(violin_data_bg[idx])
        elif ("valiant" in ele):
            list_name_valiant.append(ele)
            list_valiant.append(violin_data[idx])
            if args.without_bg is False:
                list_name_valiant.append(list_algo_bg[idx])
                list_valiant.append(violin_data_bg[idx])
        elif ("adaptive" in ele):
            list_ugal_name_aries.append(ele)
            list_ugal_aries.append(violin_data[idx])
            if args.without_bg is False:
                list_ugal_name_aries.append(list_algo_bg[idx])
                list_ugal_aries.append(violin_data_bg[idx])
        elif ("minimal" in ele):
            list_minimal_name.append(ele)
            list_minimal.append(violin_data[idx])
            if args.without_bg is False:
                list_minimal_name.append(list_algo_bg[idx])
                list_minimal.append(violin_data_bg[idx])'''


    #size
    plt.rc('font', size=11.2)          # controls default text sizes
    plt.rc('axes', titlesize=13.8)     # fontsize of the axes title
    plt.rc('figure', titlesize=25)     # fontsize of the axes title
    plt.rc('axes', labelsize=11.2)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
    plt.rc('legend', fontsize=10)    # legend fontsize
    #plt.rc('figure', titlesize=9)  # fontsize of the figure title

    # Create Grid for subplots
    gs = gridspec.GridSpec(1, 1)
    #ax2 = plt.subplot(gs[0,1])
    #ax3 = plt.subplot(gs[1,0])
    ax4 = plt.subplot(gs[0,0])
    #plt.suptitle("Performance per routing algorithm with ECMP baseline", fontsize="x-large", weight = 'bold')
    ax_lst = [ax4]
    flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e"]
    minimal_color = "#2ecc71"

    #Plot Minimal + Valiant
    #create_subplot(ax_lst[1], "Valiant routing", list_minimal, list_minimal_name, list_valiant, list_name_valiant, sharedValues.color_main_traffic, args.without_bg, args.type)   
    #Plot Minimal + UGAL
    #create_subplot(ax_lst[2], "UGAL routing", list_minimal, list_minimal_name, list_ugal, list_ugal_name, sharedValues.color_main_traffic, args.without_bg, args.type) 
    #Plot Minimal + UGAL - Aries
    violin_data = []
    algo_name = []


    violin_data.append(flow1_latency)
    violin_data.append(flow2_latency)
    violin_data.append(flow3_latency)
    violin_data.append(sling_latency)


    algo_name.append("Flowlet\n3550ns\nTimeout")
    algo_name.append("Flowlet\n8500ns\nTimeout")
    algo_name.append("Flowlet\n13500ns\nTimeout")
    algo_name.append("Slingshot")

    color_list = []
    # First Packet Elements
    color_list.extend([sharedValues.color_background_traffic] * 4)
    # Flowlet Time Elements
    color_list.extend([sharedValues.color_main_traffic] * 3)
    # Flowlet Extent Elements
    color_list.extend([sharedValues.color_extent] * 3)


    print(color_list)
    create_subplot(ax_lst[0], "UGAL-Aries routing", violin_data, algo_name, color_list, args.without_bg, args.type) 

    #Set figure size to be large
    plt.gcf().set_size_inches(8.5, 6)

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
            y = 1.08,
        )
        # xlabel
        '''subplot.set_xlabel(
            "Routing Scheme",
        )'''
        # ylabel
        subplot.set_ylabel(
            title_y_axis,
            horizontalalignment='left',
            rotation = 0,
        )
        subplot.yaxis.set_label_coords(0, 1.01)
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
        subplot.yaxis.set_tick_params(labelsize=9.8)
        subplot.xaxis.set_tick_params(labelsize=10.0)

        subplot.set_ylim(bottom=0)
        #subplot.set_ylim(top=4000)
    ax4.set_title(
            label = "Flowlet duration running AllToAll motif (32 KiB)",
            weight = 'bold',
            horizontalalignment = 'left',
            x = 0,
            y = 1.045,
        )
    # ylabel
    ax4.set_ylabel(
        "Packets per Flowlet",
        horizontalalignment='left',
        rotation = 0,
        fontsize=11.4
    )
    ax4.yaxis.set_label_coords(0, 1.01)
    ax4.xaxis.set_tick_params(labelsize=11.2)
    ax4.yaxis.set_tick_params(labelsize=11.2)
    plt.minorticks_off()
    #ax4.set_ylim(top=1200)

    # Custom Legend
    if args.without_bg is True:
        legend_dict = {'Per Flowlet Time path selection' : sharedValues.color_main_traffic, 'Per Flowlet ACK path selection' : sharedValues.color_extent}
        num_col = 2
        x_pos = 0.5
    else:
        legend_dict = {'Per Flowlet Time path selection' : sharedValues.color_main_traffic, 'Per Flowlet ACK path selection' : sharedValues.color_extent}
        num_col = 3
        x_pos = 0.5
    patchList = []
    for key in legend_dict:
            data_key = mpatches.Patch(color=legend_dict[key], label=key)
            patchList.append(data_key)
    patchList.append(Line2D([0], [0], marker='o', color='white', label='Average',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=10))
    patchList.append(Line2D([0], [0], marker='P', color='white', label='Median',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=10))
    patchList.append(Line2D([0], [0], marker='D', color='white', label='99th Percentile',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=9))
    ax4.legend(handles=patchList,loc='upper left', ncol=1)
    #ax4.legend(handles=patchList,bbox_to_anchor=(x_pos, -0.07), ncol=num_col)
    #ax3.legend(handles=patchList,bbox_to_anchor=(0.99, 0.8), ncol=1)

    # Save Plot to folder giving it a custom name based on input and timestamp
    plt.tight_layout()
    Path("plots/png").mkdir(parents=True, exist_ok=True)
    Path("plots/pdf").mkdir(parents=True, exist_ok=True)
    file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
    plt.savefig(Path("plots/png") / (str("duration_flowlet") + file_name))
    plt.savefig(Path("plots/pdf") / (str("duration_flowlet") + file_name + ".pdf"))
    # Finally Show the plot
    plt.show()

if __name__ == "__main__":
    main()