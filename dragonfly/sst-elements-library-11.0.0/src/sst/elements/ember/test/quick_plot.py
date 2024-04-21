import matplotlib.pyplot as plt

import re
import os
import argparse
import numpy as np
import statistics
from datetime import datetime
from pathlib import Path    

list_credit = [[] for i in range(5)]
list_credit_down = [[] for i in range(5)]
packet_list = [[] for i in range(5)]



for root, dirs, files in os.walk("tmpOut/parseMe/"):
    idx = 0
    for file in files:
        list_latencies = []
        runtimes = []
        idle = []
        band = []
        fct_time = []
        list_hops = []
        packet = []
        num_pkts = 0
        num_ooo = 0
        num_cached = 0
        num_ccredits = 0
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

                match = re.search('OOO (\d+) of (\d+)', line)
                if match:
                    ooo_num = int(match.group(1))
                    tot_pkt = int(match.group(2))                

                match = re.search('Flow BandWidth (\d+\.\d+) (\d+)', line)
                if match:
                    list_latencies.append(float(match.group(1)))
                    band.append(float(match.group(1)))
                    fct_time.append(int(match.group(2)))
                    num_latency += 1

                match = re.search('Rank (\d+) - Total Time (\d+\.\d+)', line)
                if match:
                    runtimes.append(float(match.group(2)))

                match = re.search('Credits Port (\d+)', line)
                if match:
                    list_credit[idx].append(int(match.group(1)))

                match = re.search('Down Port (\d+)', line)
                if match:
                    list_credit_down[idx].append(int(match.group(1)))

                match = re.search('Idle -> (\d+)', line)
                if match:
                    idle.append(int(match.group(1)))
                 

                match = re.search('Num Hops: (\d+)', line)
                if match:
                    list_hops.append(int(match.group(1)))
                
                match = re.search('Packet Latency -> (\d+)', line)
                if match:
                    packet.append(int(match.group(1)))
                    packet_list[idx].append(int(match.group(1)))


                if "New Flowlet" in line:
                    num_flowlets += 1

                if "Blocked" in line:
                    num_ccredits += 1

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
        '''if ("sling" in str(file)):
            avg_latency_ns = sum(list_latencies) / len(list_latencies)
            a = np.array(list_latencies)
            avg95_latency_ns = np.percentile(a, 95)
            avg99_latency_ns = np.percentile(a, 99)
            avg90_latency_ns = np.percentile(a, 90)
            print("Avg latency is {} us".format(str(avg_latency_ns / 1)))
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
        tot_cac_new_sling = num_cached_slingshot + num_slingshot'''
        

        '''print("Number of total packets is {}".format(str(num_latency)))
        if tot_cac_new != 0:
            print("Flowlet - % Cached {} - % New {}".format(str((num_cached / tot_cac_new) * 100), str((num_flowlets / tot_cac_new) * 100)))
        if tot_cac_new_sling != 0:
            print("Sling - % Cached {} - % New {}".format(str((num_cached_slingshot / tot_cac_new_sling) * 100), str((num_slingshot / tot_cac_new_sling) * 100)))
        #print("% OOO {}".format(str((num_ooo / num_pkts) * 100)))
        print("Avg latency is {} us".format(str(avg_latency_ns / 1)))'''
        print("Avg BDW is {} Gb/s - {} GB/s | Mean BDW is {} Gb/s".format(str(statistics.mean(band)), str(statistics.mean(band) / 8),str(statistics.median(band) / 8)))
        print("Avg FCT is {} ns - {} us - {} ms | Mean FCT is {} us".format(str(statistics.mean(fct_time)), str(statistics.mean(fct_time) / 1000), str(statistics.mean(fct_time) / 1000000), str(statistics.median(fct_time) / 1000)))
        #print("Idle Avg {} | Mean Idle {}".format(str(statistics.mean(idle)), str(statistics.median(idle) / 1)))
        if ("ecmp" in str(file)):
            ooo_num = 0
        print("Num OOO {} of {} - {}".format(str(ooo_num), str(tot_pkt), str(ooo_num/tot_pkt * 100)))
        #print("Avg RunTime {} | Median {}".format(str(statistics.mean(runtimes)), str(statistics.median(runtimes))))
        #print("Avg Packet {} | Median {}".format(str(statistics.mean(packet)), str(statistics.median(packet))))
        print("")
        idx += 1
'''
print(len(packet_list[0]))
print(len(packet_list[1]))

print(max(packet_list[0]))
print(max(packet_list[1]))

#plt.hist(packet_list[0], bins=100, label="Adaptive", alpha=0.5)
#plt.hist(packet_list[1], bins=100, label="Det", alpha=0.5)

packet_list[0] = [x for x in packet_list[0] if x > 100000]
packet_list[1] = [x for x in packet_list[1] if x > 100000]


_, bins, _ = plt.hist(packet_list[0], bins=50, alpha=0.5, label="Adaptive")
_ = plt.hist(packet_list[1], bins=bins, alpha=0.5, label="Det")

plt.legend(loc="upper right")
plt.xlabel("Latency per packet (ns)")
plt.ylabel("Count")
plt.savefig('hist2.png')
#plt.show()



plt.hist(list_credit[0], bins=20, label="Adaptive Up", alpha=0.5)
plt.hist(list_credit[1], bins=20, label="Deterministic Up", alpha=0.5)
plt.hist(list_credit_down[0], bins=20, label="Adaptive Down", alpha=0.5)
plt.hist(list_credit_down[1], bins=20, label="Deterministic Down", alpha=0.5)
plt.legend(loc="upper left")
plt.xlabel("Credits Left Port")
plt.ylabel("Count")
plt.savefig('hist.png')
plt.show()
'''