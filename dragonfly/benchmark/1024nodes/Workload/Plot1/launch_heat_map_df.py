
from time import sleep, time
import subprocess
import string
import os

#alpha_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
alpha_values = [0.1, 0.3, 0.7]
ratio_valus = [1,5,10,15,30,45, 60]



alphabet = list(string.ascii_lowercase[0:len(ratio_valus)])
print(alphabet)
os.makedirs("output/dragonfly_flowcut_mpr/", exist_ok=True) 
os.makedirs("output/dragonfly_flowlet/", exist_ok=True) 


flowlet = True
if (flowlet):
    timeout_values = [1,1000,2500,5000,10000,25000,75000, 300000, 450000]
    for timeout in timeout_values:
        launch_string = 'SST_NO_MEM=1 time sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --flowlet_timeout={} --routing=flowlet --algorithm=ugal --flowcut_mode=2 --exponential_alpha=0.7 --flowcut_max_ratio=6 --flowcut_value=10000 --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > output/dragonfly_flowlet/flowlet_{}'.format(timeout, str(timeout))
        print(launch_string)
        sleep(2)
        process = subprocess.Popen([launch_string], shell=True)
        process.wait()
    exit(1)


for alpha in alpha_values:
    i = 0
    for ratio in ratio_valus:
        launch_string = 'SST_NO_MEM=1 time sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --routing=slingshot --algorithm=ugal --flowcut_mode=2 --exponential_alpha={} --flowcut_max_ratio={} --flowcut_value=10000 --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > output/dragonfly_flowcut_mpr/{}'.format(alpha, ratio, str(alpha) + "_" + str(alphabet[i]) + "_" + str(ratio))
        print(launch_string)
        sleep(2)
        process = subprocess.Popen([launch_string], shell=True)
        process.wait()
        i += 1

# Launch ECMP
launch_string = 'SST_NO_MEM=1 time sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --routing=default --algorithm=minimal --flowcut_mode=2 --exponential_alpha={} --flowcut_max_ratio={} --flowcut_value=10000 --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > output/dragonfly_flowcut_mpr/{}'.format(1, 1, "ecmp")
print(launch_string)
sleep(2)
process = subprocess.Popen([launch_string], shell=True)
process.wait()
# Launch UGAL
launch_string = 'SST_NO_MEM=1 time sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --routing=default --algorithm=ugal --flowcut_mode=2 --exponential_alpha={} --flowcut_max_ratio={} --flowcut_value=10000 --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > output/dragonfly_flowcut_mpr/{}'.format(1, 1, "ugal")
print(launch_string)
sleep(2)
process = subprocess.Popen([launch_string], shell=True)
process.wait()
# Launch Valiant
launch_string = 'SST_NO_MEM=1 time sst --num_threads=8 --model-options="--param="nic:module=merlin.reorderlinkcontrol" --topo=dragonfly --routing=default --algorithm=valiant --flowcut_mode=2 --exponential_alpha={} --flowcut_max_ratio={} --flowcut_value=10000 --shape=16:16:16:4 --ackMode=true --loadFile=loads/Scatter" ../../../sst-elements-library-11.0.0/src/sst/elements/ember/test/emberLoad.py > output/dragonfly_flowcut_mpr/{}'.format(1, 1, "valiant")
print(launch_string)
sleep(2)
process = subprocess.Popen([launch_string], shell=True)
process.wait()