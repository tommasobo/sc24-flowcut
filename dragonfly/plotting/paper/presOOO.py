import matplotlib.pyplot as plt
from pathlib import Path    
from datetime import datetime
import numpy as np

import sharedValues


# Create dataset
'''height = [0, 74.2, 68.2, 23.9, 3.2, 0]
bars = ('ECMP', 'UGAL-L', 'UGAL-Sling', 'Valiant', 'Flowlet\nSwitching', 'Flowcut\nSwitching')
x_pos = np.arange(len(bars))'''

height = [0, 38.3, 72.2, 2.88, 0]
bars = ["ECMP", "Adaptive", "Valiant", "Flowlet\nSwitching", "Flowcut\nSwitching - MPR"]

#bars = ('ECMP', 'Valiant', 'UGAL-L', 'Timeout = 450ns', 'Timeout = 650ns', 'Timeout = 1000ns', 'Slingshot +\nUGAL-A')
x_pos = np.arange(len(bars))


ax = plt.axes(facecolor=sharedValues.color_background_plot)

# Title and Labels
ax.set_title(
	label = "Amount of Out-Of-Order Packets",
	weight = 'bold',
	horizontalalignment = 'left',
	x = 0,
	y = 1.005
)
# xlabel
ax.set_xlabel(
	"Routing Scheme",
)
# ylabel
ax.set_ylabel(
	"Packets out-of-order (%)",
)

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
barlist = plt.bar(x_pos, height)
 
# Create names on the x-axis
plt.xticks(x_pos, bars)

barlist[0].set_color("#272727")
barlist[1].set_color("#FE8419")
barlist[2].set_color("#379E2A")
barlist[3].set_color("#C82E2E")
barlist[4].set_color("#996EBF")
#barlist[5].set_color(sharedValues.color_global_ports[1])

plt.gcf().set_size_inches(7, 5.5)
plt.tight_layout()
Path("plots/png").mkdir(parents=True, exist_ok=True)
Path("plots/pdf").mkdir(parents=True, exist_ok=True)
file_name = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')
plt.savefig(Path("plots/png") / (str("ooo_drag_adv") + file_name))
plt.savefig(Path("plots/pdf") / (str("ooo_drag_adv") + file_name + ".pdf"))
# Finally Show the plot
plt.show()