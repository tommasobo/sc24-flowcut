from dis import dis
from math import dist
import random
import csv
from pathlib import Path    
import numpy

class EntryCSV:
  def __init__(self, sending_to, size,sleep):
    self.sending_to = sending_to
    self.size = size
    self.sleep = sleep

# Variables global
num_nodes = 1024
num_iterations_per_node = 15
max_node_id = num_nodes - 1
min_msg = 50400
max_msg = 580602
ratio_reduce_nodes = 1
distr = "random"

path = Path("input/")
path.mkdir(parents=True, exist_ok=True)


first_half = list(range(512))
second_half = list(range(512))

for it, idx in enumerate(second_half):
    second_half[idx] = second_half[idx] + 512

print(second_half)
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
    random.shuffle(second_half)
    for num_rank in range(num_nodes):
        random_parter = random.randint(0,max_node_id)
        # Get Random Size, set lower bound
        if (num_rank < 512):
            random_parter = second_half[num_rank]
            size = random.randint(min_msg,max_msg)
            sleep = 0
            sending_to_list[num_rank].append(EntryCSV(random_parter, size, sleep))
            receiving_from_list[random_parter].append(EntryCSV(num_rank, size, sleep))

            sending_to_list[random_parter].append(EntryCSV(num_rank, size, sleep))
            receiving_from_list[num_rank].append(EntryCSV(random_parter, size, sleep))

        '''else:
            random_parter = first_half[num_rank-512]
            size = random.randint(min_msg,max_msg)
            sleep = 0
            sending_to_list[num_rank].append(EntryCSV(random_parter, size, sleep))
            receiving_from_list[random_parter].append(EntryCSV(num_rank, size, sleep))'''


'''random.shuffle(second_half)
random.shuffle(first_half)

for num_rank in range(num_nodes):
    if (num_rank % ratio_reduce_nodes == 0):
        for idx_action in range(num_iterations_per_node):

            random_parter = random.randint(0,max_node_id)
            # Get Random Size, set lower bound

            if (num_rank < 512):
                random_parter = second_half[num_rank]
                size = random.randint(min_msg,max_msg)
                sleep = 0
                sending_to_list[num_rank].append(EntryCSV(random_parter, size, sleep))
                receiving_from_list[random_parter].append(EntryCSV(num_rank, size, sleep))

            else:
                random_parter = first_half[num_rank-512]
                size = random.randint(min_msg,max_msg)
                sleep = 0
                sending_to_list[num_rank].append(EntryCSV(random_parter, size, sleep))
                receiving_from_list[random_parter].append(EntryCSV(num_rank, size, sleep))
            
            if (num_rank < 512):
                random_parter = num_rank + num_nodes - 512
                size = random.randint(min_msg,max_msg)
                sleep = 0
                sending_to_list[num_rank].append(EntryCSV(random_parter, size, sleep))
                receiving_from_list[random_parter].append(EntryCSV(num_rank, size, sleep))

            elif (num_rank >= 512):
                random_parter = num_rank - num_nodes + 512
                size = random.randint(min_msg,max_msg)
                sleep = 0
                sending_to_list[num_rank].append(EntryCSV(random_parter, size, sleep))
                receiving_from_list[random_parter].append(EntryCSV(num_rank, size, sleep))'''

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