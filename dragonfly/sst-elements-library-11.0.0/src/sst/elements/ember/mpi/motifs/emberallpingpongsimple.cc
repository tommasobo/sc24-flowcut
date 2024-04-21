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
#include "emberallpingpongsimple.h"
#include "sst/elements/merlin/interfaces/reorderLinkControl.h"
#include "sst/elements/merlin/merlin.h"
#include "sst/elements/ember/mpi/motifs/embercommonvariables.h"

//#include "sst/elements/merlin/topology/dragonfly.h"


using namespace SST::Ember;

// Number of Nodes * Iterations

EmberAllPingPongSimpleGenerator::EmberAllPingPongSimpleGenerator(SST::ComponentId_t id,
                                            Params& params) :
	EmberMessagePassingGenerator(id, params, "AllPingPongSimple"),
    m_loopIndex(0)
{
	m_iterations = (uint32_t) params.find("arg.iterations", 1);
	m_messageSize = (uint32_t) params.find("arg.messageSize", 1200);
	m_computeTime = (uint32_t) params.find("arg.computetime", 100);
    routing_scheme = params.find<std::string>("arg.--routing", "Empty");
	routing_algo = params.find<std::string>("arg.--algorithm", "Empty");
	shape = params.find<std::string>("arg.--shape", "Empty");
	timeout_flow = params.find<uint64_t>("arg.--flowlet_timeout", 0);

    memSetBacked();	
    m_sendBuf = memAllocCustomChar(m_messageSize, 'A');
    //m_sendBuf = memAlloc(m_messageSize);
    m_recvBuf = memAlloc(m_messageSize);
    m_sendBuf_small = memAllocCustomChar(8, 'A');
    m_recvBuf_small = memAlloc(8);
    name = "AllPingPong";

    // Get Number of nodes
    size_sending = SST::Ember::EmberMessagePassingGenerator::size();

}

void EmberAllPingPongSimpleGenerator::saveStatistics() {
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
	double average_run = (double)avg_time / (1. * (size() / 1));
	double latency = (average_run/(total_relevant_pkts / (size() / 2)));
	double lat = (double)(avg_time / 2) / total_relevant_pkts;
	double bandwidth = (double) m_messageSize / (latency * (m_messageSize / PKT_SIZE));
	double bandwidth_2 = (double) (m_messageSize * m_iterations) / average_run;
	
	printf("\nLocal Value is %ld ns, Sum is %ld ns, Avg is %.2f ns \n\n", local_diff, avg_time, avg_time / (1. * size())); 
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
	myfile.open (std::string(PATH_INPUT_FROM_EMBER) + std::string("/" + name + routing_scheme + routing_algo + "|" + current_time + ".csv"));
	myfile << "program_run_name," + name + "\n";
	myfile << "shape," + shape + "\n";
	myfile << "routing_scheme," + routing_scheme + "\n";
	myfile << "routing_algo," + routing_algo + "\n";
	myfile << "flowlet_timeout," + std::to_string(timeout_flow) + "\n";
	myfile << "run_time_ns," + std::to_string(avg_time / (1. * size())) + "\n";
	myfile << "number_ranks," + std::to_string(size()) + "\n";
	myfile << "number_iterations," + std::to_string(m_iterations) + "\n";
	myfile << "message_size," + std::to_string(m_messageSize) + "\n";
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

bool EmberAllPingPongSimpleGenerator::generate( std::queue<EmberEvent*>& evQ)
{
    int numNodes = 16 * 16;
    if ( m_loopIndex == m_iterations ) {
        if ( 0 == rank()) {
            double totalTime = (double)(m_stopTime - m_startTime)/1000000000.0;

            double latency = ((totalTime/m_iterations));
            double bandwidth = (double) (m_messageSize) / latency;

            printf("\nRuntime: %.3f\n", totalTime * 1000000.0);

            output("%s: total time %.3f us, losop %d, bufLen %d"
                    ", latency %.3f us. bandwidth %f GB/s\n",
                                getMotifName().c_str(),
                                totalTime * 1000000.0, m_iterations,
                                m_messageSize,
                                latency * 1000000.0,
                                bandwidth / 1000000000.0 );
        }
        return true;
    }

    if ( 0 == m_loopIndex ) {
        verbose(CALL_INFO, 1, 0, "rank=%d size=%d\n", rank(), size());
        if ( 0 == rank() ) {
            enQ_getTime( evQ, &m_startTime );
        }
    }

    const bool participate = ( size() % 2 == 0 ) ? true :
	( rank() == ( size() - 1 ) ) ? false : true;

	int next_index = 0;
    if(participate) {            
        if ( rank() < numNodes) {
            enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                   size() - (numNodes - rank()), TAG, GroupWorld, &m_req);
            enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + numNodes) % size(), TAG, GroupWorld );
			enQ_wait(evQ, &m_req);
        } else {
            enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,  (rank() - numNodes) % size(), TAG,
					GroupWorld, &m_req);
            enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + numNodes) % size(), TAG, GroupWorld );
			enQ_wait(evQ, &m_req);
        }
    }

	/*
	if(participate) {            
        if ( rank() < numNodes) {
            enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                   size() - (numNodes - rank()), TAG, GroupWorld, NULL );
            enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + numNodes) % size(), TAG, GroupWorld );
        } else if (rank() >= SST::Ember::EmberMessagePassingGenerator::size() - numNodes) {
            enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + numNodes) % size(), TAG, GroupWorld );
            enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,  (rank() - numNodes) % size(), TAG,
					GroupWorld, NULL);
        } else {
            enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,  (rank() - numNodes) % size(), TAG,
					GroupWorld, NULL);
            enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + numNodes) % size(), TAG, GroupWorld );
        }
    }
	*/

    if ( ++m_loopIndex == m_iterations ) {
        enQ_barrier(evQ, GroupWorld);
        if ( 0 == rank() ) {
            enQ_getTime( evQ, &m_stopTime );
        }
    }
    return false;
}