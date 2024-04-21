import re
import os
import argparse
import numpy as np
from datetime import datetime
from pathlib import Path    

for root, dirs, files in os.walk("tmpOut/parseMe/"):
    for file in files:
        list_latencies = []
        list_hops = []
        num_pkts = 0
        num_ooo = 0
        num_cached = 0
        num_flowlets = 0
        num_slingshot = 0
        num_latency = 0
        num_cached_slingshot = 0
        runtime = ""

        data = []
        already_matched_name = False

        with open("tmpOut/parseMe/" + file) as fp:
            Lines = fp.readlines()

            data = list()
            for line in Lines:
                match = re.search("EMBER: Motif='(\w+)\s+", line)
                if match:
                    program_name = (str(match.group(1)))
                    if already_matched_name is False:
                        data.append("programName," + str(program_name))
                        already_matched_name = True
                    
                match = re.search('EMBER: numNodes=(\d+)', line)
                if match:
                    num_nodes = (int(match.group(1)))
                    data.append("numNodes," + str(num_nodes))

                match = re.search('routing=(\w+)', line)
                if match:
                    routing_scheme = (str(match.group(1)))
                    data.append("routingScheme," + str(routing_scheme))

                match = re.search('defaultRouting=(\w+)', line)
                if match:
                    routing_algo = (str(match.group(1)))
                    data.append("routingAlgo," + str(routing_algo))

                match = re.search('FCT (\d+) (\d+) - (\d+) (\d+) (\d+) - (\d+) (\d+)', line)
                if match:
                    list_latencies.append(int(match.group(5)))
                    num_latency += 1

                match = re.search('Latency OOO is: (\d+)', line)
                if match:
                    list_latencies.append(int(match.group(1)))
                    num_latency += 1

                match = re.search('Num Hops: (\d+)', line)
                if match:
                    list_hops.append(int(match.group(1)))

                if "New Flowlet" in line:
                    num_flowlets += 1

                if "Using Cached Flowlet" in line:
                    num_cached += 1
                
                if "New Flowlet Slingshot" in line:
                    num_slingshot += 1

                if "Using Cached Slingshot" in line:
                    num_cached_slingshot += 1

                if "Packet Data Seen" in line:
                    num_pkts += 1

                if "Packet Data OOO" in line:
                    num_ooo += 1

                match = re.search('Runtime: (\d+)', line)
                if match:
                    runtime = (int(match.group(1)))

        print("File name is {} - Runtime {}".format(str(file), str(runtime)))
        if ("sling" in str(file)):
            avg_latency_ns = sum(list_latencies) / len(list_latencies)
            a = np.array(list_latencies)
            avg95_latency_ns = np.percentile(a, 95)
            avg99_latency_ns = np.percentile(a, 99)
            avg90_latency_ns = np.percentile(a, 90)
            print("Avg latency is {} us".format(str(avg_latency_ns / 1000)))
            print("90th percentile is {} - 95th percentile is {} - 99th percentile latency is {} us".format(str(avg90_latency_ns / 1000), str(avg95_latency_ns / 1000), str(avg99_latency_ns / 1000)))
            a2 = np.array(list_latencies)
            avg98_latency_ns = np.percentile(a2, 98.0)
            print("99.99 lat is " + str(avg98_latency_ns))
            list_latencies[:] = [x for x in list_latencies if x <= avg98_latency_ns]
        avg_latency_ns = sum(list_latencies) / len(list_latencies)
        a = np.array(list_latencies)
        avg95_latency_ns = np.percentile(a, 95)
        avg99_latency_ns = np.percentile(a, 99)
        avg90_latency_ns = np.percentile(a, 90)
        tot_cac_new = num_cached + num_flowlets
        tot_cac_new_sling = num_cached_slingshot + num_slingshot
        

        print("Number of total packets is {}".format(str(num_latency)))
        if tot_cac_new != 0:
            print("Flowlet - % Cached {} - % New {}".format(str((num_cached / tot_cac_new) * 100), str((num_flowlets / tot_cac_new) * 100)))
        if tot_cac_new_sling != 0:
            print("Sling - % Cached {} - % New {}".format(str((num_cached_slingshot / tot_cac_new_sling) * 100), str((num_slingshot / tot_cac_new_sling) * 100)))
        #print("% OOO {}".format(str((num_ooo / num_pkts) * 100)))
        print("Avg latency is {} us".format(str(avg_latency_ns / 1000)))
        print("90th percentile is {} - 95th percentile is {} - 99th percentile latency is {} us".format(str(avg90_latency_ns / 1000), str(avg95_latency_ns / 1000), str(avg99_latency_ns / 1000)))
        print("")
