import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np
import matplotlib.patches as mpatches

import sharedValues

 #size
plt.rc('font', size=12.5)          # controls default text sizes
plt.rc('axes', titlesize=13.5)     # fontsize of the axes title
plt.rc('figure', titlesize=25)     # fontsize of the axes title
plt.rc('axes', labelsize=12.5)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=10.0)    # legend fontsize

# Create dataset
flowchip_switching_1 = [724, 845, 1200, 2001]
flowchip_switching_2 = [733, 900, 1244, 2230]
flowchip_switching_3 = [719, 807, 1111, 1600]
flowchip_switching_4 = [757, 817, 1151, 1799]

legend_name = ["Flowcut Switching - All", "Flowcut Switching - Ingress", "Flowcut Switching MPR - All", "Flowcut Switching MPR - Ingress"]

flowchip_switching_1[0] = flowchip_switching_1[0] * 6
flowchip_switching_2[0] = flowchip_switching_2[0] * 6
flowchip_switching_3[0] = flowchip_switching_3[0] * 6
flowchip_switching_4[0] = flowchip_switching_4[0] * 6

flowchip_switching_1[1] = flowchip_switching_1[1] * 4.7
flowchip_switching_2[1] = flowchip_switching_2[1] * 4.7
flowchip_switching_3[1] = flowchip_switching_3[1] * 4.7
flowchip_switching_4[1] = flowchip_switching_4[1] * 4.7

flowchip_switching_1[2] = flowchip_switching_1[2] * 2.9
flowchip_switching_2[2] = flowchip_switching_2[2] * 2.9
flowchip_switching_3[2] = flowchip_switching_3[2] * 2.9
flowchip_switching_4[2] = flowchip_switching_4[2] * 2.9

ooo = [20, 40, 60, 80]
bars = ('20', '40', '60', '80')
x_pos = np.arange(len(bars))



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Where to re-route traffic? (Uniform Random Traffic)",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.055,
    fontsize=14
)
# xlabel
ax.set_xlabel(
	"Offered Load (%)",
)
# ylabel
ax.set_ylabel(
	"AVG FCT (μs)",
	horizontalalignment='left',
	rotation = 0,
)
ax.yaxis.set_label_coords(0, 1.012)

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
width = 0.7  # the width of the bars

barlist1 = ax.plot(x_pos, flowchip_switching_1, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[0], color=sharedValues.color_global_ports[1])
barlist2 = ax.plot(x_pos, flowchip_switching_2, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[1], color=sharedValues.color_global_ports[1], linestyle = 'dotted')
barlist2 = ax.plot(x_pos, flowchip_switching_3, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[2], color=sharedValues.color_global_ports[0])
barlist2 = ax.plot(x_pos, flowchip_switching_4, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[3], color=sharedValues.color_global_ports[0], linestyle = 'dotted')
 
# Create names on the x-axis
plt.xticks(x_pos, bars)
#ax.set_ylim(bottom=0, top=2000)
mn, mx = ax.get_ylim()

ax.set_yscale('linear')
ax.set_ylim(bottom=500)
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


ax.xaxis.set_tick_params(labelsize=12.5)
ax.yaxis.set_tick_params(labelsize=12.5)


#LEgend
'''legend_dict = {'ECMP' : sharedValues.color_global_ports[0], 'Flowchip Switching' : sharedValues.color_global_ports[1], 'Flowlet Switching' : sharedValues.color_global_ports[2]}
patchList = []
for key in legend_dict:
		data_key = mpatches.Patch(color=legend_dict[key], label=key)
		patchList.append(data_key)

leg = ax.legend(handles=patchList, loc='best')
for idx, lh in enumerate(leg.legendHandles): 
	if (idx == 5):
		lh.set_alpha(0)
'''
plt.gcf().set_size_inches(8, 6)
plt.legend(loc="lower left")
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("runtime_ooo") + file_name))
plt.savefig(Path("plots/pdf") / (str("runtime_ooo") + file_name + ".pdf"))
# Finally Show the plot
plt.show()