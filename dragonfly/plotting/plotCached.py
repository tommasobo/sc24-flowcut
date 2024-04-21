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

# parse
parser = argparse.ArgumentParser()
parser.add_argument('--title', required=False, default="Ratio of cached vs new flowlets in ResNet50")
parser.add_argument('--csv', required=False)
parser.add_argument('--out', required=False)
parser.add_argument('--showplot', action='store_const', const=True)
parser.add_argument('--type', required=False, default="latency")
parser.add_argument('--can_skip', required=False, type=bool, default=False)
args = parser.parse_args()

print(args.type)
if args.can_skip == False:
    for root, dirs, files in os.walk("input_for_plots/parse/"):
        for file in files:
            if ("default" in file):
                print("Skip")
                #continue
            list_latencies = []
            list_hops = []
            list_duration_flow = []
            list_duration_sling = []
            num_pkts = 0
            num_ooo = 0
            num_cached = 0
            num_flowlets = 0
            num_slingshot = 0
            num_cached_slingshot = 0

            data = []
            already_matched_name = False

            with open("input_for_plots/parse/" + file) as fp:
                Lines = fp.readlines()

                data = list()
                for line in Lines:
                    match = re.search("EMBER: Motif='(\w+)\s+", line)
                    if match:
                        program_name = (str(match.group(1)))
                        if already_matched_name is False:
                            data.append("programName," + str(program_name))
                            already_matched_name = True
                        
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

                    if "New Flowlet" in line:
                        num_flowlets += 1

                    if "Using Cached Flowlet" in line:
                        num_cached += 1
                    
                    if "New Flowlet Slingshot" in line:
                        num_slingshot += 1

                    if "Using Cached Slingshot" in line:
                        num_cached_slingshot += 1

                    if "Packet Data Seen" in line:
                        num_pkts += 1

                    if "Packet Data OOO" in line:
                        num_ooo += 1

                    match = re.search('Duration Slingshot: (\d+)', line)
                    if match:
                        list_duration_sling.append(int(match.group(1)))

                    match = re.search('Duration Flowlet: (\d+)', line)
                    if match:
                        list_duration_flow.append(int(match.group(1)))

            avg_latency_ns = sum(list_latencies) / len(list_latencies)
            avg_hops = sum(list_hops) / len(list_hops)
            a = np.array(list_latencies)
            avg99_latency_ns = np.percentile(a, 99)

            if (routing_scheme == "flowlet"):
                percentage_cached = (num_cached / (num_cached + num_flowlets)) * 100
                percentage_new = (num_flowlets / (num_cached + num_flowlets)) * 100
            elif (routing_scheme == "slingshot"):
                percentage_cached = (num_cached_slingshot / (num_cached_slingshot + num_slingshot)) * 100
                percentage_new = (num_slingshot / (num_cached_slingshot + num_slingshot)) * 100
            else:
                percentage_cached = -1
                percentage_new = -1

            if (routing_scheme == "flowlet" or routing_scheme == "slingshot"):
                data.append("avgLatency," + str(avg_latency_ns))
                data.append("avgHops," + str(avg_hops))
                data.append("avgLatency99," + str(avg99_latency_ns))
                data.append("packetsTotal," + str(num_pkts))
                data.append("packetsOOO," + str(num_ooo))
                data.append("packetsOOO%," + str((num_ooo / num_pkts) * 100))
                data.append("numFlowlet," + str(num_flowlets))
                data.append("numFlowletCached," + str(num_cached))
                data.append("numSlingshot," + str(num_slingshot))
                data.append("numSlingshotCached," + str(num_cached_slingshot))
                data.append("percentageCached," + str(percentage_cached))
                data.append("percentageNew," + str(percentage_new))


                print("Avg latency is {} - Avg Num Hop is {}".format(str(avg_latency_ns), str(avg_hops)))
                print("99th percentile latency is {}".format(str(avg99_latency_ns)))
                print("Tot Pkt {} - OOO {} - % {}".format(num_pkts, num_ooo, (num_ooo / num_pkts) * 100))

                if (routing_algo == "adaptive"):
                    with open("input_for_plots/parsed_csv/" + file + ".csv", "w") as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        for line in data:
                            line_for_csv = line.split(",")
                            writer.writerow(line_for_csv)

#size
plt.rc('font', size=12.0)          # controls default text sizes
plt.rc('axes', titlesize=sharedValues.size_title)     # fontsize of the axes title
plt.rc('axes', labelsize=12)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=9.8)    # legend fontsize
plt.rc('figure', titlesize=10)  # fontsize of the figure title


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
list_flowlet = []
list_flowlet_cached = []
list_slingshot = []
list_slingshot_cached = []
list_percentage_cached = []
list_percentage_new = []


# Read Input Data
for root, dirs, files in os.walk("input_for_plots/parsed_csv/"):
    for file in files:
        if file.endswith('.csv'):
            csv_op = csv.reader(open("input_for_plots/parsed_csv/" + file), delimiter=',')
            for line in csv_op:
                if (line[0] == "programName"):
                    list_ember_test.append(line[1])
                elif (line[0] == "avgLatency"):
                    list_latency.append(line[1])
                elif (line[0] == "run_time_ns"):
                    list_runtime.append(line[1])
                elif (line[0] == "packetsOOO"):
                    list_ooo.append(line[1])
                elif (line[0] == "packetsTotal"):
                    list_total_pkts.append(line[1])
                elif (line[0] == "routingScheme"):
                    list_routing_scheme.append(line[1])
                elif (line[0] == "routingAlgo"):
                    list_routing_algo.append(line[1])
                elif (line[0] == "avgLatency99"):
                    list_latency_99.append(line[1])
                elif (line[0] == "avgHops"):
                    list_hops.append(line[1])
                elif (line[0] == "numFlowlet"):
                    list_flowlet.append(line[1])
                elif (line[0] == "numFlowletCached"):
                    list_flowlet_cached.append(line[1])
                elif (line[0] == "numSlingshot"):
                    list_slingshot.append(line[1])
                elif (line[0] == "numSlingshotCached"):
                    list_slingshot_cached.append(line[1])
                elif (line[0] == "percentageCached"):
                    list_percentage_cached.append(line[1])
                elif (line[0] == "percentageNew"):
                    list_percentage_new.append(line[1])

# plot data
list_x = []
list_y = []
list_y_1 = []
list_y_2 = []

print(list_percentage_cached)
print(list_routing_algo)
y_axis = ""
# Perfectionate Names
for idx, val in enumerate(list_ember_test):
    if (list_routing_algo[idx] == "ugal"):
        algo_name = "UGALa"
    elif (list_routing_algo[idx] == "minimal"):
        algo_name = "ECMP-SST"
    elif (list_routing_algo[idx] == "valiant"):
        algo_name = "Valiant"
    elif (list_routing_algo[idx] == "adaptive"):
        algo_name = "UGAL-Aries"
    elif (list_routing_algo[idx] == "min-a"):
        algo_name = "Minimal Adaptive"
    elif (list_routing_algo[idx] == "ecmp"):
        algo_name = "ECMP"

    if (list_routing_scheme[idx] == "default"):
        list_x.append(algo_name)
    elif (list_routing_scheme[idx] == "flowlet"):
        list_x.append(algo_name + " + Vlowlet")
    elif (list_routing_scheme[idx] == "slingshot"):
        list_x.append(algo_name + " + Slingshot")

    if (args.type == "latency"):
        list_y.append(int(float(list_latency[idx])))
        y_axis = "Latency (ns)"
    elif (args.type == "ooo"):
        ooo_percentage = (float(list_ooo[idx]) / float(list_total_pkts[idx])) * 100
        list_y.append(ooo_percentage)
        y_axis = "Out Of Order Packets (%)"
    elif (args.type == "latency99"):
        list_y.append(int(float(list_latency_99[idx])))
        y_axis = "Latency 99th percentile (ns)"
    elif (args.type == "hops"):
        list_y.append((float(list_hops[idx])))
        y_axis = "Number Hops"
    elif (args.type == "runtime"):
        runtime_ms = float(list_runtime[idx]) / 1000000
        list_y.append(runtime_ms)
        y_axis = "Runtime (ms)"
    elif (args.type == "flow"):
        list_y_1.append(float(list_percentage_cached[idx]))
        list_y_2.append(float(list_percentage_new[idx]))
        y_axis = "Cached Routing vs New Routing Decision (% of total packets)"

# Title and Labels
ax.set_title(
	label = str(args.title),
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.06
)
# xlabel
ax.set_xlabel(
	"Routing Scheme",
)
# ylabel
ax.set_ylabel(
	y_axis,
	horizontalalignment='left',
	rotation = 0,
)
ax.yaxis.set_label_coords(0, 1.02)

# Order by Value and alternate Default and Flowlet
print(list_x)
print(list_y_1)
print(list_y_2)

original_list_x = list_x

list_x = sort_together([original_list_x, list_y_1])[0]
list_y_1 = sort_together([original_list_x, list_y_1])[1]
list_y_2 = sort_together([original_list_x, list_y_2])[1]


list_x = list(list_x)
list_y_1 = list(list_y_1)
list_y_2 = list(list_y_2)
list_x.reverse()
list_y_1.reverse()
list_y_2.reverse()

for idx, val in enumerate(list_x):
    if ("Vlowlet" in val):
        list_x[idx] = list_x[idx].replace("Vlowlet", "Flowlet")
    if ("UGALa" in val):
        list_x[idx] = list_x[idx].replace("UGALa", "UGAL")

# Data

width = 0.35  # the width of the bars
x = np.arange(len(list_x))
rects1 = ax.bar(x - width/2, list_y_1, width, color=sharedValues.color_main_traffic)
rects2 = ax.bar(x + width/2, list_y_2, width, color=sharedValues.color_background_traffic)

# Set the tick positions
ax.set_xticks(x)
# Set the tick labels
ax.set_xticklabels(list_x)
#ax.bar_label(ax.containers[0], color="#1B9E77")
plt.gcf().set_size_inches(12, 6.5)


# For Runtime Graphs
ax.set_ylim(bottom=0)
ax.set_ylim(top=100)
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
# legend
legend_dict = {'Cached routing decision' : sharedValues.color_main_traffic, 'New routing decision' : sharedValues.color_background_traffic}
patchList = []
for key in legend_dict:
        data_key = mpatches.Patch(color=legend_dict[key], label=key)
        patchList.append(data_key)

plt.legend(handles=patchList)
plt.xticks(fontsize=11.5, color='black')
plt.yticks(fontsize=11.5, color='black')

ax.tick_params(axis="x", labelsize=9.0)

# Save Plot to folder giving it a custom name based on input and timestamp
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str(args.title) + file_name + y_axis))
plt.savefig(Path("plots/pdf") / (str(args.title) + file_name + y_axis + ".pdf"))
# Finally Show the plot
plt.show()

