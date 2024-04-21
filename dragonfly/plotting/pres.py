import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np
import matplotlib.patches as mpatches

import sharedValues

 #size
plt.rc('font', size=11.2)          # controls default text sizes
plt.rc('axes', titlesize=13.0)     # fontsize of the axes title
plt.rc('figure', titlesize=25)     # fontsize of the axes title
plt.rc('axes', labelsize=11.2)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=10.2)    # legend fontsize

# Create dataset
height = [160040, 150002, 151232, 154278, 157238, 150702]
ooo = [0, 19.2, 17.2, 4.4, 0, 0]
bars = ('ECMP', 'UGAL-4', 'Flowlet\n2500ns\nTimeout', 'Flowlet\n40300ns\nTimeout', 'Flowlet\n70150ns\nTimeout', 'Slingshot')
x_pos = np.arange(len(bars))



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Runtime and Out Of Order (OOO) packets per routing scheme running\nResNet50 motif",
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
	"Runtime (μs)",
	horizontalalignment='left',
	rotation = 0,
)
ax.yaxis.set_label_coords(0, 1.012)
ax.text(3.91, 225900, 'Out Of Order Packets (%)', size=11.2, color='black')

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
width = 0.35  # the width of the bars

barlist = ax.bar(x_pos - width/2, height, width, color=sharedValues.color_global_ports[0], alpha=sharedValues.alpha_bar_plots)

 
# Create names on the x-axis
plt.xticks(x_pos, bars)
ax.set_ylim(bottom=0, top=225000)
ax2 = ax.twinx()
mn, mx = ax.get_ylim()
ax2.set_ylim(top=100)
rects2 = ax2.bar(x_pos + width/2, ooo, width, color="grey", alpha=sharedValues.alpha_bar_plots)
ax2.set_yticks(np.linspace(0, 100, 10)) 


barlist[0].set_color(sharedValues.color_global_ports[1])
barlist[1].set_color(sharedValues.color_global_ports[1])

barlist[5].set_color(sharedValues.color_extent)

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

# AX 2
# y grid
#ax2.grid(axis='y', color='w', linewidth=2, linestyle='-')
#ax2.set_axisbelow(True)
# hide ticks y-axis
ax2.tick_params(axis='y', left=False, right=False)
# spines
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)

ax.xaxis.set_tick_params(labelsize=11.2)
ax.yaxis.set_tick_params(labelsize=11.2)
ax2.xaxis.set_tick_params(labelsize=11.2)
ax2.yaxis.set_tick_params(labelsize=11.2)

#LEgend
legend_dict = {'Runtime per packet path selection' : sharedValues.color_background_traffic, 'Runtime per Flowlet Time path selection' : sharedValues.color_main_traffic, 'Runtime per Flowlet ACK path selection' : sharedValues.color_extent, "" : "#000000", "OOO Packets %" : "grey"}
patchList = []
for key in legend_dict:
		data_key = mpatches.Patch(color=legend_dict[key], label=key)
		patchList.append(data_key)

leg = ax.legend(handles=patchList, loc='best')
for idx, lh in enumerate(leg.legendHandles): 
	if (idx == 3):
		lh.set_alpha(0)

plt.gcf().set_size_inches(8.5, 6)
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("runtime_ooo") + file_name))
plt.savefig(Path("plots/pdf") / (str("runtime_ooo") + file_name + ".pdf"))
# Finally Show the plot
plt.show()