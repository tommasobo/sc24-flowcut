# Flowcut Switching: High-Performance Adaptive Routing with In-Order Delivery Guarantees
Network latency severely impacts the performance of applications running on supercomputers. Adaptive routing algorithms route packets over different available paths to reduce latency and improve network utilization. However, if a switch routes packets belonging to the same network flow on different paths, they might arrive at the destination out-of-order due to differences in the latency of these paths. For some transport protocols like TCP, QUIC, and RoCE, out-of-order (OOO) packets might cause large performance drops or significantly increase CPU utilization. In this work, we propose flowcut switching, a new adaptive routing algorithm that provides high-performance in-order packet delivery. Differently from existing solutions like flowlet switching, which are based on the assumption of bursty traffic and that might still reorder packets, flowcut switching guarantees in-order delivery under any network conditions, and is effective also for non-bursty traffic, as it is often the case for RDMA.

## Installation from Source Code
The installation from source code should take about 15 minutes on a modern machine.

### Requirements
C++11, python3, python-dev and OpenMPI 4.0.5 are necessary when installing the project from source code as these are the minimum requirements for SST to run.
In particular, in our case, we run our code locally with the following compilers and software:
* gcc (Ubuntu 9.3.0-10ubuntu2) 9.3.0
* Open MPI 4.0.5
* Python 3.8.10

### Installation
Once, the download has been finished, extract the archive and go inside the extracted folder. Once that has been done, it is possible to start installing SST.

To install SST 11.1.0 and OpenMPI 4.0.5 we refer to the official instructions from the [SST website.](http://sst-simulator.org/SSTPages/SSTBuildAndInstall_11dot1dot0_SeriesDetailedBuildInstructions/#openmpi-405-strongly-recommended) Note that the source files for SST are already part of this repository and it is important to use them as they contains all our modifications compared to the original SST repository (keep this in mind also when setting the location of `SST_CORE_ROOT` and `SST_ELEMENTS_ROOT`)
One common issue could be the `make all` of SST Core or SST Elements failing. In that case please try to run `automake` first.
Once the installation has been done, it is possible to test its correctness by running:
```bash
sst-test-core
sst-test-elements -w "*simple*"
```

Finally it is necessary to add this environmental variable to your `~/.bashrc` file or equivalent for the correct execution of the scripts.
```
export PYTHONPATH="${PYTHONPATH}:$SST_ELEMENTS_ROOT/src/sst/elements/ember/test/"
```

## Usage relevant for the artifact

We provide Python scripts in the ```benchmark/1024nodes/Workload``` folder to run the various experiments.
