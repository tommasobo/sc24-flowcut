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
import matplotlib.patches
from matplotlib.lines import Line2D
from datetime import datetime
import numpy as np
import random

import matplotlib.patches as mpatches
import numpy
from matplotlib.pyplot import figure
import sharedValues
import statistics
from sklearn.neighbors import KernelDensity



def process_csv_points(file_name):
    input_folder = "input_data"
    idx = 0
    with open(Path(input_folder, file_name)) as fp:
        Lines = fp.readlines()
        x_points = []
        y_points = []
        for line in Lines:
            splitted_line = line.split(",")
            #print("X {} - Y {}".format(float(splitted_line[0]), float(splitted_line[1])))
            #if (idx % 7 == 0):
            x_points.append(float(splitted_line[0]))
            y_points.append(float(splitted_line[1]))
            idx += 1 

        return x_points, y_points

def plot_all(points):

    plt.rc('font', size=12.5)          # controls default text sizes
    plt.rc('axes', titlesize=13.5)     # fontsize of the axes title
    plt.rc('figure', titlesize=25)     # fontsize of the axes title
    plt.rc('axes', labelsize=12.5)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
    plt.rc('legend', fontsize=10.0)    # legend fontsize

    ooo = [20, 40, 60, 80]
    bars = ('20', '40', '60', '80')
    x_pos = np.arange(len(bars))

    ax = plt.axes(facecolor=sharedValues.color_background_plot)

    # Title and Labels
    ax.set_title(
        label = "Flow size distribution for different workloads",
        #label = "",
        weight = 'bold',
        horizontalalignment = 'left',
        x = 0,
        y = 1.0,
        fontsize=14
    )
    # xlabel
    ax.set_xlabel(
        "Flow Sizes (B)",
        #"",
    )
    # ylabel
    ax.set_ylabel(
        "CDF",
    )
    #ax.yaxis.set_label_coords(0, 1.012)

    draws = np.random.choice(points[0][0], size=30, replace=True)

    barlist = ax.plot(points[0][0], points[0][1], color=sharedValues.color_global_ports[0], alpha=sharedValues.alpha_bar_plots, linewidth=3)
    barlist1 = ax.plot(points[1][0], points[1][1], color=sharedValues.color_global_ports[1], alpha=sharedValues.alpha_bar_plots, linewidth=3)
    barlist1 = ax.plot(points[2][0], points[2][1], color=sharedValues.color_extent, alpha=sharedValues.alpha_bar_plots, linewidth=3)
    
    # Create names on the x-axis
    #plt.xticks(x_pos, bars)
    #ax.set_ylim(bottom=0, top=2000)

    ax.set_yscale('linear')
    ax.set_ylim(bottom=0)
    ax.set_ylim(top=1)
    #ax.set_ylim(top=60)
    plt.minorticks_off()

    # y grid
    ax.set_xscale('log')

    ax.grid(axis='y', color='w', linewidth=2, linestyle='-')
    ax.set_axisbelow(True)
    # hide ticks y-axis
    ax.tick_params(axis='y', left=False, right=False)
    # spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.set_xlim([100, 10**9])
    ax.xaxis.set_tick_params(labelsize=12.5)
    ax.yaxis.set_tick_params(labelsize=12.5)

    ax.text(10**5,0.5,"Web-search", size=12,
                           verticalalignment='center', rotation=0, color=sharedValues.color_global_ports[0])

    ax.text(32203,0.77,"Data mining", size=12,
                           verticalalignment='center', rotation=0, color=sharedValues.color_global_ports[1])

    ax.text(1500,0.87,"Enterprise", size=12,
                           verticalalignment='center', rotation=0, color=sharedValues.color_extent)

    #plt.gcf().set_size_inches(9, 4)
    plt.tight_layout()
    Path("plots/png").mkdir(parents=True, exist_ok=True)
    Path("plots/pdf").mkdir(parents=True, exist_ok=True)
    file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
    plt.savefig(Path("plots/png") / (str("runtime_ooo") + file_name))
    plt.savefig(Path("plots/pdf") / (str("runtime_ooo") + file_name + ".pdf"))
    # Finally Show the plot
    plt.show()

def inverse_linear_normalized(x2, y2, y_input):
    return x2 * (y_input / y2)


def inverse_linear(x1, y1, x2, y2, y_input):
    return inverse_linear_normalized(x2 - x1, y2 - y1, y_input - y1) + x1


def inverse_cdf(x_values, y_values, y_input):
    # Take in SORTED arrays of x and y values representing
    #   the points connecting a bunch of linear functions
    if y_input < y_values[0] or y_input > y_values[-1]:
        raise Exception(f'y_input {y_input} out of range')

    for i in range(1, len(y_values)):
        if y_input <= y_values[i]:
            return inverse_linear(
                x_values[i - 1], y_values[i - 1],
                x_values[i], y_values[i],
                y_input
            )

    raise Exception('Unreachable')

def plot_loghist(x, x1, x2, binss):

    hist, bins = np.histogram(x2, bins=binss)
    logbins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
    plt.hist(x2, bins=logbins, color=sharedValues.color_extent)

    hist, bins = np.histogram(x, bins=binss)
    logbins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
    plt.hist(x, bins=logbins, color=sharedValues.color_global_ports[0])

    hist, bins = np.histogram(x1, bins=binss)
    logbins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
    plt.hist(x1, bins=logbins, color=sharedValues.color_global_ports[1], alpha=0.75)
 
    plt.xscale('log')
    plt.show()

def main():
    web_search_file = "web_search_cdf.csv"
    data_mining_file = "data_mining_cdf.csv"
    enterprise_file = "enterprise_cdf.csv"

    points = []

    points.append(process_csv_points(web_search_file))
    points.append(process_csv_points(data_mining_file))
    points.append(process_csv_points(enterprise_file))
    plot_all(points)

    my_values = []
    other = []
    for i in range(5000):
        other.append(random.uniform(0, 100))
        my_values.append(float(inverse_cdf(points[0][0], points[0][1], random.uniform(0, 1))))
    
    my_method = []
    my_method_2 = []
    my_method_3 = []
    for i in range(5000):
        my_method.append((numpy.interp(random.uniform(0, 1), points[0][1], points[0][0])))
        my_method_2.append((numpy.interp(random.uniform(0, 1), points[1][1], points[1][0])))
        my_method_3.append((numpy.interp(random.uniform(0, 1), points[2][1], points[2][0])))
    #plot_loghist(my_method, my_method_2, my_method_3, 10000)'''

    my_values_1 = []
    for i in range(5000):
        my_values_1.append(float(inverse_cdf(points[1][0], points[1][1], random.uniform(0, 1))))

    my_values_2 = []
    for i in range(5000):
        my_values_2.append(float(inverse_cdf(points[2][0], points[2][1], random.uniform(0, 1))))

    plot_loghist(my_values, my_values_1, my_values_2, 50)

    # Save to File
    with open('size_flow_web_search.txt', 'w') as f:
        for item in my_values:
            if (item == 0):
                item = 1
            f.write("%s\n" % int(item))

    with open('size_flow_data_mining.txt', 'w') as f:
        for item in my_values_1:
            if (item == 0):
                item = 1
            f.write("%s\n" % int(item))

    with open('size_flow_enterprise.txt', 'w') as f:
        for item in my_values_2:
            if (item == 0):
                item = 1
            f.write("%s\n" % int(item))

    print(int(statistics.mean(my_values)))
    print(int(statistics.median(my_values)))
    print()

    print(int(statistics.mean(my_values_1)))
    print(int(statistics.median(my_values_1)))
    print()

    print(int(statistics.mean(my_values_2)))
    print(int(statistics.median(my_values_2)))
    print()

    print(sum(i > 10000000 for i in my_values))


if __name__ == "__main__":
    main()