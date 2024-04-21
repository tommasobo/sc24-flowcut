# Flowcut Switching: High-Performance Adaptive Routing with In-Order Delivery Guarantees
Network latency severely impacts the performance of applications running on supercomputers. Adaptive routing algorithms route packets over different available paths to reduce latency and improve network utilization. However, if a switch routes packets belonging to the same network flow on different paths, they might arrive at the destination out-of-order due to differences in the latency of these paths. For some transport protocols like TCP, QUIC, and RoCE, out-of-order (OOO) packets might cause large performance drops or significantly increase CPU utilization. In this work, we propose flowcut switching, a new adaptive routing algorithm that provides high-performance in-order packet delivery. Differently from existing solutions like flowlet switching, which are based on the assumption of bursty traffic and that might still reorder packets, flowcut switching guarantees in-order delivery under any network conditions, and is effective also for non-bursty traffic, as it is often the case for RDMA.

# htsim Network Simulator

htsim is a high performance discrete event simulator, inspired by ns2, but much faster, primarily intended to examine congestion control algorithm behaviour.  It was originally written by [Mark Handley](http://www0.cs.ucl.ac.uk/staff/M.Handley/) to allow [Damon Wishik](https://www.cl.cam.ac.uk/~djw1005/) to examine TCP stability issues when large numbers of flows are multiplexed.  It was extended by [Costin Raiciu](http://nets.cs.pub.ro/~costin/) to examine [Multipath TCP performance](http://nets.cs.pub.ro/~costin/files/mptcp-nsdi.pdf) during the MPTCP standardization process, and models of datacentre networks were added to [examine multipath transport](http://nets.cs.pub.ro/~costin/files/mptcp_dc_sigcomm.pdf) in a variety of datacentre topologies.  [NDP](http://nets.cs.pub.ro/~costin/files/ndp.pdf) was developed using htsim, and simple models of DCTCP, DCQCN were added for comparison.  Later htsim was adopted by Correct Networks (now part of Broadcom) to develop [EQDS](http://nets.cs.pub.ro/~costin/files/eqds.pdf), and switch models were improved to allow a variety of forwarding methods.  Support for a simple RoCE model, PFC, Swift and HPCC were added.

## The basics

There are some limited instructions in the [wiki](https://github.com/Broadcom/csg-htsim/wiki).  

htsim is written in C++, and has no dependencies.  It should compile and run with g++ or clang on MacOS or Linux.  To compile htsim, cd into the sim directory and run make.

To get started with running experiments, take a look in the experiments directory where there are some examples.  These examples generally require bash, python3 and gnuplot.

## Getting started with htsim

Compile with the following instruction. To do so, we recommend running the following command line from the ```/sim``` directory (feel free to change the number of jobs being run in parallel).

```
make clean && cd datacenter/ && make clean && cd .. && make -j 8 && cd datacenter/ && make -j 8 && cd ..
```

It is then possible to run htsim by using three possible methods:
- Using connection matrixes. Details [here](https://github.com/Broadcom/csg-htsim/wiki).
- Using C++ code to setup the simulation directly.
- Using LGS. See the following paragraphs for details.

## Usage relevant for the artifact

We provide Python scripts in the ```plotting/``` folder to run the various experiments.
