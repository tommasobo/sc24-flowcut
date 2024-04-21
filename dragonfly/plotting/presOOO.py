import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np

import sharedValues
plt.rcParams["figure.figsize"] = (7.2,6)


# Create dataset
#height = [0, 8.3, 22.2, 0.88, 0]
#bars = ["ECMP", "Adaptive", "Valiant", "Flowlet Switching", "Flowcut Switching - MPR"]

height = [0, 15.3, 32.2, 2.18, 0]
bars = ["Flowcut Switching MPR - All Re-Routing", "Flowcut Switching MPR - Ingress Re-Routing"]

#bars = ('ECMP', 'Valiant', 'UGAL-L', 'Timeout = 450ns', 'Timeout = 650ns', 'Timeout = 1000ns', 'Slingshot +\nUGAL-A')
x_pos = np.arange(len(bars))



ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Packets OOO - Random Permutation (Web-search) - Dragonfly",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.035
)
# xlabel
ax.set_xlabel(
	"Routing Scheme",
)
# ylabel
ax.set_ylabel(
	"Packets out-of-order (%)",
	#horizontalalignment='left',
	rotation = 90,
)
ax.yaxis.set_label_coords(0, 1.012)

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
barlist = plt.bar(x_pos, height, color=sharedValues.color_global_ports[0])
 
# Create names on the x-axis
plt.xticks(x_pos, bars)

barlist[0].set_color(sharedValues.color_global_ports[1])
barlist[1].set_color(sharedValues.color_global_ports[1])

barlist[len(bars) - 1].set_color(sharedValues.color_global_ports[2])

plt.gcf().set_size_inches(12, 6.5)
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("violinDuration") + file_name))
plt.savefig(Path("plots/pdf") / (str("violinDuration") + file_name + ".pdf"))
# Finally Show the plot
plt.show()