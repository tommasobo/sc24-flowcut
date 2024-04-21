import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np
import matplotlib.patches as mpatches

import sharedValues


plt.rcParams["figure.figsize"] = (7.2,6)

 #size
plt.rc('font', size=12.5)          # controls default text sizes
plt.rc('axes', titlesize=13.5)     # fontsize of the axes title
plt.rc('figure', titlesize=25)     # fontsize of the axes title
plt.rc('axes', labelsize=12.5)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=10.0)    # legend fontsize

# Create dataset
height2 = [160040, 150002, 151232, 154278, 157238, 150702]
height = [(element * 400) / 1000 for element in height2]

# ooo = [0, 76.50, 53.62, 17.01, 4.665, 0.56, 0] DF_WEB
#ooo = [0, 67.20, 43.762, 9.58, 3.0665, 0.51, 0] DF_ENT
#ooo = [0, 33.910, 20.212, 14.51, 1.150665, 0.03, 0] DF_ATA
#ooo = [0, 39.810, 4.91, 0] FT_RANDOM
ooo = [0, 39.810, 4.91, 0] 

#bars = ('ECMP', 'UGAL', 'Valiant', 'Flowlet\nBest\nPerf.', 'Flowlet\nBalanced\nPerf.', 'Flowlet\nLowest\nOOO', 'Flowcut\nSwitching')
bars = ('ECMP', 'Adaptive', 'Flowlet\nBalanced\nPerf.', 'Flowcut\nSwitching')

x_pos = np.arange(len(bars))



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Packets OOO - Random Permutation (Random Distr.) - fattree",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	#y = 1.055,
    fontsize=13.0
)
# xlabel
'''ax.set_xlabel(
	"Routing Scheme",
)'''
# ylabel
ax.set_ylabel(
	"Packets out-of-order (%)",
	#horizontalalignment='left',
	rotation = 90,
)
#ax.yaxis.set_label_coords(0, 1.012)

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
width = 0.7  # the width of the bars

barlist = ax.bar(x_pos, ooo, width, color=sharedValues.color_global_ports[0], alpha=sharedValues.alpha_bar_plots)

 
# Create names on the x-axis
plt.xticks(x_pos, bars)
ax.set_ylim(bottom=0, top=100)
mn, mx = ax.get_ylim()


'''barlist[0].set_color(sharedValues.color_global_ports[1])
barlist[1].set_color(sharedValues.color_global_ports[1])

barlist[5].set_color(sharedValues.color_extent)'''

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


ax.xaxis.set_tick_params(labelsize=13.5)
ax.yaxis.set_tick_params(labelsize=13.5)


#LEgend
legend_dict = {'Per flow path selection' : sharedValues.fourth_color, 'Per packet path selection' : sharedValues.color_background_traffic, 'Per Flowlet Time path selection' : sharedValues.color_main_traffic, 'Per Flowlet ACK path selection' : sharedValues.color_extent}
patchList = []
for key in legend_dict:
		data_key = mpatches.Patch(color=legend_dict[key], label=key)
		patchList.append(data_key)

'''leg = ax.legend(handles=patchList, loc='best')
for idx, lh in enumerate(leg.legendHandles): 
	if (idx == 5):
		lh.set_alpha(0)'''
#plt.axhline(1.41, linestyle='--', alpha=0.4, color="grey")

#plt.gcf().set_size_inches(6, 5)
plt.tight_layout()
Path("plots1/png").mkdir(parents=True, exist_ok=True)
Path("plots1/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots1/png") / (str("OOO") + file_name))
plt.savefig(Path("plots1/pdf") / (str("OOO") + file_name + ".pdf"))
# Finally Show the plot
plt.show()