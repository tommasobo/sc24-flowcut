
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
#include "emberbert.h"

using namespace SST::Ember;

#define TAG 0xDEADBEEF

EmberBertGenerator::EmberBertGenerator(SST::ComponentId_t id,
                                            Params& params) :
	EmberMessagePassingGenerator(id, params, "Bert"),
    m_loopIndex(0)
{
	m_iterations = (uint32_t) params.find("arg.iterations", 1);
	m_messageSize = (uint32_t) params.find("arg.messageSize", 128);
	m_computeTime = (uint32_t) params.find("arg.computetime", 1000);

    memSetBacked();
    m_sendBuf = memAllocCustomChar(m_messageSize , 'A');
    m_sendBuf1 = memAllocCustomChar(m_messageSize, 'B');
    m_sendBuf2 = memAllocCustomChar(m_messageSize, 'C');
    m_recvBuf = memAlloc(m_messageSize);
}

bool EmberBertGenerator::generate( std::queue<EmberEvent*>& evQ)
{
    if ( m_loopIndex == m_iterations ) {
        if ( 0 == rank()) {
            double totalTime = (double)(m_stopTime - m_startTime)/1000000000.0;

            double latency = ((totalTime/m_iterations)/2);
            double bandwidth = (double) m_messageSize / latency;

            output("%s: total time %.3f us, loop %d, bufLen %d"
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

    if ( rank() == 0) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld );
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld, &m_resp );
    } else if (rank() == 1) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld, &m_resp );
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld );

    }
            
    if ( ++m_loopIndex == m_iterations ) {
        if ( 0 == rank() ) {
            enQ_getTime( evQ, &m_stopTime );
        } 
    }
    
    return false;
}
