import re
import subprocess
from pathlib import Path
import sys
from argparse import ArgumentParser
import pathlib
import os
import statistics
import time
import random
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
sys.path.append("../")

from general_bench import *

def getCompletionTime(name_file_to_use, min_size=0, max_size=999999999, algo=None):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Simulation is complete, simulated time: (\d+.\d+)", line)
            if result:
                actual = float(result.group(1))
    return actual

def getListFCT(name_file_to_use, min_size=0, max_size=999999999, algo=None):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Flow BandWidth (\d+.\d+) (\d+) -", line)
            if result:
                actual = int(result.group(2))
                temp_list.append(actual)
    return temp_list

def getList99FCT(name_file_to_use, algo=None):
    temp_list = []
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"Flow Completion time is (\d+.\d+)", line)
            if result:
                actual = float(result.group(1))
                temp_list.append(actual)
    return temp_list

def getTotOOO(name_file_to_use):
    seen = 0
    ooo = 0
    with open(name_file_to_use) as file:
        for line in file:
            # FCT
            result = re.search(r"OOO (\d+) of (\d+)", line)
            if result:
                seen += int(result.group(2))
                ooo += int(result.group(1))
    return ooo / seen * 100


# ECMP
run_string = 'sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --algorithm=minimal --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > out.tmp'
print(run_string)
os.system(run_string)
fct_ecmp = getListFCT("out.tmp")
fct99_ecmp = getList99FCT("out.tmp")
overallC_ecmp = getCompletionTime("out.tmp")
ooo_ecmp = getTotOOO("out.tmp")

# VALIANT
run_string = 'sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --algorithm=valiant --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > out.tmp'
print(run_string)
os.system(run_string)
fct_valiant = getListFCT("out.tmp")
fct99_valiant = getList99FCT("out.tmp")
overallC_valiant = getCompletionTime("out.tmp")
ooo_valiant = getTotOOO("out.tmp")

# UGAL
run_string = 'sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --algorithm=ugal --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > out.tmp'
print(run_string)
os.system(run_string)
fct_ugal = getListFCT("out.tmp")
fct99_ugal = getList99FCT("out.tmp")
overallC_ugal = getCompletionTime("out.tmp")
ooo_ugal = getTotOOO("out.tmp")

# FLOWLET1
run_string = 'sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --flowlet_timeout=3000 --routing=flowlet --algorithm=ugal --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > out.tmp'
print(run_string)
os.system(run_string)
fct_flowlet = getListFCT("out.tmp")
fct99_flowlet = getList99FCT("out.tmp")
overallC_flowlet = getCompletionTime("out.tmp")
ooo_flowlet = getTotOOO("out.tmp")

# FLOWLET2
run_string = 'sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --flowlet_timeout=11000 --routing=flowlet --algorithm=ugal --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > out.tmp'
print(run_string)
os.system(run_string)
fct_flowlet2 = getListFCT("out.tmp")
fct99_flowlet2 = getList99FCT("out.tmp")
overallC_flowlet2 = getCompletionTime("out.tmp")
ooo_flowlet2 = getTotOOO("out.tmp")

# FLOWLET3
run_string = 'sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --flowlet_timeout=20000 --routing=flowlet --algorithm=ugal --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > out.tmp'
print(run_string)
os.system(run_string)
fct_flowlet3 = getListFCT("out.tmp")
fct99_flowlet3 = getList99FCT("out.tmp")
overallC_flowlet3 = getCompletionTime("out.tmp")
ooo_flowlet3 = getTotOOO("out.tmp")

# FLOWCUT
run_string = 'sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --flowcut_mode=2 --exponential_alpha=0.7 --flowcut_max_ratio=6 --flowcut_value=10000 --routing=slingshot --algorithm=ugal --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > out.tmp'
print(run_string)
os.system(run_string)
fct_flowcut = getListFCT("out.tmp")
fct99_flowcut = getList99FCT("out.tmp")
overallC_flowcut = getCompletionTime("out.tmp")
ooo_flowcut = getTotOOO("out.tmp")


all_data = [statistics.mean(fct_ecmp), statistics.mean(fct_valiant), statistics.mean(fct_ugal), statistics.mean(fct_flowlet), statistics.mean(fct_flowlet2), statistics.mean(fct_flowlet3), statistics.mean(fct_flowcut)]

# Create a list of labels for each dataset
labels = ['ECMP', 'Valiant', 'UGAL', 'Flowlet\nBest\nPerf.', 'Flowlet\nBala.\nPerf.', 'Flowlet\nLowest\nOOO', 'Flowcut']

plt.figure(figsize=(6, 4.5))
# Calculate the average value and 95% confidence interval for each list

# Create a bar plot using Seaborn
colors = ['#3274a1', '#e1812c', '#3a923a', '#c03d3e', '#9372b2']
colors = ["#53b280"] * 10

ax = sns.barplot(x=labels, y=all_data, ci=None, palette=colors)  # Setting ci=None disables the default error bars

ax.set_xticks(ax.get_xticks())
ax.set_yticks(ax.get_yticks())
ax.tick_params(labelsize=12.2)
ax.set_yticklabels([str(round(i,1)) for i in ax.get_yticks()], fontsize = 15)

# Set labels and title
plt.ylabel('Flow Completion Time ({})'.format("ms"),fontsize=15)
#plt.xlabel('Congestion Control Algorithm',fontsize=17.5)

plt.grid()  #just add this
plt.legend([],[], frameon=False)
ax.set_axisbelow(True)

# Show the plot
plt.tight_layout()
plt.savefig("avg_fct.svg", bbox_inches='tight')
plt.savefig("avg_fct.png", bbox_inches='tight')
plt.savefig("avg_fct.pdf", bbox_inches='tight')
plt.close()

# PLOT OVERALL
all_data = [overallC_ecmp, overallC_valiant, overallC_ugal, overallC_flowlet, overallC_flowlet2, overallC_flowlet3, overallC_flowcut]

# Create a list of labels for each dataset
labels = ['ECMP', 'Valiant', 'UGAL', 'Flowlet\nBest\nPerf.', 'Flowlet\nBala.\nPerf.', 'Flowlet\nLowest\nOOO', 'Flowcut']

plt.figure(figsize=(6, 4.5))
# Calculate the average value and 95% confidence interval for each list

# Create a bar plot using Seaborn
colors = ['#3274a1', '#e1812c', '#3a923a', '#c03d3e', '#9372b2']
colors = ["#53b280"] * 10

ax = sns.barplot(x=labels, y=all_data, ci=None, palette=colors)  # Setting ci=None disables the default error bars
ax.set_xticks(ax.get_xticks())
ax.set_yticks(ax.get_yticks())
ax.tick_params(labelsize=12.2)
ax.set_yticklabels([str(round(i,1)) for i in ax.get_yticks()], fontsize = 15)

# Set labels and title
plt.ylabel('Job Completion Time ({})'.format("ms"),fontsize=15)
#plt.xlabel('Congestion Control Algorithm',fontsize=17.5)

plt.grid()  #just add this
plt.legend([],[], frameon=False)
ax.set_axisbelow(True)

# Show the plot
plt.tight_layout()
plt.savefig("completion.svg", bbox_inches='tight')
plt.savefig("completion.png", bbox_inches='tight')
plt.savefig("completion.pdf", bbox_inches='tight')
plt.close()

# PLOT OOO
all_data = [ooo_ecmp, ooo_valiant, ooo_ugal, ooo_flowlet, ooo_flowlet2, ooo_flowlet3, 0]

# Create a list of labels for each dataset
labels = ['ECMP', 'Valiant', 'UGAL', 'Flowlet\nBest\nPerf.', 'Flowlet\nBala.\nPerf.', 'Flowlet\nLowest\nOOO', 'Flowcut']

plt.figure(figsize=(6, 4.5))
# Calculate the average value and 95% confidence interval for each list

# Create a bar plot using Seaborn
colors = ['#3274a1', '#e1812c', '#3a923a', '#c03d3e', '#9372b2']
colors = ["#c0696c"] * 10

ax = sns.barplot(x=labels, y=all_data, palette=colors)  # Setting ci=None disables the default error bars
ax.set_xticks(ax.get_xticks())
ax.set_yticks(ax.get_yticks())
ax.tick_params(labelsize=12.2)
ax.set_yticklabels([str(round(i,1)) for i in ax.get_yticks()], fontsize = 15)

# Set labels and title
plt.ylabel('Packets out-of-order (%)',fontsize=15)    
#plt.xlabel('Congestion Control Algorithm',fontsize=17.5)

plt.grid()  #just add this
plt.legend([],[], frameon=False)
ax.set_axisbelow(True)

# Show the plot
plt.tight_layout()
plt.savefig("ooo.svg", bbox_inches='tight')
plt.savefig("ooo.png", bbox_inches='tight')
plt.savefig("ooo.pdf", bbox_inches='tight')
plt.close()