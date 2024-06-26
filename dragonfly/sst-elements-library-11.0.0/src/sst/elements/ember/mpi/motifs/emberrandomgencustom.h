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


#ifndef _H_EMBER_RANDOMCustom_GEN
#define _H_EMBER_RANDOMCUSTOM_GEN

#include "mpi/embermpigen.h"

namespace SST {
namespace Ember {

class EmberRandomCustomTrafficGenerator : public EmberMessagePassingGenerator {

public:
    SST_ELI_REGISTER_SUBCOMPONENT_DERIVED(
        EmberRandomCustomTrafficGenerator,
        "ember",
        "RandomCustomMotif",
        SST_ELI_ELEMENT_VERSION(1,0,0),
        "Performs a random traffic pattern communication",
        SST::Ember::EmberGenerator
    )

    SST_ELI_DOCUMENT_PARAMS(
        {   "arg.messagesize",      "Sets the message size of the communications (in count of DOUBLE)", "1"},
        {   "arg.iterations",       "Sets the number of iterations to perform",     "1"},
    )

    SST_ELI_DOCUMENT_STATISTICS(
        { "time-Init", "Time spent in Init event",          "ns",  0},
        { "time-Finalize", "Time spent in Finalize event",  "ns", 0},
        { "time-Rank", "Time spent in Rank event",          "ns", 0},
        { "time-Size", "Time spent in Size event",          "ns", 0},
        { "time-Send", "Time spent in Recv event",          "ns", 0},
        { "time-Recv", "Time spent in Recv event",          "ns", 0},
        { "time-Irecv", "Time spent in Irecv event",        "ns", 0},
        { "time-Isend", "Time spent in Isend event",        "ns", 0},
        { "time-Wait", "Time spent in Wait event",          "ns", 0},
        { "time-Waitall", "Time spent in Waitall event",    "ns", 0},
        { "time-Waitany", "Time spent in Waitany event",    "ns", 0},
        { "time-Compute", "Time spent in Compute event",    "ns", 0},
        { "time-Barrier", "Time spent in Barrier event",    "ns", 0},
        { "time-Alltoallv", "Time spent in Alltoallv event", "ns", 0},
        { "time-Alltoall", "Time spent in Alltoall event",  "ns", 0},
        { "time-Allreduce", "Time spent in Allreduce event", "ns", 0},
        { "time-Reduce", "Time spent in Reduce event",      "ns", 0},
        { "time-Bcast", "Time spent in Bcast event",        "ns", 0},
        { "time-Gettime", "Time spent in Gettime event",    "ns", 0},
        { "time-Commsplit", "Time spent in Commsplit event", "ns", 0},
        { "time-Commcreate", "Time spent in Commcreate event", "ns", 0},
    )
public:
	EmberRandomCustomTrafficGenerator(SST::ComponentId_t, Params& params);
    	bool generate( std::queue<EmberEvent*>& evQ);

protected:
	uint32_t maxIterations;
	uint32_t iteration;
	uint32_t msgSize;
    MessageResponse m_resp;

    uint64_t m_startTime = 0;
    uint64_t m_stopTime = 0;
    uint64_t avg_time = 0;
    uint64_t local_diff = 0;

    void* allocBuffer;
    void* recvBuffer;
    void* m_sendBuf_small;
    void* m_recvBuf_small;

    std::string name;
    std::string routing_scheme;
    std::string routing_algo;
    std::string shape;
    uint64_t timeout_flow;

    void saveStatistics();

};

}
}

#endif