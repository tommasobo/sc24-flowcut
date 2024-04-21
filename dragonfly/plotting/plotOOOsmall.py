import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np
import matplotlib.patches as mpatches

import sharedValues

plt.rc('font', size=12.5)          # controls default text sizes
plt.rc('axes', titlesize=13.5)     # fontsize of the axes title
plt.rc('figure', titlesize=25)     # fontsize of the axes title
plt.rc('axes', labelsize=12.5)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=11.2)    # legend fontsize

# Create dataset
ugal = [-11,85.1,67.7,20.3,6.2,27.3]
flow = [-37.1,46,19.6,10.2,2.1,19.0]
sling = [-44.2,31.4,28.1,9,6.6,18.9]

ooo1 = [64.6, 56, 57.5, 13.2, 19.2, 25.8]
ooo2 = [3.4, 2.4, 4, 0, 4.1, 1.3]
ooo3 = [0, 0, 0, 0, 0, 0]

bars = ('ECMP', 'UGAL-4', 'Flowlet\n850ns\nTimeout', 'Flowlet\n5000ns\nTimeout', 'Flowlet\n7500ns\nTimeout', 'Slingshot')
x_pos = np.arange(len(bars))

pos_y = [1,6,11,16,21,26]
pos_y2 = [2,7,12,17,22,27]
pos_y3 = [3,8,13,18,23,28]

pos_ylabel = [2.5,7.5,12.5,17.5,22.5,27.5]

list_bench = ["Uniform", "Random", "ADV+1", "AllToAll", "ResNet50", "BERT"]


ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Percentage of Out-Of-Order (OOO) packets ",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.055,
    fontsize=14
)
# xlabel
'''ax.set_xlabel(
	"Routing Scheme",
)'''
# ylabel
ax.set_ylabel(
	"Application Name",
	horizontalalignment='left',
	rotation = 0,
)
ax.yaxis.set_label_coords(0, 1.01)
#ax.text(3.91, 2030, 'Out Of Order Packets (%)', size=11.2, color='black')

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
width = 1  # the width of the bars

barlist = ax.barh(pos_y, ooo1, width, color=sharedValues.color_background_traffic, alpha=sharedValues.alpha_bar_plots)

 
# Create names on the x-axis

ax.set_xlim(left=0, right=100)
#ax2.set_ylim(top=100)
rects2 = ax.barh(pos_y2, ooo2, width, color=sharedValues.color_main_traffic, alpha=sharedValues.alpha_bar_plots)
rects3 = ax.barh(pos_y3, ooo3, width, color=sharedValues.color_extent, alpha=sharedValues.alpha_bar_plots)

#ax2.set_yticks(np.linspace(0, 100, 9)) 

count = 0
for rect in barlist:
    height = rect.get_height()
    width = rect.get_width()
    print(width)
    add = 5
    sign = ""
    if (ooo1[count] < 0):
        add = -7
        sign = ""
    ax.text(rect.get_x() + width + add, rect.get_y() + 1* (height / 2),
            sign + str(int(ooo1[count])) + "%",
            ha='center', va='center', color=sharedValues.color_background_traffic, fontsize=10.3)
    count += 1
count = 0
for rect in rects2:
    height = rect.get_height()
    width = rect.get_width()
    print(width)
    add = 5
    sign = ""
    if (ooo2[count] < 0):
        add = -7
        sign = ""
    ax.text(rect.get_x() + width + add, rect.get_y() + 1* (height / 2),
            sign + str(int(ooo2[count])) + "%",
            ha='center', va='center', color=sharedValues.color_main_traffic, fontsize=10.3)
    count += 1
count = 0
for rect in rects3:
    height = rect.get_height()
    width = rect.get_width()
    print(width)
    add = 5
    sign = ""
    if (ooo3[count] < 0):
        add = -7
        sign = ""
    ax.text(rect.get_x() + width + add, rect.get_y() + 1* (height / 2),
            sign + str(int(ooo3[count])) + "%",
            ha='center', va='center', color=sharedValues.color_extent, fontsize=10.3)
    count += 1




ax.set_yscale('linear')
#ax.set_ylim(bottom=0)
#ax.set_ylim(top=60)
plt.minorticks_off()

# y grid
ax.grid(axis='x', color='w', linewidth=2, linestyle='-')
ax.set_axisbelow(True)
# hide ticks y-axis
ax.tick_params(axis='y', left=True, right=False)
# spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# AX 2
# y grid
#ax2.grid(axis='y', color='w', linewidth=2, linestyle='-')
#ax2.set_axisbelow(True)
# hide ticks y-axis

ax.xaxis.set_tick_params(labelsize=11.2)
ax.yaxis.set_tick_params(labelsize=11.2)
ax.set_yticks(pos_ylabel)
ax.set_yticklabels(list_bench)

#LEgend
#LEgend
legend_dict = {'Slingshot' : sharedValues.color_extent, 'Flowlet\n(Balanced Perf.)' : sharedValues.color_main_traffic, 'UGAL-4' : sharedValues.color_background_traffic}
patchList = []
for key in legend_dict:
		data_key = mpatches.Patch(color=legend_dict[key], label=key)
		patchList.append(data_key)

leg = ax.legend(handles=patchList, loc='upper right')
plt.xlabel("OOO packets (%)")

plt.gcf().set_size_inches(6, 5)
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("oooSmall") + file_name))
plt.savefig(Path("plots/pdf") / (str("oooSmall") + file_name + ".pdf"))
# Finally Show the plot
plt.show()