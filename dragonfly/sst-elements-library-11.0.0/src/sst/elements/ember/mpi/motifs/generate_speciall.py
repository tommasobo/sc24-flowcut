from dis import dis
from math import dist
import random
import csv
from pathlib import Path
from tracemalloc import start    
import numpy

class EntryCSV:
  def __init__(self, sending_to, size,sleep):
    self.sending_to = sending_to
    self.size = size
    self.sleep = sleep

# Variables global
num_nodes = 64
host_per_switch = 8
tot_switch = 8
num_iterations_per_node = 1
max_node_id = num_nodes - 5
min_msg = 3950000
max_msg = 3950000
distr = "random"
ratio_reduce_nodes = 1

path = Path("input/")
path.mkdir(parents=True, exist_ok=True)

all_list = list(range(int(num_nodes)))
first_half = list(range(int(num_nodes / 2)))
second_half = list(range(int(num_nodes / 2)))
start_switch = []
end_switch = []

for idx in range(tot_switch):
    if (len(start_switch) == 0):
        start_switch.append(0)
    else:
        start_switch.append(start_switch[idx-1] + host_per_switch)
    if (len(end_switch) == 0):
        end_switch.append(host_per_switch-1)
    else:
        end_switch.append(end_switch[idx-1] + host_per_switch)

print(start_switch)
print(end_switch)
print(all_list)

def process_csv_points(file_name):
    input_folder = "input"
    idx = 0
    with open(Path(input_folder, file_name)) as fp:
        Lines = fp.readlines()
        x_points = []
        y_points = []
        for line in Lines:
            splitted_line = line.split(",")
            #print("X {} - Y {}".format(float(splitted_line[0]), float(splitted_line[1])))
            #if (idx % 7 == 0):
            x_points.append(float(splitted_line[0]))
            y_points.append(float(splitted_line[1]))
            idx += 1 

        return x_points, y_points

sending_to_list = [[] for i in range(num_nodes)]
receiving_from_list = [[] for i in range(num_nodes)]

#Process Distributions
web_search_file = "web_search_cdf.csv"
data_mining_file = "data_mining_cdf.csv"
enterprise_file = "enterprise_cdf.csv"

points = []

'''points.append(process_csv_points(web_search_file))
points.append(process_csv_points(data_mining_file))
points.append(process_csv_points(enterprise_file))'''



for idx_action in range(num_iterations_per_node):
    all_list = list(range(int(num_nodes)))
    for num_rank in range(num_nodes):
        # Get Random Size, set lower bound
        random_parter = random.choice(all_list)
        start_id = 0
        stop_id = 0
        for i in range(len(start_switch)):
            if (num_rank >= start_switch[i] and num_rank <= end_switch[i]):
                start_id = start_switch[i]
                stop_id = end_switch[i]

        count = 0
        found = True
        while (random_parter >= start_id and random_parter <= stop_id and num_rank == random_parter):
            random_parter = random.choice(all_list)
            count += 1
            if (count > 5000): # Terrible hack to check if there are no more possible combinations available
                found = False
                break

        if found:
            size = random.randint(min_msg,max_msg)
            sleep = 0
            sending_to_list[num_rank].append(EntryCSV(random_parter, size, sleep))
            receiving_from_list[random_parter].append(EntryCSV(num_rank, size, sleep))

            all_list.remove(random_parter)

for num_rank_idx in range(num_nodes):
    # Sends
    file_name = "input/send_" + str(num_rank_idx) + ".csv"
    with open(file_name, mode='w') as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for item in sending_to_list[num_rank_idx]:
            temp_list = []
            temp_list.append(str(item.sending_to))
            temp_list.append(str(item.size))
            temp_list.append(str(item.sleep))
            employee_writer.writerow(temp_list)

    # Reads
    file_name = "input/read_" + str(num_rank_idx) + ".csv"
    with open(file_name, mode='w') as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for item in receiving_from_list[num_rank_idx]:
            temp_list = []
            temp_list.append(str(item.sending_to))
            temp_list.append(str(item.size))
            temp_list.append(str(item.sleep))
            employee_writer.writerow(temp_list)