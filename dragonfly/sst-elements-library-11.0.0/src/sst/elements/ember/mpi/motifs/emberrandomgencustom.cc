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

#include <algorithm>
#include <random>

#include <sst_config.h>

#include <sst/core/rng/xorshift.h>
#include "emberrandomgencustom.h"
#include "sst/elements/merlin/interfaces/reorderLinkControl.h"
#include "sst/elements/ember/mpi/motifs/embercommonvariables.h"
#include "sst/elements/merlin/merlin.h"

using namespace SST::Ember;
using namespace SST::RNG;

std::vector<std::unordered_map<int, int>> rank_couple;

std::vector<std::vector<int>> sending_ranks;
std::vector<std::vector<int>> receiving_ranks;


EmberRandomCustomTrafficGenerator::EmberRandomCustomTrafficGenerator(SST::ComponentId_t id, Params& params) :
	EmberMessagePassingGenerator(id, params) {

	msgSize = (uint32_t) params.find("arg.messageSize", 1);
	maxIterations = (uint32_t) params.find("arg.iterations", 1);
	routing_scheme = params.find<std::string>("arg.--routing", "Empty");
	routing_algo = params.find<std::string>("arg.--algorithm", "Empty");
	shape = params.find<std::string>("arg.--shape", "Empty");
	timeout_flow = params.find<uint64_t>("arg.--flowlet_timeout", 0);
	name = "RandomTrafficGenerator";
	iteration = 0;

	memSetBacked();
	allocBuffer = memAllocCustomChar(msgSize, MESSAGE_TO_SEND);
	m_sendBuf_small = memAllocCustomChar(SMALL_MESSAGE_SIZE,MESSAGE_TO_SEND);
    m_recvBuf_small = memAllocCustomChar(SMALL_MESSAGE_SIZE, MESSAGE_TO_SEND);
	recvBuffer = memAllocCustomChar(msgSize, MESSAGE_TO_SEND);

	if (rank() == 0) {
		sending_ranks = std::vector<std::vector<int>>(maxIterations, std::vector<int>(size() / 2, 1));
		receiving_ranks = std::vector<std::vector<int>>(maxIterations, std::vector<int>(size() / 2, 1));

		std::vector<int> list_ranks(size());
  		std::iota(list_ranks.begin(), list_ranks.end(), 0);

		for (int num_iter = 0; num_iter < maxIterations; num_iter++) {
			std::shuffle(std::begin(list_ranks), std::end(list_ranks), std::random_device());
			int half_list = size() / 2;
			for (int num_rank = 0; num_rank < size() / 2; num_rank++) {
				sending_ranks[num_iter][num_rank] = list_ranks[num_rank];
				receiving_ranks[num_iter][num_rank] = list_ranks[num_rank + half_list];
			}
		}	
	}
}

void EmberRandomCustomTrafficGenerator::saveStatistics() {
	auto ooo_relevant_pkts = SST::Merlin::ReorderLinkControl::getNumOutOfOrder();
	auto total_relevant_pkts = SST::Merlin::ReorderLinkControl::getTotPkts();
	auto num_flowlets = SST::Merlin::getTotFlowlets();
	auto num_cached = SST::Merlin::getTotCached();
	auto size_table = SST::Merlin::getSumTables();
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
	double bandwidth = (double) msgSize / (latency * (msgSize / PKT_SIZE));
	double bandwidth_2 = (double) (msgSize * maxIterations) / average_run;
	
	
	printf("\nLocal Value is %ld ns, Sum is %ld ns, Avg is %.2f ns \n\n", local_diff, avg_time, avg_time / (1. * size())); 
	printf("\n\n\nNumber of packets out of order is %d out of %d (%.2f%%)\n", ooo_relevant_pkts, total_relevant_pkts, ((ooo_relevant_pkts / (float)total_relevant_pkts) * 100));
	printf("Number flowlets %d - Number cached %d - Ratio Pkts per Flow %d(%d KB) - Size Table %d - Avg Duration Flow\n", num_flowlets, num_cached, ratio_cached_flowlet, avg_size_flowlet, size_table);
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
	myfile << "number_iterations," + std::to_string(maxIterations) + "\n";
	myfile << "message_size," + std::to_string(msgSize) + "\n";
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
	myfile << "table_size," + std::to_string(size_table) + "\n";
	myfile.close();
}

bool EmberRandomCustomTrafficGenerator::generate( std::queue<EmberEvent*>& evQ ) {
	
	if ( iteration == maxIterations ) {
        if ( 0 == rank()) {
            double totalTime = (double)(m_stopTime - m_startTime)/1000000000.0;

            double latency = ((totalTime/maxIterations)/2);
            double bandwidth = (double) msgSize / latency;

			printf("\nRuntime Random: %.3f\n", totalTime * 1000000.0);

            output("%s: total time %.3f us, loop %d, bufLen %d"
                    ", latency %.3f us. bandwidth %f GB/s\n",
                                getMotifName().c_str(),
                                totalTime * 1000000.0, maxIterations,
                                msgSize,
                                latency * 1000000.0,
                                bandwidth / 1000000000.0 );
        }
        return true;
    }


    if ( 0 == iteration ) {
        verbose(CALL_INFO, 1, 0, "rank=%d size=%d\n", rank(), size());
        if ( 0 == rank() ) {
            enQ_getTime( evQ, &m_startTime );
        }
    }

    const bool participate = ( size() % 2 == 0 ) ? true :
	( rank() == ( size() - 1 ) ) ? false : true;
	
    if( participate ) {
		enQ_compute(evQ, [&, loc_iteration = iteration]() { 
			if(std::find(sending_ranks[loc_iteration].begin(), sending_ranks[loc_iteration].end(), rank()) != sending_ranks[loc_iteration].end()) {
			/* v contains x */
			auto itr=std::find(sending_ranks[loc_iteration].begin(), sending_ranks[loc_iteration].end(), rank());
			auto index=std::distance(sending_ranks[loc_iteration].begin(), itr);
			enQ_send( evQ, allocBuffer, msgSize, CHAR,
                    receiving_ranks[loc_iteration][index], TAG, GroupWorld );
			enQ_recv( evQ, m_recvBuf_small, SMALL_MESSAGE_SIZE, CHAR,
                    receiving_ranks[loc_iteration][index], TAG, GroupWorld, &m_resp );
			if (loc_iteration  == maxIterations - 1)
				enQ_getTime( evQ, &m_stopTime );
			enQ_compute(evQ, [&, it = loc_iteration]() {  
				if (it  == maxIterations - 1) {
					local_diff = m_stopTime - m_startTime;
					//printf("1) Start time is %ld, Stop time is %ld, Difference is %ld, Loc Iteration %d, Glo Iteration %d, It %d, Max %d\n", m_startTime, m_stopTime, local_diff, loc_iteration, iteration, it, maxIterations);
					return 0;
				} else {
					return 0;
				}
            });
			
		} else {
			/* v does not contain x */
			auto itr=std::find(receiving_ranks[loc_iteration].begin(), receiving_ranks[loc_iteration].end(), rank());
			auto index=std::distance(receiving_ranks[loc_iteration].begin(), itr);
			enQ_recv( evQ, recvBuffer, msgSize, CHAR,
                    sending_ranks[loc_iteration][index], TAG, GroupWorld, &m_resp );
			enQ_send( evQ, m_sendBuf_small, SMALL_MESSAGE_SIZE, CHAR,
				sending_ranks[loc_iteration][index], TAG, GroupWorld );
			if (loc_iteration  == maxIterations - 1)
				enQ_getTime( evQ, &m_stopTime );
            enQ_compute(evQ, [&, it = loc_iteration]() {  
				if (it  == maxIterations - 1) {
					local_diff = m_stopTime - m_startTime;
					//printf("2) Start1 time is %ld, Stop time is %ld, Difference is %ld, Loc Iteration %d, Glo Iteration %d, It %d, Max %d\n", m_startTime, m_stopTime, local_diff, loc_iteration, iteration, it, maxIterations);
					return 0;
				} else {
					return 0;
				}
            });
		}
		if ( ++iteration == maxIterations ) {
			enQ_barrier(evQ, GroupWorld);
			if ( 0 == rank()) {
				enQ_getTime( evQ, &m_stopTime );
			}
    	}
			return 0;
		});
    }

    return false;
}