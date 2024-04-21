// Copyright 2009-2021 NTESS. Under the terms
// of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Copyright (c) 2009-2021, NTESS
// All rights reserved.
//
// Portions are copyright of other developers:
// See the file CONTRIBUTORS.TXT in the top level directory
// the distribution for more information.
//
// This file is part of the SST software package. For license
// information, see the LICENSE file in the top level directory of the
// distribution.


#include <sst_config.h>
#include "emberallreduceresnet.h"

#include "sst/elements/merlin/interfaces/reorderLinkControl.h"
#include "sst/elements/merlin/merlin.h"
#include "sst/elements/ember/mpi/motifs/embercommonvariables.h"

using namespace SST::Ember;


#define NUM 7

//pointers of the send/receive buffers
float* grad_ptrs[NUM];
float* sum_grad_ptrs[NUM];
float* sum_grad_ptrs_1[NUM];


/*
int msgSize[NUM] = {
1001,
2050048,
2048,
2048,
1048576,
512,
512,
2359296,
512,
512,
1048576,
2048,
2048,
1048576,
512,
512,
2359296,
512,
512,
1048576,
2048,
2048,
1048576,
512,
512,
2359296,
512,
512,
524288,
2048,
2048,
2097152,
1024,
1024,
262144,
256,
256,
589824,
256,
256,
262144,
1024,
1024,
262144,
256,
256,
589824,
256,
256,
262144,
1024,
1024,
262144,
256,
256,
589824,
256,
256,
262144,
1024,
1024,
262144,
256,
256,
589824,
256,
256,
262144,
1024,
1024,
262144,
256,
256,
589824,
256,
256,
262144,
1024,
1024,
262144,
256,
256,
589824,
256,
256,
131072,
1024,
1024,
524288,
512,
512,
65536,
128,
128,
147456,
128,
128,
65536,
512,
512,
65536,
128,
128,
128,
65536,
512,
512,
65536,
128,
128,
147456,
128,
128,
65536,
512,
512,
65536,
128,
128,
147456,
128,
128,
32768,
512,
512,
131072,
256,
256,
16384,
64,
64,
36864,
64,
64,
16384,
256,
256,
16384,
64,
64,
36864,
64,
64,
16384,
256,
256,
16384,
64,
64,
36864,
64,
64,
4096,
256,
256,
16384,
64,
64,
9408
};*/
//sizes for the gradients
int msgSize[NUM] = {
1001,
205000,
2048,
2048,
104850,
512,
512,
};
static void test(void* a, void* b, int* len, PayloadDataType* ) {

	printf("%s() len=%d\n",__func__,*len);
}

EmberAllreduceResnetGenerator::EmberAllreduceResnetGenerator(SST::ComponentId_t id,
                                            Params& params) :
	EmberMessagePassingGenerator(id, params, "AllreduceResnet"),
    m_loopIndex(0)
{
	m_iterations = (uint32_t) params.find("arg.iterations", 1);
	m_compute    = (uint32_t) params.find("arg.compute", 0);
	m_count      = (uint32_t) params.find("arg.count", 1);
	if ( params.find<bool>("arg.doUserFunc", false )  )   {
		m_op = op_create( test, 0 );
	} else {
		m_op = Hermes::MP::SUM;
	}

	printf("ResNet!\n");
    routing_scheme = params.find<std::string>("arg.--routing", "Empty");
	routing_algo = params.find<std::string>("arg.--algorithm", "Empty");
	shape = params.find<std::string>("arg.--shape", "Empty");
	timeout_flow = params.find<uint64_t>("arg.--flowlet_timeout", 0);
	job_id = params.find<uint64_t>("arg.--job_id", 0);
	name = "Resnet";
}

void EmberAllreduceResnetGenerator::saveStatistics() {
	auto ooo_relevant_pkts = SST::Merlin::ReorderLinkControl::getNumOutOfOrder();
	auto total_relevant_pkts = SST::Merlin::ReorderLinkControl::getTotPkts();
	auto num_flowlets = SST::Merlin::getTotFlowlets();
	auto num_cached = SST::Merlin::getTotCached();
	auto ratio_cached_flowlet = 0;
	auto avg_size_flowlet = 0;
	if (num_flowlets !=0) {
		ratio_cached_flowlet = num_cached / num_flowlets;
		avg_size_flowlet = ((num_cached / num_flowlets) * PKT_SIZE) / 1000;
	}
	auto ooo_bg_pkts = SST::Merlin::ReorderLinkControl::getTotNumOutOfOrder();
	auto total_bg_pkts = SST::Merlin::ReorderLinkControl::allPkts();		
	double average_run = m_stopTime - m_startTime;
	double latency = (average_run/(total_relevant_pkts / size()));
	double lat = (double)(avg_time / 2) / total_relevant_pkts;
	
    
    //double bandwidth = (double) msgSize / (latency * (msgSize / PKT_SIZE));
	//double bandwidth_2 = (double) (msgSize * m_iterations) / average_run;

    double bandwidth_2 = 0;
    double bandwidth = 0;
	
	//printf("\nLocal Value is %ld ns, Sum is %ld ns, Avg is %.2f ns \n\n", local_diff, avg_time, avg_time / (1. * size())); 
	printf("\n\n\nNumber of packets out of order is %d out of %d (%.2f%%)\n", ooo_relevant_pkts, total_relevant_pkts, ((ooo_relevant_pkts / (float)total_relevant_pkts) * 100));
	printf("Number flowlets %d - Number cached %d - Ratio Pkts per Flow %d(%d KB) - Size Table - Avg Duration Flow\n", num_flowlets, num_cached, ratio_cached_flowlet, avg_size_flowlet);
	printf("Number of Control or Unrelated Packets %d (OOO %.2f%%) \n\n", total_bg_pkts, ((ooo_bg_pkts / (float)total_bg_pkts) * 100));
	printf("Avg Time Completion %.2f ns, Latency %.2f ns or %.2f ns, BandWidth %.2f GB/s or %.2f GB/s\n\n\n", average_run, latency, lat,  bandwidth, bandwidth_2);

	std::ofstream myfile;
	auto t = std::time(nullptr);
	auto tm = *std::localtime(&t);
	std::ostringstream oss;
	oss << std::put_time(&tm, "%d-%m-%Y-%H-%M-%S");
	auto current_time = oss.str();
	myfile.open (std::string(PATH_INPUT_FROM_EMBER) + std::string("/" + name + routing_scheme + routing_algo + "|" + current_time + std::to_string(job_id) +".csv"));
	myfile << "program_run_name," + name + "\n";
	myfile << "shape," + shape + "\n";
	myfile << "routing_scheme," + routing_scheme + "\n";
	myfile << "routing_algo," + routing_algo + "\n";
	myfile << "flowlet_timeout," + std::to_string(timeout_flow) + "\n";
	myfile << "run_time_ns," + std::to_string(average_run) + "\n";
	myfile << "number_ranks," + std::to_string(size()) + "\n";
	myfile << "number_iterations," + std::to_string(m_iterations) + "\n";
	myfile << "message_size," + std::to_string(0) + "\n";
	myfile << "packets_size," + std::to_string(PKT_SIZE) + "\n";
	myfile << "ooo_relevant_pkts," + std::to_string(ooo_relevant_pkts) + "\n";
	myfile << "total_relevant_pkts," + std::to_string(total_relevant_pkts) + "\n";
	myfile << "num_flowlet," + std::to_string(num_flowlets) + "\n";
	myfile << "num_cached," + std::to_string(num_cached) + "\n";
	myfile << "ratio_cached_flowlet," + std::to_string(ratio_cached_flowlet) + "\n";
	myfile << "avg_size_flowlet," + std::to_string(avg_size_flowlet) + "\n";
	myfile << "ooo_bg_pkts," + std::to_string(ooo_bg_pkts) + "\n";
	myfile << "total_bg_pkts," + std::to_string(total_bg_pkts) + "\n";
	myfile << "latency," + std::to_string(latency) + "\n";
	myfile << "bandwidth_2," + std::to_string(bandwidth_2) + "\n";
	myfile.close();
}

bool EmberAllreduceResnetGenerator::generate( std::queue<EmberEvent*>& evQ) {

    if ( m_loopIndex == m_iterations ) {
        if ( 0 == rank() ) {
			double totalTime = (double)(m_stopTime - m_startTime)/1000000000.0;
            double latency = (double)(m_stopTime-m_startTime)/(double)m_iterations;
            latency /= 1000000000.0;
            output( "%s: ranks %d, loop %d, %d double(s), latency %.3f us\n",
                    getMotifName().c_str(), size(), m_iterations, m_count, latency * 1000000.0  );
			printf("\nRuntime: %.3f\n", totalTime * 1000000.0);
        }
        return true;
    }

    for(int i=0; i<NUM; i++){
        grad_ptrs[i] = (float *)calloc(msgSize[i] / 5, sizeof(float));
        sum_grad_ptrs[i] = (float *)calloc(msgSize[i] / 5, sizeof(float));
        memset(grad_ptrs[i], MESSAGE_TO_SEND, msgSize[i] / 5);
    }


    // Main Body
    for(int i=0; i<NUM; i++){
        assert(grad_ptrs[i]!=NULL && sum_grad_ptrs[i]!=NULL);
    }

	if ( 0 == m_loopIndex ) {
		memSetBacked();
		if (rank() == 0) {
			enQ_getTime( evQ, &m_startTime );
		}
        
    }
    
    for (int i=0; i<10; i++)
    {
        for(int j=0; j<NUM; j++){
            enQ_allreduce( evQ, grad_ptrs[j], sum_grad_ptrs[j], msgSize[j] / 5, FLOAT, SUM, GroupWorld);
        }

        //enQ_barrier(evQ, GroupWorld);
    }
    
    if ( ++m_loopIndex == m_iterations ) {
		enQ_barrier(evQ, GroupWorld);
		if (rank() == 0) {
			enQ_getTime( evQ, &m_stopTime );
		}

        /*if (rank() == 0){
            enQ_compute(evQ, [&]() { 
                //saveStatistics();
                local_diff = m_stopTime - m_startTime;
                printf("\nLocal Value is %ld, Sum is %ld, Avg is %.2f", local_diff, avg_time, avg_time / (1. * size())); 
                auto a = SST::Merlin::ReorderLinkControl::getNumOutOfOrder();
                auto b = SST::Merlin::ReorderLinkControl::getTotPkts();
                auto num_flowlets = SST::Merlin::getTotFlowlets();
                auto num_cached = SST::Merlin::getTotCached();
                printf("\n\n\nNumber of packets out of order is %d out of %d (%.2f%%)\n", a, b, ((a / (float)b) * 100));
                printf("Number flowlets %d - Number cached %d - Ratio Pkts per Flow %d - Size Table - Avg Duration Flow\n", num_flowlets, num_cached, num_cached / num_flowlets);
                auto c = SST::Merlin::ReorderLinkControl::getTotNumOutOfOrder();
                printf("Number of Control or Unrelated Packets %d (OOO %.2f%%) \n\n", SST::Merlin::ReorderLinkControl::allPkts(), ((c / (float)SST::Merlin::ReorderLinkControl::allPkts()) * 100));
                double average_run = (double)local_diff;
                double latency = average_run/((SST::Merlin::ReorderLinkControl::allPkts() + b) / size());
                double bandwidth = (double)(1250) / latency;
                printf("Avg Time Completion %.2f, Latency %.2f, BandWidth %.2f\n\n\n", average_run, latency, bandwidth);*/
                /*return 0;
            });
        }*/
    }
    return false;
}
