from random import randrange

num_resnet_proxy = 1
size_ranks = 1024
size_resnet = 24

ranks = list(range(0, size_ranks))
resnet_ranks = list()


finished = False
for i in range (0, num_resnet_proxy):
    resnet_ranks.append(list())
    finished = False
    while finished == False:
        rand_index = randrange(len(ranks))
        if (len(resnet_ranks[i]) < size_resnet):
            resnet_ranks[i].append(ranks[rand_index])
            del ranks[rand_index]
        else:
            finished = True

for i in range (0, num_resnet_proxy):
    print(resnet_ranks[i])
    print()

print(ranks)


