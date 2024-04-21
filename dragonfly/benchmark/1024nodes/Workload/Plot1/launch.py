import re
import subprocess
from pathlib import Path
import sys
from argparse import ArgumentParser
import pathlib
import os
import time
sys.path.append("../")
from general_bench import *

topologies = {
  "dragonfly_min": 0,
  "dragonfly_ugal": 0,
  "dragonfly_valiant": 0,
  "dragonfly_flowlets": 300,
  "dragonfly_flowletm": 1000,
  "dragonfly_flowletl": 10000,
  "dragonfly_flowcut": 0,
}

topologies = {
  "dragonfly_flowlets": 400,
  "dragonfly_flowletm": 2500,
  "dragonfly_flowletl": 100000,
}

topologies = {
  "dragonfly_min": 0,
  "dragonfly_flowcut": 0,
}


topologies = {
  "dragonfly_min": 0,
  "dragonfly_ugal": 0,
  "dragonfly_valiant": 0,
  "dragonfly_flowlets": 300,
  "dragonfly_flowcut": 0,
}

sizes = [512, 8192, 65536, 131072, 2**19, 2**21, 2*23]
sizes = [655360]

def create_motif_load(name):
    path_motif = pathlib.Path(motif_folder)
    path_motif.mkdir(parents=True, exist_ok=True)

    motif_content = ["[JOB_ID] 10\n",
    "[NID_LIST] generateNidList=generateNidListRange(0,1024)\n",
    "[MOTIF] Init\n",
    "[MOTIF] Scatter messageSize=11\n",
    "[MOTIF] Fini"]

    with open(motif_folder + "/" + name, 'w') as file:
        file.writelines(motif_content)

def generate_simulations(args, to_replace, name, topologies, sizes):
    for msg_size in sizes:
        for topo in topologies:
            if (args.topo != "" and args.topo not in topo):
                continue
            timeout = 0
            print(topo)
            if (topologies[topo] != 0):
                timeout = topologies[topo]
            check_if_exist(topo, timeout)
            # Parse Current File, replace data and store it in an array
            new_lines = []
            generating_id_string = ""
            location_motif = motif_folder + "/" + name

            

            ## If jobs using all nodes
            if (args.size == 0):
                with open(location_motif, 'r') as f:
                    for line in f:
                        # Change topo size based on topology
                        if ("dragonfly" in topo or "fattree" in topo):
                            generating_id_string = generate_id_string_dragonfly

                        tmp = msg_size
                        line = re.sub(r"{}\d+".format(to_replace), "{}{}".format(to_replace, tmp), line)
                        new_lines.append(line)

                # Write the array back to the same file
                with open(location_motif, 'w') as file:
                    print(generating_id_string)
                    new_lines[1] = generating_id_string
                    file.writelines(new_lines)

            # If size is not zero then we need to create a custom motif with also null nids
            if (args.size != 0):
                create_motif_load(name, motif_folder, topo, args.size)
            run_sst(args, topo, msg_size, timeout, name)

def main(args):
    # Generate our custom Motif for this specific benchmark
    name = "Scatter"
    create_motif_load(name)
    generate_simulations(args, "messageSize=", name, topologies, sizes)    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--topo", type=str, help="Topology to run", default="")
    parser.add_argument("--env", type=str, help="Local or Cluster", default="", choices=["cluster", "daint", "ault", "local", "slimfly"])
    parser.add_argument("--num_threads", type=int, help="Number of threads to use for SST", default=8)
    parser.add_argument("--nodes", type=int, help="Number of nodes for cluster", default="8")
    parser.add_argument("--cpus_per_task", type=str, help="Number of cores per node for cluster", default="8")
    parser.add_argument("--mem", type=str, help="Memory per Node for cluster", default="16G")
    parser.add_argument("--hostfile", type=str, help="Hostfile name for Slimfly", default="hostfile")
    parser.add_argument("--size", type=str, help="Size of the job", default=0)    
    args = parser.parse_args()
    main(args)
