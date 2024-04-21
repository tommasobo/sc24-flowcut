# Flowcut Switching: High-Performance Adaptive Routing with In-Order Delivery Guarantees
Network latency severely impacts the performance of applications running on supercomputers. Adaptive routing algorithms route packets over different available paths to reduce latency and improve network utilization. However, if a switch routes packets belonging to the same network flow on different paths, they might arrive at the destination out-of-order due to differences in the latency of these paths. For some transport protocols like TCP, QUIC, and RoCE, out-of-order (OOO) packets might cause large performance drops or significantly increase CPU utilization. In this work, we propose flowcut switching, a new adaptive routing algorithm that provides high-performance in-order packet delivery. Differently from existing solutions like flowlet switching, which are based on the assumption of bursty traffic and that might still reorder packets, flowcut switching guarantees in-order delivery under any network conditions, and is effective also for non-bursty traffic, as it is often the case for RDMA.

## General Instructions
This is the entry point for the artifact. The two subfolders provide more details for each corresponding artifact and a more detailed readME.