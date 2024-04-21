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
'''ecmp = [121, 154, 215, 446, 684]
ugal = [120, 157, 228, 400, 494]
flowlet_switching = [127, 154, 225, 434, 544]
flowchip_switching_1 = [124, 156, 228, 439, 599]
flowchip_switching_2 = [121, 154, 245, 426, 524]'''

'''ecmp = [643, 690, 724, 813, 1384]
ugal = [648, 701, 699, 764, 988]
flowlet_switching = [650, 700, 714, 799, 1120]
flowchip_switching_1 = [644, 702, 718, 806, 1100]
flowchip_switching_2 = [644, 705, 698, 777, 1080]'''

ecmp = [19, 30, 37, 77, 288]
ugal = [18, 24, 30, 50, 168]
flowlet_switching = [19, 27, 33, 63, 199]
flowchip_switching_1 = [19, 29, 33, 71, 222]
flowchip_switching_2 = [19, 27, 34, 65, 203]

legend_name = ["ECMP", "UGAL", "Flowlet Switching", "Flowcut Switching", "Flowcut Switching - MPR"]


ooo = [20, 40, 60, 80, 100]
bars = ('20', '40', '60', '80', '100')
x_pos = np.arange(len(bars))



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Flow Completion Time - Web Search",
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
	"AVG FCT (us)",
)

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
width = 0.7  # the width of the bars

barlist = ax.plot(ooo, ecmp, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[0], color=sharedValues.color_global_ports[0])
barlist = ax.plot(ooo, ugal, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[1], color=sharedValues.color_global_ports[1])
barlist2 = ax.plot(ooo, flowlet_switching, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[2], color=sharedValues.color_extent)
barlist1 = ax.plot(ooo, flowchip_switching_1, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[3], color=sharedValues.fourth_color)
barlist2 = ax.plot(ooo, flowchip_switching_2, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[4], color="black")
'''barlist2 = ax.plot(x_pos, flowchip_switching_3, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[5])
barlist2 = ax.plot(x_pos, flowchip_switching_4, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[6])
barlist2 = ax.plot(x_pos, flowchip_switching_5, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[7])
barlist2 = ax.plot(x_pos, flowchip_switching_6, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[8])
barlist2 = ax.plot(x_pos, flowchip_switching_7, alpha=sharedValues.alpha_bar_plots, marker='o', label=legend_name[9])'''


ax.text(101,200,"Flowlet\n1.1% OOO", size=12,
                           verticalalignment='center', rotation=0, color=sharedValues.color_extent)

ax.text(101,167,"UGAL\n58% OOO", size=12,
						verticalalignment='center', rotation=0, color=sharedValues.color_global_ports[1])

 
# Create names on the x-axis
#plt.xticks(x_pos, bars)
#ax.set_ylim(bottom=0, top=2000)
mn, mx = ax.get_ylim()


'''barlist[0].set_color(sharedValues.fourth_color)
barlist[1].set_color(sharedValues.color_global_ports[1])

barlist[5].set_color(sharedValues.color_extent)'''

ax.set_yscale('linear')
#ax.set_ylim(bottom=400)
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
plt.legend(loc="upper left")
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("runtime_ooo") + file_name))
plt.savefig(Path("plots/pdf") / (str("runtime_ooo") + file_name + ".pdf"))
# Finally Show the plot
plt.show()