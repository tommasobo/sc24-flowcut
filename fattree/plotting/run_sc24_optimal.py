import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import matplotlib
import random

import sharedValues
plt.rcParams["figure.figsize"] = (7.2,6)

 #size
plt.rc('font', size=12.5)          # controls default text sizes
plt.rc('axes', titlesize=13.0)     # fontsize of the axes title
plt.rc('figure', titlesize=25)     # fontsize of the axes title
plt.rc('axes', labelsize=12.5)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=11.8)    # legend fontsize

# Create dataset
height = [1389, 840, 840, 1203, 1739, 1250]
ooo = [0, -1002, 50, 3.2, 0.15, 0]
bars = ('ECMP', 'UGAL-4', 'Flowlet\n850ns\nTimeout', 'Flowlet\n5000ns\nTimeout', 'Flowlet\n7500ns\nTimeout', 'Slingshot')
x_pos = np.arange(len(bars))

pos_y = [1,5,9,13]
pos_y2 = [2,6,10,14]
pos_y3 = [2,5,8,11, 14]

list_bench = ["Permutation", "Permutation\nwith failure", "Web\nSearch", "Alibaba", "All-To-All"]



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Optimal Flowlet timeout window for different applications",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.04
)
# xlabel
'''ax.set_xlabel(
	"Routing Scheme",
)'''
# ylabel
ax.set_ylabel(
	"Flowlet timeout (us)",
	horizontalalignment='left',
	rotation = 0,
)
ax.yaxis.set_label_coords(0, 1.012)
#ax.text(3.91, 2030, 'Out Of Order Packets (%)', size=11.2, color='black')

x = [1, 1]
y = [2.25, 2.75]

data = [[0.99, 5.5],[1.01,13.35],[0.9,14.8],[0.65,24.5],[1.59,82]]

medianprops = dict(linestyle='-.', linewidth=0, color='black')
'''ax.boxplot(data, showcaps=False,showfliers=False,  medianprops=medianprops, whiskerprops=medianprops, zorder=1)
ax.errorbar(x, y, yerr=0.1, linewidth=1, ls='none',zorder=2,color='black')'''

# Get the current reference
ax = plt.gca()


ax.set_yscale('linear')
#ax.set_ylim(bottom=0)
#ax.set_xlim(right=7)
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


# AX 2
# y grid
#ax2.grid(axis='y', color='w', linewidth=2, linestyle='-')
#ax2.set_axisbelow(True)
# hide ticks y-axis


rect1 = matplotlib.patches.Rectangle((1,data[0][0]), 2, data[0][1] - data[0][0], facecolor='black', fill=None)
rect2 = matplotlib.patches.Rectangle((4,data[1][0]), 2, data[1][1] - data[1][0], facecolor='black', fill=None)
rect3 = matplotlib.patches.Rectangle((7,data[2][0]), 2, data[2][1] - data[2][0], facecolor='black', fill=None)
rect4 = matplotlib.patches.Rectangle((10,data[3][0]), 2, data[3][1] - data[3][0], facecolor='black', fill=None)
rect5 = matplotlib.patches.Rectangle((13,data[4][0]), 2, data[4][1] - data[4][0], facecolor='black', fill=None)
ax.add_patch(rect1)
ax.add_patch(rect2)
ax.add_patch(rect3)
ax.add_patch(rect4)
ax.add_patch(rect5)
plt.ylim([0, 85])
plt.xlim([0, 17])


ax.plot(2,data[0][0],'o',zorder=3,color=sharedValues.color_timeout[2])
ax.plot(2,1.38,'o',zorder=3,color=sharedValues.color_timeout[1])
ax.plot(2,data[0][1],'o',zorder=3,color=sharedValues.color_timeout[0])

ax.plot(5,data[1][0],'o',zorder=3,color=sharedValues.color_timeout[2])
ax.plot(5,1.6,'o',zorder=3,color=sharedValues.color_timeout[1])
ax.plot(5,data[1][1],'o',zorder=3,color=sharedValues.color_timeout[0])

ax.plot(8,data[2][0],'o',zorder=3,color=sharedValues.color_timeout[2])
ax.plot(8,2.8,'o',zorder=3,color=sharedValues.color_timeout[1])
ax.plot(8,data[2][1],'o',zorder=3,color=sharedValues.color_timeout[0])

ax.plot(11,data[3][0],'o',zorder=3,color=sharedValues.color_timeout[2])
ax.plot(11,12.5,'o',zorder=3,color=sharedValues.color_timeout[1])
ax.plot(11,data[3][1],'o',zorder=3,color=sharedValues.color_timeout[0])

ax.plot(14,data[4][0],'o',zorder=3,color=sharedValues.color_timeout[2])
ax.plot(14,42,'o',zorder=3,color=sharedValues.color_timeout[1])
ax.plot(14,data[4][1],'o',zorder=3,color=sharedValues.color_timeout[0])


ax.xaxis.set_tick_params(labelsize=13.1)
ax.yaxis.set_tick_params(labelsize=13.1)
ax.set_xticks(pos_y3)
ax.set_xticklabels(list_bench)

#LEgend
legend_dict = {'Flowlet Lowest OOO' : sharedValues.color_timeout[0], 'Flowlet Balanced Performance' : sharedValues.color_timeout[1], 'Flowlet Best Performance' : sharedValues.color_timeout[2]}
patchList = []
for key in legend_dict:
		data_key = mpatches.Patch(color=legend_dict[key], label=key)
		patchList.append(data_key)

leg = ax.legend(handles=patchList, loc='upper left') 


#plt.gcf().set_size_inches(7.5, 5)
plt.tight_layout()

Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
plt.savefig(Path("plots/png") / (str("optimal") + ""))
plt.savefig(Path("plots/pdf") / (str("optimal") + "" + ".pdf"))