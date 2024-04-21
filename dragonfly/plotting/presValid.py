import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np

import sharedValues


plt.rc('font', size=12.5)          # controls default text sizes
plt.rc('axes', titlesize=13.5)     # fontsize of the axes title
plt.rc('figure', titlesize=25)     # fontsize of the axes title
plt.rc('axes', labelsize=12.5)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=7)    # fontsize of the tick labels
plt.rc('ytick', labelsize=22)    # fontsize of the tick labels
plt.rc('legend', fontsize=10.0)    # legend fontsize

# Create dataset
height = [2.3,3.18,19.9,99.4,179.1,341.3,509.3,669.3]
height2 = [1.79,2.60,15.9,91.1,169.2,334.1,491.0,654.5]

bars = ("8B", "1KiB", "128KiB", "1MiB", "2MiB", "4MiB", "6MiB", "8MiB")
x_pos = np.arange(len(bars))

percentage = [100*(LA_count - SF_count) / SF_count for SF_count, LA_count in zip(height, height2)]



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Eiger vs SST Performance - Ping Pong between 64 nodes - Different groups",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.050,
	fontsize=14
)
# xlabel
ax.set_xlabel(
	"Message Size",
)
# ylabel
ax.set_ylabel(
	"Runtime (us)",
	horizontalalignment='left',
	rotation = 0,
)
ax.yaxis.set_label_coords(0, 1.012)
ax.xaxis.set_tick_params(labelsize=12.5)
ax.yaxis.set_tick_params(labelsize=12.5)
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

# Create bars
#barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])

x = np.arange(len(x_pos))  # the label locations
width = 0.35  # the width of the bars

rects1 = plt.bar(x - width/2, height, width, label='Eiger', color=sharedValues.color_background_traffic)
rects2 = plt.bar(x + width/2, height2, width, label='SST', color=sharedValues.color_main_traffic)

count = 0
print(percentage)
for rect in rects1:
    print(str(count))
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., 1.008*height,
            "+" + str(int(abs(percentage[count]))) + "%",
            ha='center', va='bottom', color=sharedValues.color_background_traffic)
    count += 1

# Create names on the x-axis
plt.xticks(x_pos, bars)
ax.legend()

#barlist[0].set_color(sharedValues.color_global_ports[1])
#barlist[6].set_color(sharedValues.color_global_ports[2])

plt.gcf().set_size_inches(9.0, 5.6)
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
# Finally Show the plot
plt.show()