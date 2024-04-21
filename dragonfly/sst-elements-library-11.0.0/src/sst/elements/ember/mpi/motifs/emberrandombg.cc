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
#include "emberrandombg.h"
#include "sst/elements/merlin/interfaces/reorderLinkControl.h"
#include "sst/elements/ember/mpi/motifs/embercommonvariables.h"
#include "sst/elements/merlin/merlin.h"

using namespace SST::Ember;
using namespace SST::RNG;


std::vector<std::vector<int>> sending_ranks_bg;
std::vector<std::vector<int>> receiving_ranks_bg;


EmberRandomBgTrafficGenerator::EmberRandomBgTrafficGenerator(SST::ComponentId_t id, Params& params) :
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
	allocBuffer = memAllocCustomChar(msgSize, OTHER_MESSAGE);
	m_sendBuf_small = memAllocCustomChar(SMALL_MESSAGE_SIZE,OTHER_MESSAGE);
    m_recvBuf_small = memAllocCustomChar(SMALL_MESSAGE_SIZE, OTHER_MESSAGE);
	recvBuffer = memAllocCustomChar(msgSize, OTHER_MESSAGE);
}

bool EmberRandomBgTrafficGenerator::generate( std::queue<EmberEvent*>& evQ ) {
	
    enQ_compute(evQ, [&, loc_iteration = iteration]() { 
        if (rank() == 0) {
            sending_ranks_bg = std::vector<std::vector<int>>(maxIterations, std::vector<int>(size() / 2, 1));
            receiving_ranks_bg = std::vector<std::vector<int>>(maxIterations, std::vector<int>(size() / 2, 1));

            std::vector<int> list_ranks(size());
            std::iota(list_ranks.begin(), list_ranks.end(), 0);

            for (int num_iter = 0; num_iter < maxIterations; num_iter++) {
                std::shuffle(std::begin(list_ranks), std::end(list_ranks), std::random_device());
                int half_list = size() / 2;
                for (int num_rank = 0; num_rank < size() / 2; num_rank++) {
                    sending_ranks_bg[num_iter][num_rank] = list_ranks[num_rank];
                    receiving_ranks_bg[num_iter][num_rank] = list_ranks[num_rank + half_list];
                }
            }	
        }
        return 0;
    });

    enQ_barrier(evQ, GroupWorld);

    bool participate = ( size() % 2 == 0 ) ? true :
	( rank() == ( size() - 1 ) ) ? false : true;
	
    if( participate ) {
		enQ_compute(evQ, [&, loc_iteration = iteration]() { 
			if(std::find(sending_ranks_bg[loc_iteration].begin(), sending_ranks_bg[loc_iteration].end(), rank()) != sending_ranks_bg[loc_iteration].end()) {
			/* v contains x */
			auto itr=std::find(sending_ranks_bg[loc_iteration].begin(), sending_ranks_bg[loc_iteration].end(), rank());
			auto index=std::distance(sending_ranks_bg[loc_iteration].begin(), itr);
			enQ_send( evQ, allocBuffer, msgSize, CHAR,
                    receiving_ranks_bg[loc_iteration][index], TAG, GroupWorld );
			enQ_recv( evQ, m_recvBuf_small, SMALL_MESSAGE_SIZE, CHAR,
                    receiving_ranks_bg[loc_iteration][index], TAG, GroupWorld, &m_resp );			
		} else {
			/* v does not contain x */
			auto itr=std::find(receiving_ranks_bg[loc_iteration].begin(), receiving_ranks_bg[loc_iteration].end(), rank());
			auto index=std::distance(receiving_ranks_bg[loc_iteration].begin(), itr);
			enQ_recv( evQ, recvBuffer, msgSize, CHAR,
                    sending_ranks_bg[loc_iteration][index], TAG, GroupWorld, &m_resp );
			enQ_send( evQ, m_sendBuf_small, SMALL_MESSAGE_SIZE, CHAR,
				sending_ranks_bg[loc_iteration][index], TAG, GroupWorld );
		}
			return 0;
		});
    }

    return false;
}