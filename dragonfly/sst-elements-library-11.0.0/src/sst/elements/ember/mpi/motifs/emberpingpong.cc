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
#include "emberpingpong.h"

using namespace SST::Ember;

int counter = 0;

#define TAG 0xDEADBEEF
#define NUM_PACKETS 1000

int table_received_packets_[1][1000];

EmberPingPongGenerator::EmberPingPongGenerator(SST::ComponentId_t id, Params& params ) :
	EmberMessagePassingGenerator(id, params, "PingPong"),
    m_loopIndex(0),
    m_rank2(1),
    m_blockingSend( true ),
    m_blockingRecv( true ),
    m_waitall( false )
{
	m_messageSize = (uint32_t) params.find("arg.messageSize", 1);
	m_iterations = (uint32_t) params.find("arg.iterations", 1);
	m_rank2 = (uint32_t) params.find("arg.rank2", 1);

    memSetBacked();	
    m_sendBuf = memAlloc(m_messageSize);
    m_recvBuf = memAlloc(m_messageSize);
    m_blockingSend = (uint32_t) params.find("arg.blockingSend", true);;
    m_blockingRecv = (uint32_t) params.find("arg.blockingRecv", true);;
    m_waitall = (uint32_t) params.find("arg.waitall", false);

    ((char*) m_sendBuf)[0] = 77;

    //printf("Address m_sendBuf is %p, Address m_recvBuf is %p", m_sendBuf, m_recvBuf);

}

bool EmberPingPongGenerator::generate( std::queue<EmberEvent*>& evQ)
{
    if ( m_loopIndex == m_iterations || ! ( 0 == rank() || m_rank2 == rank() ) ) {
        if ( 0 == rank()) {
            double totalTime = (double)(m_stopTime - m_startTime)/1000000000.0;

            double latency = ((totalTime/m_iterations)/2);
            double bandwidth = (double) m_messageSize / latency;

            output("%s: otherRank %d, total time %.3f us, loop %d, bufLen %d"
                    ", latency %.3f us. bandwidth %f GB/s\n",
                                getMotifName().c_str(), m_rank2,
                                totalTime * 1000000.0, m_iterations,
                                m_messageSize,
                                latency * 1000000.0,
                                bandwidth / 1000000000.0 );
        }
        return true;
    }

    //printf("CHIAMATA - LOOP INDEX %d - ITERATION %d - RANK %d\n", m_loopIndex, m_iterations, rank());

    if ( 0 == m_loopIndex ) {
        verbose(CALL_INFO, 1, 0, "rank=%d size=%d\n", rank(), size());

        if ( 0 == rank() ) {
        	output("rank2=%d messageSize=%d iterations=%d\n",m_rank2, m_messageSize, m_iterations);
            enQ_getTime( evQ, &m_startTime );
        }
    }


    if((m_loopIndex % 5 == 0) && m_loopIndex > 0) {
        enQ_compute( evQ, 102400 );
    }

    
    if ( 0 == rank()) {
    //printf(" Printing Send: ");
    for (int i = 0; i < m_messageSize; i++) {
        unsigned char c = ((char*)m_sendBuf)[i] ;    
        //printf ("%c ", c) ;
    }
    //printf(" ");
        if ( m_blockingSend ) {
            //printf("Blocking Send First, Rank %d", rank());
            enQ_send( evQ, m_sendBuf, m_messageSize, CHAR, m_rank2,
                                                TAG, GroupWorld );
        } else {
            enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, m_rank2,
                                                TAG, GroupWorld, &m_req );
            if ( m_waitall ) {
                enQ_waitall( evQ, 1, &m_req, (MessageResponse**)&m_resp );
            } else {
                enQ_wait( evQ, &m_req );
            }
        }
        if ( m_blockingRecv ) {
            enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR, m_rank2,
                                                TAG, GroupWorld, &m_resp );
            //printf("Blocking Recv First, Rank %d", rank());
            enQ_compute(evQ, [&]() {   
                printf("Printing Recv1: ");
                for (int i = 0; i < m_messageSize; i++) {
                    char c = *((char*)m_recvBuf + i);
                    //printf ("%c ", c) ;
                }
                return 0;
            });
        } else {
            enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR, m_rank2,
                                                TAG, GroupWorld, &m_req );
            if ( m_waitall ) {
                enQ_waitall( evQ, 1, &m_req, (MessageResponse**)&m_resp );
            } else {
                enQ_wait( evQ, &m_req );
            }
        }
	} else if ( m_rank2 == rank()) {
        if ( m_blockingRecv ) {
            enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR, 0,
                                                TAG, GroupWorld, &m_resp );
            //printf("Printing Recv2 Outside Compute: ");
            for (int i = 0; i < m_messageSize; i++) {
                char c = *((char*)m_recvBuf + i);
                //printf ("%c ", c) ;
            }
            //printf("Blocking Recv Second, Rank %d", rank());
            enQ_compute(evQ, [&]() {   
                //printf("Printing Recv2: ");
                for (int i = 0; i < m_messageSize; i++) {
                    char c = *((char*)m_recvBuf + i);
                    //printf ("%c ", c) ;
                }
                return 0;
            });
        } else {
		    enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR, 0,
                                                TAG, GroupWorld, &m_req );
            if ( m_waitall ) {
                enQ_waitall( evQ, 1, &m_req, (MessageResponse**)&m_resp );
            } else {
                enQ_wait( evQ, &m_req );
            }
        }
        if ( m_blockingSend ) {
            enQ_send( evQ, m_sendBuf, m_messageSize, CHAR, 0,
                                                TAG, GroupWorld );
        //printf("Blocking Send Second, Rank %d", rank());
        } else {
            enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, 0,
                                                TAG, GroupWorld, &m_req );
            if ( m_waitall ) {
                enQ_waitall( evQ, 1, &m_req, (MessageResponse**)&m_resp );
            } else {
                enQ_wait( evQ, &m_req );
            }
        }
	}

    if ( ++m_loopIndex == m_iterations ) {
        enQ_getTime( evQ, &m_stopTime );
    }
    return false;
}