import os

to_plot1 = "python3 performance_complete.py"
to_plot2 = "python3 performance_rate.py"

os_ratio = 1
exp_name = "incast_inter_dc_large"

# Random
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc random -cwnd 2500000 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)

# ECMP
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc ecmp -cwnd 2500000 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)

# Flowlet
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowlet -cwnd 2500000 -flowlet_value 10550000 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)

# Flowcut
to_run = "../sim/datacenter/htsim_ndp_entry_modern -topo ../sim/datacenter/topologies/fat_tree_128.topo -o uec_entry -k 1 -nodes 128 -q 4452000 -strat ecmp_host_random_ecn -linkspeed 50000 -mtu 4096 -seed 15 -hop_latency 1000 -switch_latency 0 -os_border 1 -tm ../sim/datacenter/connection_matrices/perm_128_t.cm -collect_data 1 -topology interdc -max_queue_size 1750000 -interdc_delay 500000 -routing_sc flowcut -cwnd 2500000 -rtt_ratio 3 > out3.tmp && python3 performance_complete.py"
print(to_run)
os.system(to_run)