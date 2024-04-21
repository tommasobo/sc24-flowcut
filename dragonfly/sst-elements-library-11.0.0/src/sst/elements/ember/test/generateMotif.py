import argparse
import random

# set it up
parser = argparse.ArgumentParser(description='Parsing for LoadMotif')
parser.add_argument("--ember", type=str, default="AllPingPongCustomBig", help="Ember Script to Use")
parser.add_argument("--hosts", type=int, default=1, help="Number of Hosts per Router/Switch")
parser.add_argument("--routers", type=int, default=1, help="Number of Routers per Group")
parser.add_argument("--groups", type=int, default=1, help="Number of Groups")
parser.add_argument("--bg", type=int, default=0, help="Backgrounf traffic")
parser.add_argument("--msg_size", type=int, default=1000, help="Msg Size")

# get it
args = parser.parse_args()
job_id = 10

first_list = list()
second_list = list()
third_list = list()
fourth_list = list()
all_ele = list()

num_nodes = args.hosts * args.routers * args.groups
for i in range(0,num_nodes):
    all_ele.append(i)
    rand_num = random.randint(0,args.bg)
    if (rand_num == 0):
        first_list.append(i)
    elif (rand_num == 1):
        fourth_list.append(i)
    elif (rand_num == 2):
        third_list.append(i)
    else:
        second_list.append(i)
        
f = open("generatedLoadMotif", "w")
for i in range(0,args.bg):
    f.write("[JOB_ID] " + str(job_id) + "\n")
    if (args.bg == 1):
        f.write("[NID_LIST] " + ','.join(str(v) for v in first_list) + "\n")
    elif (args.bg == 2):
        f.write("[NID_LIST] " + ','.join(str(v) for v in second_list) + "\n")
    elif (args.bg == 3):
        f.write("[NID_LIST] " + ','.join(str(v) for v in third_list) + "\n")
    f.write("[MOTIF] Init\n")
    f.write("[MOTIF] Random" + " messageSize=" + str(args.msg_size) + " iterations=1\n")
    f.write("[MOTIF] Fini" + "\n\n")
    job_id += 1


f.write("[JOB_ID] " + str(job_id) + "\n")
if (args.bg == 0):
    values = ','.join(str(v) for v in all_ele)
    f.write("[NID_LIST] " + str(values) + "\n")
else:
    f.write("[NID_LIST] " + str(','.join(str(v) for v in fourth_list)) + "\n")
f.write("[MOTIF] Init" + "\n")
f.write("[MOTIF] " + args.ember + " messageSize=" + str(args.msg_size) + " iterations=1" + "\n")
f.write("[MOTIF] Fini" + "\n")
job_id += 1

f.close()
