import re
import os
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path    
from matplotlib.colors import ListedColormap
import seaborn as sns
from datetime import datetime
import matplotlib.patches as mpatches
from more_itertools import sort_together
from matplotlib.pyplot import figure
import sharedValues


for root, dirs, files in os.walk("input_for_plots/parse_dist/"):
    for file in files:
        list_latencies = []
        list_hops = []
        num_pkts = 0
        num_ooo = 0

        data = []

        with open("input_for_plots/parse_dist/" + file) as fp:
            Lines = fp.readlines()
            '''program_name = 
            num_nodes = 
            message_size = 
            iteration = 
            runtime_ns = 
            routing_scheme =
            routing_algo =
            flowlet_timeout ='''
            data = list()
            for line in Lines:
                match = re.search("EMBER: Motif='(\w+)\s+", line)
                if match:
                    program_name = (str(match.group(1)))
                    data.append("programName," + str(program_name))
                    
                match = re.search('EMBER: numNodes=(\d+)', line)
                if match:
                    num_nodes = (int(match.group(1)))
                    data.append("numNodes," + str(num_nodes))

                match = re.search('routing=(\w+)', line)
                if match:
                    routing_scheme = (str(match.group(1)))
                    data.append("routingScheme," + str(routing_scheme))

                match = re.search('defaultRouting=(\w+)', line)
                if match:
                    routing_algo = (str(match.group(1)))
                    data.append("routingAlgo," + str(routing_algo))

                match = re.search('Latency is: (\d+)', line)
                if match:
                    list_latencies.append(int(match.group(1)))

                match = re.search('Num Hops: (\d+)', line)
                if match:
                    list_hops.append(int(match.group(1)))

                if "Packet Data Seen" in line:
                    num_pkts += 1

                if "Packet Data OOO" in line:
                    num_ooo += 1

        avg_latency_ns = sum(list_latencies) / len(list_latencies)
        avg_hops = sum(list_hops) / len(list_hops)
        a = np.array(list_latencies)
        avg99_latency_ns = np.percentile(a, 99)

        data.append("avgLatency," + str(avg_latency_ns))
        data.append("avgHops," + str(avg_hops))
        data.append("avgLatency99," + str(avg99_latency_ns))
        data.append("packetsTotal," + str(num_pkts))
        data.append("packetsOOO," + str(num_ooo))
        data.append("packetsOOO%," + str((num_ooo / num_pkts) * 100))


        print("Avg latency is {} - Avg Num Hop is {}".format(str(avg_latency_ns), str(avg_hops)))
        print("99th percentile latency is {}".format(str(avg99_latency_ns)))
        print("Tot Pkt {} - OOO {} - % {}".format(num_pkts, num_ooo, (num_ooo / num_pkts) * 100))

        #size
        plt.rc('font', size=12.0)          # controls default text sizes
        plt.rc('axes', titlesize=sharedValues.size_title)     # fontsize of the axes title
        plt.rc('axes', labelsize=12)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
        plt.rc('legend', fontsize=9.8)    # legend fontsize
        plt.rc('figure', titlesize=10)  # fontsize of the figure title

        # parse
        parser = argparse.ArgumentParser()
        parser.add_argument('--title', required=False, default="Performance of different routing algorithms in ResNet 320 Nodes + No Background Traffic")
        parser.add_argument('--csv', required=False)
        parser.add_argument('--out', required=False)
        parser.add_argument('--showplot', action='store_const', const=True)
        parser.add_argument('--type', required=False, default="latency")
        args = parser.parse_args()
        # init
        plt.figure()
        ax = plt.axes(facecolor=sharedValues.color_background_plot)
        # info
        title = "?"
        xlabel = "?"
        ylabel = "?"

        list_ember_test = []
        list_routing_scheme = []
        list_routing_algo = []
        list_latency = []
        list_runtime = []
        list_ooo = []
        list_total_pkts = []
        list_hops = []
        list_latency_99 = []

        # Title and Labels
        ax.set_title(
            label = str("Distribution Latencies"),
            weight = 'bold',
            horizontalalignment = 'left',
            x = 0,
            y = 1.06
        )
        # xlabel
        ax.set_xlabel(
            "Latency (ns)",
        )
        # ylabel
        ax.set_ylabel(
            "Frequency",
            horizontalalignment='left',
            rotation = 0,
        )
        ax.yaxis.set_label_coords(0, 1.02)

        ax.hist(list_latencies)

        #ax.bar_label(ax.containers[0], color="#1B9E77")
        plt.gcf().set_size_inches(14, 8)

        # For Runtime Graphs
        ax.set_yscale('linear')
        #ax.set_ylim(bottom=0)
        #ax.set_ylim(top=60)
        plt.minorticks_off()

        # y grid
        ax.grid(axis='y', color='w', linewidth=2, linestyle='-')
        ax.set_axisbelow(True)
        # hide ticks y-axis
        ax.tick_params(axis='y', left=False, right=False)
        # spines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

        plt.xticks(fontsize=11.5, color='black')
        plt.yticks(fontsize=11.5, color='black')

        ax.tick_params(axis="x", labelsize=9.0)

        # Save Plot to folder giving it a custom name based on input and timestamp
        plt.tight_layout()
        Path("plots/png").mkdir(parents=True, exist_ok=True)
        Path("plots/pdf").mkdir(parents=True, exist_ok=True)
        file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
        plt.savefig(Path("plots/png") / (str("Distribution Latencies") + file_name))
        plt.savefig(Path("plots/pdf") / (str("Distribution Latencies") + file_name + ".pdf"))
        # Finally Show the plot
        plt.show()