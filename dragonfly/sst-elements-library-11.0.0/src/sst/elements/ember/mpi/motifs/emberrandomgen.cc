// Copyright 2009-2020 NTESS. Under the terms
// of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Copyright (c) 2009-2020, NTESS
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

#include <sst/core/rng/xorshift.h>
#include "emberrandomgen.h"
#include <sys/stat.h>
#include <unistd.h>
#include <string>
#include <fstream>
#include <time.h>


using namespace SST::Ember;
using namespace SST::RNG;

static inline bool exists(const std::string& name) {
  struct stat buffer;
  return (stat (name.c_str(), &buffer) == 0);
}

EmberRandomTrafficGenerator::EmberRandomTrafficGenerator(SST::ComponentId_t id, Params& params) :
  EmberMessagePassingGenerator(id, params) {
  started = false;
	msgSize = (uint32_t) params.find("arg.messageSize", 1800);
	maxIterations = (uint32_t) params.find("arg.iterations", 1);
        waitToStart = params.find("arg.waitToStart", 0 );
	//std::cout << "Rand Rank " << rank() << " created" << std::endl;
	memSetBacked();
}

bool EmberRandomTrafficGenerator::generate( std::queue<EmberEvent*>& evQ ) {
    enQ_compute(evQ, [&]() {
        if(!waitToStart){
            started = true;
        }else if(exists("/tmp/ember_can_start_" + std::string(getenv("ALLREDUCE_OUT_FOLDER"))) && !started){
             enQ_compute(evQ, [&]() {
                std::cout << "EmberRandomTraffic Rank " << rank() << " entering barrier at " << getCurrentSimTimeNano() <<  std::endl;
                started = true;
                return 0;
            });

            enQ_barrier(evQ, GroupWorld);
            enQ_compute(evQ, [&]() {
                std::cout << "EmberRandomTraffic Rank " << rank() << " started at " << getCurrentSimTimeNano() <<  std::endl;
                started = true;
                return 0;
            });

        }
        if(started){
		srand((unsigned int)time(NULL));

		XORShiftRNG* rng = new XORShiftRNG(rand());

		const uint32_t worldSize = size();
		uint32_t* rankArray = (uint32_t*) malloc(sizeof(uint32_t) * worldSize);

		// Set up initial passing (everyone passes to themselves)
		for(uint32_t i = 0; i < worldSize; i++) {
			rankArray[i] = i;
		}

		for(uint32_t i = 0; i < worldSize; i++) {
			uint32_t swapPartner = rng->generateNextUInt32() % worldSize;
			//printf("%d - %d - Swap partner is %d\n",rank(), i, swapPartner);
			uint32_t oldValue = rankArray[i];
			rankArray[i] = rankArray[swapPartner];
			rankArray[swapPartner] = oldValue;
		}

		void* allocBuffer = memAllocCustomChar( msgSize, 'B' );
		int nextMRIndex = 0;

		MessageRequest* msgRequests = (MessageRequest*) malloc(sizeof(MessageRequest) * 2);

		if(rankArray[rank()] != rank()) {
			enQ_isend( evQ, allocBuffer, msgSize, CHAR, rankArray[rank()],
				0, GroupWorld, &msgRequests[nextMRIndex++]);
		}

		void* recvBuffer = memAlloc( msgSize );

		for(uint32_t i = 0; i < worldSize; i++) {
			if(rank() == rankArray[i] && (i != rank())) {
				enQ_irecv( evQ, recvBuffer, msgSize, CHAR, i, 0,
					GroupWorld, &msgRequests[nextMRIndex++]);
				break;
			}
		}

		enQ_waitall( evQ, nextMRIndex, msgRequests, NULL );

		iteration++;
		delete rng;
        }else{
            enQ_compute(evQ, 0);
        }

        return 0;
    });
    return false;
}