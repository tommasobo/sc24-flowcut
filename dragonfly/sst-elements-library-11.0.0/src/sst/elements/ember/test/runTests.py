import subprocess
import  fileinput
from pathlib import Path


list_algo = ["minimal", "valiant", "adaptive-local", "ugal"]
list_routing = ["default", "flowlet", "slingshot"]
motif_file_name = "loadMotifAuto"

file = Path(motif_file_name)
file.write_text(file.read_text().replace("ugal", "minimal"))
file.write_text(file.read_text().replace("flowlet", "default"))
count = 0

for idx_r, routing in enumerate(list_routing):
    for idx_a, algo in enumerate(list_algo):
        string = 'time sst --num_threads=4 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --shape=16:16:16:4  --routing=' + routing + ' --algorithm=' + algo + ' --flowlet_timeout=40000000 --loadFile=loadMotifAuto" emberLoad.py > tmpOut/out' + str(count)
        process = subprocess.Popen([string], shell=True)
        process.wait()
        count += 1
        if (idx_a < (len(list_algo) - 1)):
            file = Path(motif_file_name)
            file.write_text(file.read_text().replace(list_algo[idx_a], list_algo[idx_a+1]))
        else:
            file = Path(motif_file_name)
            file.write_text(file.read_text().replace("ugal", "minimal"))
    if (idx_r < (len(list_routing) - 1)):
        file = Path(motif_file_name)
        file.write_text(file.read_text().replace(list_routing[idx_r], list_routing[idx_r+1]))
    