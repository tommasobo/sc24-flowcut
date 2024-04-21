import enum
import random

num_nodes =  64


first_list = list()
'''second_list = list()
third_list = list()
all_ele = list()

for i in range(0,num_nodes):
    all_ele.append(i)
    rand_num = random.randint(0,1)
    if (rand_num == 0):
        first_list.append(i)
    elif (rand_num == 1):
        second_list.append(i)

        
print(*all_ele, sep=',')
print()
print(*first_list, sep=',')
print()
print(*second_list, sep=',')
print()
'''

list_nodes = list(range(64))
print(list_nodes)
#first_half = list_nodes[::2]
#second_half = list_nodes[1::2]
first_half = []
second_half = []

for idx, item in enumerate(list_nodes):
    if (idx % 4 == 0):
        first_half.append(item)
    else:
        second_half.append(item)

print(first_half)
print(second_half)