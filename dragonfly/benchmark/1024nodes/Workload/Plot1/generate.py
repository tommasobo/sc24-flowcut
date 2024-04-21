from dis import dis
import random
import csv
from pathlib import Path    

class EntryCSV:
  def __init__(self, sending_to, size,sleep):
    self.sending_to = sending_to
    self.size = size
    self.sleep = sleep

# Variables global
topo_list = ["dragonfly", "notdragonfly"]

custom_sizes = []
ent = "size_flow_enterprise.txt"
web = "size_flow_web_search.txt"
with open(ent) as f:
    for line in f:
        custom_sizes.append(int(line))

max_allowed = 2**22
min_allowed = 2**14

for topo in topo_list:
    num_nodes = 1024
    num_iterations_per_node = 2
    max_node_id = num_nodes - 1
    min_msg = 2**10
    max_msg = 2**20
    ratio_reduce_nodes = 1
    distr = "random"

    path = ""
    if (topo == "dragonfly"):
        num_nodes = 1024
        path = Path("input_dragonfly/")
    else:
        num_nodes = 1024
        path = Path("input_generic/")

    path.mkdir(parents=True, exist_ok=True)

    sending_to_list = [[] for i in range(num_nodes)]
    receiving_from_list = [[] for i in range(num_nodes)]
    nodes_list = list(range(0, num_nodes))

    for idx_action in range(num_iterations_per_node):
        random.shuffle(nodes_list)
        for num_rank in range(int(num_nodes/2)):

            size = random.randint(min_msg,max_msg)
            if (True):
                size = random.choice(custom_sizes)
                if (size > max_allowed):
                    size = max_allowed
                if (size < min_allowed):
                    size = min_allowed
            size = int(size)
            sleep = random.randint(0,0)

            sending_from = nodes_list[num_rank]
            sending_to = nodes_list[num_rank + (int(num_nodes/2))]

            sending_to_list[sending_from].append(EntryCSV(sending_to, size, sleep))
            receiving_from_list[sending_to].append(EntryCSV(sending_from, size, sleep))

            sending_to_list[sending_to].append(EntryCSV(sending_from, size, sleep))
            receiving_from_list[sending_from].append(EntryCSV(sending_to, size, sleep))

    for num_rank_idx in range(num_nodes):
        # Sends
        file_name = str(path) + "/send_" + str(num_rank_idx) + ".csv"
        with open(file_name, mode='w') as employee_file:
            employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for item in sending_to_list[num_rank_idx]:
                temp_list = []
                temp_list.append(str(item.sending_to))
                temp_list.append(str(item.size))
                temp_list.append(str(item.sleep))
                employee_writer.writerow(temp_list)

        # Reads
        file_name = str(path) + "/read_" + str(num_rank_idx) + ".csv"
        with open(file_name, mode='w') as employee_file:
            employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for item in receiving_from_list[num_rank_idx]:
                temp_list = []
                temp_list.append(str(item.sending_to))
                temp_list.append(str(item.size))
                temp_list.append(str(item.sleep))
                employee_writer.writerow(temp_list)
