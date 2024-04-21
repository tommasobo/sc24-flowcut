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
import sharedValues
from matplotlib.pyplot import figure

def fix_names(tmp):
    for idx, item in enumerate(tmp):
        is_bg = False
        if "1" in item:
            is_bg = True
            tmp[idx] = tmp[idx].replace('1', '')
            item = item.replace('1', '')
        if item == "default minimal":
            tmp[idx] = "ECMP" 
        elif item == "default ugal":
            tmp[idx] = "Default" 
        elif item == "default valiant":
            tmp[idx] = "Default" 
        elif item == "default adaptive":
            tmp[idx] = "Default" 
        elif item == "flowlet ugal":
            tmp[idx] = "UGAL" 
        elif item == "flowlet valiant":
            tmp[idx] = "Valiant" 
        elif item == "flowlet adaptive":
            tmp[idx] = "UGAL-Aries" 
        elif item == "slingshot ugal":
            tmp[idx] = "UGAL" 
        elif item == "slingshot valiant":
            tmp[idx] = "Valiant" 
        elif item == "slingshot adaptive":
            tmp[idx] = "UGAL-Aries" 
        if is_bg:
            tmp[idx] =  tmp[idx] + " "

def create_subplot(subplot_name, subplot_title, list_data_algo, list_name_algo, color, without_bg, type_plot):
    subplot_name.set_title(label = str(subplot_title))
    x_labels = []
    j = 1.5
    print(len(list_name_algo))
    print(int(((len(list_data_algo) + 2) / 2) ))
    for i in range(1, int(((len(list_data_algo) + 2) / 2))):
        x_labels.append(j)
        j += 2.0
    if (without_bg is False):
        subplot_name.set_xticks(x_labels)
    else:
       subplot_name.set_xticks(range(1, (len(list_data_algo) + 1)))
    tmp_list = []
    tmp_list.extend(list_data_algo)
    tmp_list_name = []
    tmp_list_name.extend(list_name_algo)
    list_quantiles = []
    for ele in tmp_list_name:
        list_quantiles.append([0.99])

    # Reverse
    tmp_list.reverse()
    tmp_list_name.reverse()

    print(len(tmp_list))

    violin_parts = subplot_name.violinplot(tmp_list, showextrema=False, showmedians=True, showmeans=True, points=20, quantiles=list_quantiles)
    for idx, vp in enumerate(violin_parts['bodies']):
        if (idx % 2 == 0 or without_bg is True):
            vp.set_facecolor(sharedValues.color_background_traffic)
            vp.set_edgecolor(sharedValues.color_background_traffic)
            vp.set_alpha(sharedValues.alpha_violin_bodies)
        else:
            vp.set_facecolor(color)
            vp.set_edgecolor(color)
            vp.set_alpha(sharedValues.alpha_violin_bodies)
    fix_names(tmp_list_name)
    # Make the violin body blue with a red border:
    for partname in ('cmeans','cquantiles', 'cmedians'): # 'cbars','cmins','cmaxes',
        vp = violin_parts[partname]
        vp.set_edgecolor(sharedValues.color_violin_symbols)
        vp.set_linewidth(1.6)
        vp.set_alpha(0.85)
    if (without_bg is False):
        del tmp_list_name[1::2]
    subplot_name.set_xticklabels(tmp_list_name)   

    # Hacky way to get symbols with another plot for mean, meadian and 99th percentile
    # Average
    xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cmeans'].get_paths()])
    subplot_name.scatter(xy[:,0], xy[:,1],s=66, marker="o", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    # Median
    if (type_plot != "hops"):
        xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cmedians'].get_paths()])
        subplot_name.scatter(xy[:,0], xy[:,1],s=66, marker="P", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    # 99th percentile
    xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cquantiles'].get_paths()])
    subplot_name.scatter(xy[:,0], xy[:,1],s=56, marker="D", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    violin_parts['cmeans'].set_visible(False)
    violin_parts['cmedians'].set_visible(False)
    violin_parts['cquantiles'].set_visible(False)

def get_data_from_files(path_dir, is_bg=False, type_plot="latency"):
    for root, dirs, files in os.walk(path_dir):
        list_algo = []
        violin_data = list()
        for file in sorted(files):
            list_latencies = []
            list_hops = []
            list_duration_flow = []
            list_duration_sling = []
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

            if ("flowlet" in routing_scheme or "slingshot" in routing_scheme):
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

            if (type_plot == "latency" and (routing_algo != "valiant")):
                if (routing_scheme == "flowlet"):
                    print(list_duration_flow)
                    violin_data.append(list_duration_flow)
                elif (routing_scheme == "slingshot"):
                    violin_data.append(list_duration_sling)

    print(list_algo)
    list_algo = [x for x in list_algo if "valiant" not in x]

    return violin_data, list_algo

def main():
    # parse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=False, default="Performance of different routing algorithms in ResNet 320 Nodes + No Background Traffic")
    parser.add_argument('--showplot', action='store_const', const=True)
    parser.add_argument('--type', required=False, default="latency")
    parser.add_argument('--without_bg', required=False, default="False")
    args = parser.parse_args()
    if (args.without_bg == "True"):
        args.without_bg = True
    else:
        args.without_bg = False

    violin_data, list_algo = get_data_from_files("input_for_plots/parse_dist/", type_plot=args.type)
    if args.without_bg is False:
        violin_data_bg, list_algo_bg = get_data_from_files("input_for_plots/parse_dist_bg/", True, args.type)

    list_flowlet = []
    list_flowlet_name = []

    list_slingshot = []
    list_slingshot_name = []

    for idx, ele in enumerate(list_algo):
        if ("flowlet" in ele):
            list_flowlet_name.append(ele)
            list_flowlet.append(violin_data[idx])
            if args.without_bg is False:
                list_flowlet_name.append(list_algo_bg[idx])
                list_flowlet.append(violin_data_bg[idx])
        elif ("slingshot" in ele):
            list_slingshot_name.append(ele)
            list_slingshot.append(violin_data[idx])
            if args.without_bg is False:
                list_slingshot_name.append(list_algo_bg[idx])
                list_slingshot.append(violin_data_bg[idx])

    print(list_flowlet_name)
    print(list_slingshot_name)
    #size
    plt.rc('font', size=11.0)          # controls default text sizes
    plt.rc('axes', titlesize=11.0)     # fontsize of the axes title
    plt.rc('axes', labelsize=11)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
    plt.rc('legend', fontsize=8.8)    # legend fontsize
    plt.rc('figure', titlesize=9)  # fontsize of the figure title

    # Create Grid for subplots
    gs = gridspec.GridSpec(1, 2)
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    plt.suptitle("Duration Flowlet comparing Flowlet Switching and Slingshot Routing", fontsize="x-large", weight = 'bold')
    ax_lst = [ax1,ax2]
    flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e"]
    minimal_color = "#2ecc71"

    #Plot Minimal + Valiant
    create_subplot(ax_lst[0], "Flowlet Switching", list_flowlet, list_flowlet_name, sharedValues.color_main_traffic, args.without_bg, args.type)   
    #Plot Minimal + UGAL
    create_subplot(ax_lst[1], "Slingshot Routing", list_slingshot, list_slingshot_name, sharedValues.color_main_traffic, args.without_bg, args.type) 

    #Set figure size to be large
    plt.gcf().set_size_inches(15, 9)

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
            y = 1.03
        )
        # xlabel
        '''subplot.set_xlabel(
            "Routing Scheme",
        )'''
        # ylabel
        subplot.set_ylabel(
            "Packets per Flowlet",
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
        subplot.set_ylim(top=68)
    plt.minorticks_off()

    # Custom Legend
    if args.without_bg is True:
        legend_dict = { 'ResNet50 without background traffic' : sharedValues.color_background_traffic}
        num_col = 2
        x_pos = 0.8
    else:
        legend_dict = { 'Uniform Traffic without background traffic' : sharedValues.color_background_traffic, 'Uniform Traffic with background traffic' : sharedValues.color_main_traffic}
        num_col = 3
        x_pos = 0.9
    patchList = []
    for key in legend_dict:
            data_key = mpatches.Patch(color=legend_dict[key], label=key)
            patchList.append(data_key)
    patchList.append(Line2D([0], [0], marker='o', color='white', label='Average',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=9))
    patchList.append(Line2D([0], [0], marker='P', color='white', label='Median',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=9))
    patchList.append(Line2D([0], [0], marker='D', color='white', label='99th Percentile',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=8))
    ax2.legend(handles=patchList,bbox_to_anchor=(x_pos, -0.07), ncol=num_col)
    ax1.legend(handles=patchList,bbox_to_anchor=(x_pos, -0.07), ncol=num_col)
    #ax3.legend(handles=patchList,bbox_to_anchor=(0.99, 0.8), ncol=1)

    # Save Plot to folder giving it a custom name based on input and timestamp
    plt.tight_layout()
    Path("plots/png").mkdir(parents=True, exist_ok=True)
    Path("plots/pdf").mkdir(parents=True, exist_ok=True)
    file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
    plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
    plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
    # Finally Show the plot
    plt.show()

if __name__ == "__main__":
    main()


'''
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
import sharedValues
from matplotlib.pyplot import figure

def fix_names(tmp):
    for idx, item in enumerate(tmp):
        is_bg = False
        if "1" in item:
            is_bg = True
            tmp[idx] = tmp[idx].replace('1', '')
            item = item.replace('1', '')
        if item == "default minimal":
            tmp[idx] = "ECMP" 
        elif item == "default ugal":
            tmp[idx] = "Default" 
        elif item == "default valiant":
            tmp[idx] = "Default" 
        elif item == "default adaptive":
            tmp[idx] = "Default" 
        elif item == "flowlet ugal":
            tmp[idx] = "UGAL" 
        elif item == "flowlet valiant":
            tmp[idx] = "Valiant" 
        elif item == "flowlet adaptive":
            tmp[idx] = "UGAL-Aries" 
        elif item == "slingshot ugal":
            tmp[idx] = "UGAL" 
        elif item == "slingshot valiant":
            tmp[idx] = "Valiant" 
        elif item == "slingshot adaptive":
            tmp[idx] = "UGAL-Aries" 
        if is_bg:
            tmp[idx] =  tmp[idx] + " "

def create_subplot(subplot_name, subplot_title, list_data_algo, list_name_algo, color, without_bg, type_plot):
    subplot_name.set_title(label = str(subplot_title))
    x_labels = []
    j = 1.5
    print(len(list_name_algo))
    print(int(((len(list_data_algo) + 2) / 2) ))
    for i in range(1, int(((len(list_data_algo) + 2) / 2))):
        x_labels.append(j)
        j += 2.0
    if (without_bg is False):
        subplot_name.set_xticks(x_labels)
    else:
       subplot_name.set_xticks(range(1, (len(list_data_algo) + 1)))
    tmp_list = []
    tmp_list.extend(list_data_algo)
    tmp_list_name = []
    tmp_list_name.extend(list_name_algo)
    list_quantiles = []
    for ele in tmp_list_name:
        list_quantiles.append([0.99])

    # Reverse
    tmp_list.reverse()
    tmp_list_name.reverse()

    print(len(tmp_list))

    violin_parts = subplot_name.violinplot(tmp_list, showextrema=False, showmedians=True, showmeans=True, points=20, quantiles=list_quantiles)
    for idx, vp in enumerate(violin_parts['bodies']):
        if (idx % 2 == 0 or without_bg is True):
            vp.set_facecolor(sharedValues.color_background_traffic)
            vp.set_edgecolor(sharedValues.color_background_traffic)
            vp.set_alpha(sharedValues.alpha_violin_bodies)
        else:
            vp.set_facecolor(color)
            vp.set_edgecolor(color)
            vp.set_alpha(sharedValues.alpha_violin_bodies)
    fix_names(tmp_list_name)
    # Make the violin body blue with a red border:
    for partname in ('cmeans','cquantiles', 'cmedians'): # 'cbars','cmins','cmaxes',
        vp = violin_parts[partname]
        vp.set_edgecolor(sharedValues.color_violin_symbols)
        vp.set_linewidth(1.6)
        vp.set_alpha(0.85)
    if (without_bg is False):
        del tmp_list_name[1::2]
    subplot_name.set_xticklabels(tmp_list_name)   

    # Hacky way to get symbols with another plot for mean, meadian and 99th percentile
    # Average
    xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cmeans'].get_paths()])
    subplot_name.scatter(xy[:,0], xy[:,1],s=66, marker="o", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    # Median
    if (type_plot != "hops"):
        xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cmedians'].get_paths()])
        subplot_name.scatter(xy[:,0], xy[:,1],s=66, marker="P", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    # 99th percentile
    xy = np.array([[l.vertices[:,0].mean(),l.vertices[0,1]] for l in violin_parts['cquantiles'].get_paths()])
    subplot_name.scatter(xy[:,0], xy[:,1],s=56, marker="D", zorder=2, color=sharedValues.color_violin_symbols, alpha=0.97, clip_on=False)
    violin_parts['cmeans'].set_visible(False)
    violin_parts['cmedians'].set_visible(False)
    violin_parts['cquantiles'].set_visible(False)

def get_data_from_files(path_dir, is_bg=False, type_plot="latency"):
    for root, dirs, files in os.walk(path_dir):
        list_algo = []
        violin_data = list()
        for file in sorted(files):
            list_latencies = []
            list_hops = []
            list_duration_flow = []
            list_duration_sling = []
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

            if ("flowlet" in routing_scheme or "slingshot" in routing_scheme):
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

            if (type_plot == "latency"):
                if (routing_scheme == "flowlet"):
                    print(list_duration_flow)
                    violin_data.append(list_duration_flow)
                elif (routing_scheme == "slingshot"):
                    violin_data.append(list_duration_sling)

    return violin_data, list_algo

def main():
    # parse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=False, default="Performance of different routing algorithms in ResNet 320 Nodes + No Background Traffic")
    parser.add_argument('--showplot', action='store_const', const=True)
    parser.add_argument('--type', required=False, default="latency")
    parser.add_argument('--without_bg', required=False, default="False")
    args = parser.parse_args()
    if (args.without_bg == "True"):
        args.without_bg = True
    else:
        args.without_bg = False

    violin_data, list_algo = get_data_from_files("input_for_plots/parse_dist/", type_plot=args.type)
    if args.without_bg is False:
        violin_data_bg, list_algo_bg = get_data_from_files("input_for_plots/parse_dist_bg/", True, args.type)

    list_flowlet = []
    list_flowlet_name = []

    list_slingshot = []
    list_slingshot_name = []

    for idx, ele in enumerate(list_algo):
        if ("flowlet" in ele):
            list_flowlet_name.append(ele)
            list_flowlet.append(violin_data[idx])
            if args.without_bg is False:
                list_flowlet_name.append(list_algo_bg[idx])
                list_flowlet.append(violin_data_bg[idx])
        elif ("slingshot" in ele):
            list_slingshot_name.append(ele)
            list_slingshot.append(violin_data[idx])
            if args.without_bg is False:
                list_slingshot_name.append(list_algo_bg[idx])
                list_slingshot.append(violin_data_bg[idx])

    print(list_flowlet_name)
    print(list_slingshot_name)
    #size
    plt.rc('font', size=11.0)          # controls default text sizes
    plt.rc('axes', titlesize=11.0)     # fontsize of the axes title
    plt.rc('axes', labelsize=11)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
    plt.rc('legend', fontsize=8.8)    # legend fontsize
    plt.rc('figure', titlesize=9)  # fontsize of the figure title

    # Create Grid for subplots
    gs = gridspec.GridSpec(1, 2)
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    plt.suptitle("Duration Flowlet comparing Flowlet Switching and Slingshot Routing", fontsize="x-large", weight = 'bold')
    ax_lst = [ax1,ax2]
    flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e"]
    minimal_color = "#2ecc71"

    #Plot Minimal + Valiant
    create_subplot(ax_lst[0], "Flowlet Switching", list_flowlet, list_flowlet_name, sharedValues.color_main_traffic, args.without_bg, args.type)   
    #Plot Minimal + UGAL
    create_subplot(ax_lst[1], "Slingshot Routing", list_slingshot, list_slingshot_name, sharedValues.color_main_traffic, args.without_bg, args.type) 

    #Set figure size to be large
    plt.gcf().set_size_inches(15, 9)

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
            y = 1.03
        )
        # xlabel
        subplot.set_xlabel(
            "Routing Scheme",
        )
        # ylabel
        subplot.set_ylabel(
            "Packets per Flowlet",
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
        subplot.set_ylim(top=50)
    plt.minorticks_off()

    # Custom Legend
    if args.without_bg is True:
        legend_dict = { 'ADVG+1 without background traffic' : sharedValues.color_background_traffic}
        num_col = 2
        x_pos = 0.8
    else:
        legend_dict = { 'Uniform Traffic without background traffic' : sharedValues.color_background_traffic, 'Uniform Traffic with background traffic' : sharedValues.color_main_traffic}
        num_col = 3
        x_pos = 0.9
    patchList = []
    for key in legend_dict:
            data_key = mpatches.Patch(color=legend_dict[key], label=key)
            patchList.append(data_key)
    patchList.append(Line2D([0], [0], marker='o', color='white', label='Average',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=9))
    patchList.append(Line2D([0], [0], marker='P', color='white', label='Median',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=9))
    patchList.append(Line2D([0], [0], marker='D', color='white', label='99th Percentile',
                          markerfacecolor=sharedValues.color_violin_symbols, markersize=8))
    ax2.legend(handles=patchList,bbox_to_anchor=(x_pos, -0.07), ncol=num_col)
    ax1.legend(handles=patchList,bbox_to_anchor=(x_pos, -0.07), ncol=num_col)
    #ax3.legend(handles=patchList,bbox_to_anchor=(0.99, 0.8), ncol=1)

    # Save Plot to folder giving it a custom name based on input and timestamp
    plt.tight_layout()
    Path("plots/png").mkdir(parents=True, exist_ok=True)
    Path("plots/pdf").mkdir(parents=True, exist_ok=True)
    file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
    plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
    plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
    # Finally Show the plot
    plt.show()

if __name__ == "__main__":
    main()
'''