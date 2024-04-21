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

ecmp = [48, 51, 58, 59, 61]
adaptive = [27, 29.4, 32.4, 35, 38]
valiant = [72, 74.4, 86.4, 99, 121]
flowlet_switching = [48, 46, 47.2, 54, 58]
flowchip_switching = [44.5, 46.2, 48.6, 51.2, 54.27]
slingshot = [40.2, 41.2, 44.6, 47.2, 49.27]

'''flowchip_switching_0 = [232, 233.34, 240.2, 248.34, 249.32]
flowchip_switching_1 = [236, 239.34, 241.2, 247.34, 255.32]
flowchip_switching_2 = [216, 219.34, 222.2, 228.34, 231.32]
flowchip_switching_3 = [201, 204, 215.3, 226.3, 227.4]
flowchip_switching_4 = [208, 209.3, 217.1, 228.34, 231.32]
flowchip_switching_5 = [211, 215.34, 222.2, 232.34, 242.32]
flowchip_switching_6 = [211.21, 216.2, 221.2, 236.34, 245.32]'''


#legend_name = ["ECMP", "UGAL-L", "UGAL-Sling", "Valiant", "Flowlet Switching", "Flowcut Switching - MPR"]

legend_name = ["ECMP", "Adaptive", "Valiant", "Flowlet Switching", "Flowcut Switching Default", "Flowcut Switching MPR"]
#legend_name = ["Flowcut Switching MPR - All Re-Routing", "Flowcut Switching MPR - Ingress Re-Routing"]
#legend_name = ["Flowcut Switching", "Flowcut Switching - MFD", "Flowcut Switching - MQL", "Flowcut Switching - MPR", "Flowcut Switching - MPRG", "Flowcut Switching - MRM", "Flowcut Switching - MRMG"]


ooo = [20, 40, 60, 80, 100]
bars = ('20', '40', '60', '80', '100')
x_pos = np.arange(len(bars))



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Permutation Web Search",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.005,
    fontsize=14
)
# xlabel
ax.set_xlabel(
	"Offered Load (%)",
)
# ylabel
ax.set_ylabel(
	"AVG FCT (μs)"
)
#ax.yaxis.set_label_coords(0, 1.012)

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
width = 0.7  # the width of the bars

barlist = ax.plot(x_pos, ecmp, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[0])
barlist = ax.plot(x_pos, adaptive, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[1])
barlist = ax.plot(x_pos, valiant, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[2])
barlist2 = ax.plot(x_pos, flowlet_switching, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[3])
barlist1 = ax.plot(x_pos, flowchip_switching, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[4])
barlist = ax.plot(x_pos, slingshot, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[5])

'''
barlist1 = ax.plot(x_pos, flowchip_switching_0, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[0])
barlist1 = ax.plot(x_pos, flowchip_switching_1, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[1])
barlist1 = ax.plot(x_pos, flowchip_switching_2, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[2])
barlist1 = ax.plot(x_pos, flowchip_switching_3, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[3])
barlist1 = ax.plot(x_pos, flowchip_switching_4, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[4])
barlist1 = ax.plot(x_pos, flowchip_switching_5, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[5])
barlist1 = ax.plot(x_pos, flowchip_switching_6, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[6])
'''
# Create names on the x-axis
plt.xticks(x_pos, bars)
ax.set_ylim(bottom=0)
mn, mx = ax.get_ylim()


'''barlist[0].set_color(sharedValues.fourth_color)
barlist[1].set_color(sharedValues.color_global_ports[1])

barlist[5].set_color(sharedValues.color_extent)'''

ax.set_yscale('linear')
ax.set_ylim(bottom=0)
ax.set_ylim(top=150)
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
plt.legend(loc="lower right")
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("tree_fb_16") + file_name))
plt.savefig(Path("plots/pdf") / (str("tree_fb_16") + file_name + ".pdf"))
# Finally Show the plot
plt.show()