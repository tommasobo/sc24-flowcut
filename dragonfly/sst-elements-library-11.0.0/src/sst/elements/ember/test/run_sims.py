import subprocess
import os
import argparse

# parse
parser = argparse.ArgumentParser()
parser.add_argument('--only_flowlet', required=False, type=bool, default=False)
args = parser.parse_args()

routing_scheme = ["default", "slingshot", "flowlet"] # "slingshot", "flowlet"
#routing_scheme = ["default"] # "slingshot", "flowlet"
#routing_algo = ["ugal"]
routing_algo = ["ugal", "adaptive-local", "valiant"]

flowlet_timeout = 170000
out_dir = "tmpOut/" + "simpleNoBG/"
save_name_test = "simple"
ackMode="true"

os.makedirs(os.path.dirname(out_dir), exist_ok=True)


if (args.only_flowlet is False):
    # Run Minimal only with Default
    scheme = "default"
    algo = "minimal"
    save_name = save_name_test + scheme + "_" + algo
    string = 'time sst --num_threads=4 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --shape=16:16:16:4 --routing=' + str(scheme) + ' --algorithm=' + str(algo) + ' --flowlet_timeout=' + str(flowlet_timeout) + ' --ackMode=' + str(ackMode) + ' --loadFile=loadMotif" emberLoad.py > ' + str(out_dir) + str(save_name)
    print(string)
    process = subprocess.Popen([string], shell=True)
    process.wait()

    # Run Other Combinations
    for scheme in routing_scheme:
        for algo in routing_algo:
            flowlet_timeout = 170000
            if algo == "adaptive-local" or algo == "valiant":
                flowlet_timeout = 170000
            save_name = save_name_test + scheme + "_" + algo
            if (scheme == "flowlet"):
                ackMode="true"
                flowlet_timeout = 170000
            else:
                ackMode="true"
            string = 'time sst --num_threads=4 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --shape=16:16:16:4 --routing=' + str(scheme) + ' --algorithm=' + str(algo) + ' --flowlet_timeout=' + str(flowlet_timeout) + ' --ackMode=' + str(ackMode) + ' --loadFile=loadMotif" emberLoad.py > ' + str(out_dir) + str(save_name)
            print(string)
            if ((algo == "adapvctive-local") and (scheme == "slingshot" or scheme == "flowlet")):
                print("Skipping")
            else:
                process = subprocess.Popen([string], shell=True)
                process.wait()
else:
    # Run just flowlet
    print("Running Just Flowlet")
    scheme = "flowlet"
    flowlet_timeout = 5000000
    for algo in routing_algo:
        save_name = "AllPingPong_" + scheme + "_" + algo
        string = 'time sst --num_threads=4 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --shape=2:4:2:8 --routing=' + str(scheme) + ' --algorithm=' + str(algo) + ' --flowlet_timeout=' + str(flowlet_timeout) + ' --ackMode=true --loadFile=loadMotif" emberLoad.py > ' + str(out_dir) + str(save_name)
        process = subprocess.Popen([string], shell=True)
        process.wait()