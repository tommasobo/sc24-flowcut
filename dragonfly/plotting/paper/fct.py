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
ecmp = [0.33, 0.556, 1.01, 1.38, 1.38, 1.8, 0.7, 1.23, 2.32, 4.7, 8.20, 9.93, 10.3, 10.7, 10.9, 10.99]
ecmp_1 = [0.63, 0.866, 1.67, 1.78, 1.99, 2.17, 2.18, 2.93, 2.72, 3.47, 6.62, 8.43, 8.93, 9.1, 9.2, 9.321]



ooo = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
bars = ('8B', '16B', '32B', '64B', '128B', '256B', '512B', '1KiB', '2KiB', '4KiB', '8KiB', '16KiB', '32KiB', '64KiB', '128KiB', '256KiB')
x_pos = np.arange(len(bars))



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Validating All To All vs Shandy",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.005,
    fontsize=14
)
# xlabel
ax.set_xlabel(
	"Message Size",
)
# ylabel
ax.set_ylabel(
	"Total Throughput (TB/s)",
)

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
width = 0.7  # the width of the bars

barlist = ax.plot(x_pos, ecmp, color=sharedValues.color_global_ports[0], alpha=sharedValues.alpha_bar_plots, marker='o')
barlist1 = ax.plot(x_pos, ecmp_1, color=sharedValues.color_global_ports[1], alpha=sharedValues.alpha_bar_plots, marker='o')

 
# Create names on the x-axis
plt.xticks(x_pos, bars)
#ax.set_ylim(bottom=0, top=2000)
mn, mx = ax.get_ylim()


'''barlist[0].set_color(sharedValues.fourth_color)
barlist[1].set_color(sharedValues.color_global_ports[1])

barlist[5].set_color(sharedValues.color_extent)'''

ax.set_yscale('linear')
ax.set_ylim(bottom=0)
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
ax.xaxis.set_major_locator(plt.MaxNLocator(8))


#LEgend

plt.gcf().set_size_inches(6, 5)
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("compare") + file_name))
plt.savefig(Path("plots/pdf") / (str("compare") + file_name + ".pdf"))
# Finally Show the plot
plt.show()