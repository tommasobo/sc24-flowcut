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

/*
#include <sst_config.h>
#include "emberallpingpong.h"

using namespace SST::Ember;

#define TAG 0xDEADBEEF

EmberAllPingPongGenerator::EmberAllPingPongGenerator(SST::ComponentId_t id,
                                            Params& params) :
	EmberMessagePassingGenerator(id, params, "AllPingPong"),
    m_loopIndex(0)
{
	m_iterations = (uint32_t) params.find("arg.iterations", 1);
	m_messageSize = (uint32_t) params.find("arg.messageSize", 128);
	m_computeTime = (uint32_t) params.find("arg.computetime", 1000);

    m_sendBuf = memAlloc(m_messageSize);
    m_recvBuf = memAlloc(m_messageSize);
}

bool EmberAllPingPongGenerator::generate( std::queue<EmberEvent*>& evQ)
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

    const bool participate = ( size() % 2 == 0 ) ? true :
	( rank() == ( size() - 1 ) ) ? false : true;

    if( participate ) {
    	enQ_compute( evQ, m_computeTime );

	if ( rank() < size()/2 ) {
        	enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    rank() + (size()/2), TAG, GroupWorld );
        	enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                    rank() + (size()/2), TAG, GroupWorld, &m_resp );

    	} else {
        	enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                    rank() - (size()/2), TAG, GroupWorld, &m_resp );
        	enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    rank() - (size()/2), TAG, GroupWorld );
    	}

    	if ( ++m_loopIndex == m_iterations ) {
        	enQ_getTime( evQ, &m_stopTime );
    	}
    }
    return false;
}

*/
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
#include "emberallpingpong.h"

using namespace SST::Ember;

#define TAG 0xDEADBEEF

EmberAllPingPongGenerator::EmberAllPingPongGenerator(SST::ComponentId_t id,
                                            Params& params) :
	EmberMessagePassingGenerator(id, params, "AllPingPong"),
    m_loopIndex(0)
{
	m_iterations = (uint32_t) params.find("arg.iterations", 1);
	m_messageSize = (uint32_t) params.find("arg.messageSize", 128);
	m_computeTime = (uint32_t) params.find("arg.computetime", 0);

    memSetBacked();
    m_sendBuf = memAllocCustomChar(m_messageSize , 'A');
    m_sendBuf1 = memAllocCustomChar(m_messageSize, 'B');
    m_sendBuf2 = memAllocCustomChar(m_messageSize, 'C');
    m_recvBuf = memAlloc(m_messageSize);

    msgRequests = (MessageRequest*) malloc(sizeof(MessageRequest) * 32);
    
}

bool EmberAllPingPongGenerator::generate( std::queue<EmberEvent*>& evQ)
{
    enQ_compute( evQ, m_computeTime );
    int numNodes = 16 * 16;
    if ( m_loopIndex == m_iterations ) {
        if (nextMRIndex > 0) {
            //enQ_waitall( evQ, nextMRIndex, msgRequests, NULL );
        }
        if ( 0 == rank()) {
            double totalTime = (double)(m_stopTime - m_startTime)/1000000000.0;

            double latency = ((totalTime/m_iterations)/2);
            double bandwidth = (double) m_messageSize / latency;

            printf("\nRuntime: %.3f\n", totalTime * 1000000.0);

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

    int num_routers = 16 * 4;

    bool participate = true;
    /*
    if(participate) {  
        // First Group          
        if ( rank() < numNodes) {
            int index_in_router = rank() % 16;
            if (index_in_router == 2 || index_in_router == 4) {
                enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + numNodes), TAG, GroupWorld );
            } else if (index_in_router == 6 || index_in_router == 8) {
                enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + (numNodes * 2)), TAG, GroupWorld );
            } else if (index_in_router == 10 || index_in_router == 12) {
                enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                    (rank() + (numNodes * 3)), TAG, GroupWorld );
            }
        // Second Group
        } else if (rank() >= numNodes && rank() < numNodes * 2) {
            int index_in_router = rank() % 16;
            if (index_in_router == 2 || index_in_router == 4) {
                enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,  (rank() - numNodes) % size(), TAG,
					GroupWorld, &m_req);
                enQ_wait(evQ, &m_req);
            }
        // Third Group
        } else if (rank() >= numNodes * 2 && rank () < numNodes * 3) {
            int index_in_router = rank() % 16;
            if (index_in_router == 6 || index_in_router == 8) {
                enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,  (rank() - (numNodes * 2)) % size(), TAG,
					GroupWorld, &m_req2);
                enQ_wait(evQ, &m_req2);
            } 
        // Fourth Group
        } else {
            int index_in_router = rank() % 16;
            if (index_in_router == 10 || index_in_router == 12) {
                enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,  (rank() - (numNodes * 3)) % size(), TAG,
					GroupWorld, &m_req3);
                enQ_wait(evQ, &m_req3);
            }

        }
    }/*
    
    /*
    if ( rank() == 0) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld );
        enQ_send( evQ, m_sendBuf1, m_messageSize, CHAR,
                1, TAG, GroupWorld );
        enQ_send( evQ, m_sendBuf2, m_messageSize, CHAR,
                1, TAG, GroupWorld );
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld, &m_resp );
    } else if (rank() == 1) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld, &m_resp );
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld, &m_resp );
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld, &m_resp );
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld );

    }*/

    /* if ( rank() == 16) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                256 + 16, TAG, GroupWorld );
    } else if (rank() == 256 + 16) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                16, TAG, GroupWorld, &m_resp );
    }

    if ( rank() == 4) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                256+4, TAG, GroupWorld );
    } else if (rank() == 256+4) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                4, TAG, GroupWorld, &m_resp );
    }*/

    /*if ( rank() == 16) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                (256*2) + 16, TAG, GroupWorld );
    } else if (rank() == (256*2) + 16) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                16, TAG, GroupWorld, &m_resp );
    }

    if ( rank() == 16) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                (256*3)+16, TAG, GroupWorld );
    } else if (rank() == (256*3)+16) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                16, TAG, GroupWorld, &m_resp );
    }

    if ( rank() == 1) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                256+1, TAG, GroupWorld );
    } else if (rank() == 256+1) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld, &m_resp );
    }*/


    /*if ( rank() < 16) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                256+rank(), TAG, GroupWorld );
    } else if (rank() >= 256 && rank() < 256+16) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                rank()-256, TAG, GroupWorld, &m_resp );
    }*/


    
    /*
    if ( rank() < numNodes) {

        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                (rank() + numNodes), TAG, GroupWorld );
        //enQ_wait(evQ, &m_req);
    } else if (rank() < numNodes * 2) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,  (rank() - numNodes), TAG,
                GroupWorld);

    }
    
   if ( rank() == 1) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                17, TAG, GroupWorld );
    } else if (rank() == 17) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld, &m_resp );
    }*/


    /*if ( rank() == 0) {
        enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, 100, TAG,
                                                GroupWorld, &m_req);
        enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, 100, TAG,
                                                GroupWorld, &m_req);
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                   100, TAG, GroupWorld, &m_req);
    } else if (rank() == 100) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                   0, TAG, GroupWorld, &m_req);
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                   0, TAG, GroupWorld, &m_req);
        enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, 0, TAG,
                                                GroupWorld, &m_req);
        enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, 88, TAG,
                                                GroupWorld, &m_req);
    } else if (rank() == 88) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                   100, TAG, GroupWorld, &m_req);
    }*/

   /* if (rank() > 15 && rank() < 32) {
        /*enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                i, TAG, GroupWorld, &msgRequests[nextMRIndex++]);
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                rank() - 16, TAG, GroupWorld, &m_resp );
    }
    
    if ( rank() < 16) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                rank() + 16, TAG, GroupWorld );
    } 


    if ( rank() == 0) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                12, TAG, GroupWorld );
    } else if (rank() == 12) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld,&m_req );
    }*/

    /*
    if ( rank() == 0) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                56, TAG, GroupWorld );
    } else if (rank() == 56) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld,&m_resp );
    } else if (rank() == 1) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                57, TAG, GroupWorld );
    } else if (rank() == 57) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld,&m_resp );
    } else if (rank() == 2) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                58, TAG, GroupWorld );
    } else if (rank() == 58) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                2, TAG, GroupWorld,&m_resp );
    }*/

    /* if ( rank() < 8) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                size() - 1 - rank(), TAG, GroupWorld );
    } else if (rank() >= 56) {
        enQ_recv( evQ, m_recvBuf, m_messageSize, CHAR,
                (size() - 1 - rank()), TAG, GroupWorld, &m_resp );
    }*/


    // Scenario 1
    /*if (rank() == 0) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                63, TAG, GroupWorld );
    } else if (rank() == 63) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld,&m_req );
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                8, TAG, GroupWorld,&m_req );
    } else if (rank() == 8) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                63, TAG, GroupWorld );
    }


    // Scenario 2
    if (rank() == 0) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                63, TAG, GroupWorld );
    } else if (rank() == 63) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld,&m_req );
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                8, TAG, GroupWorld,&m_req );
    } else if (rank() == 8) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                63, TAG, GroupWorld );
    }
    if (rank() == 1) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                62, TAG, GroupWorld );
    } else if (rank() == 62) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld,&m_req );
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                9, TAG, GroupWorld,&m_req );
    } else if (rank() == 9) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                62, TAG, GroupWorld );
    }

    // Scenario 3
    if (rank() == 0) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                56, TAG, GroupWorld );
    } else if (rank() == 56) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld,&m_req );
    } else if (rank() == 1) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                57, TAG, GroupWorld );
    } else if (rank() == 57) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                1, TAG, GroupWorld,&m_req );
    }*/


    // Scenario 4
    /*if ( rank() < 8) {
        enQ_send( evQ, m_sendBuf, m_messageSize, CHAR,
                rank() + 56, TAG, GroupWorld );
    } else if (rank() > 55) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                rank() - 56, TAG, GroupWorld,&m_req );
    }*/

    if ( rank() == 0) {
        enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, 30, TAG,
                                                GroupWorld, &m_req);
        enQ_isend( evQ, m_sendBuf, m_messageSize, CHAR, 33, TAG,
                                                GroupWorld, &m_req);
    } else if (rank() == 33) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld,&m_req );
    } else if (rank() == 30) {
        enQ_irecv( evQ, m_recvBuf, m_messageSize, CHAR,
                0, TAG, GroupWorld,&m_req );
    }
        
    
    if ( ++m_loopIndex == m_iterations ) {
        //enQ_barrier(evQ, GroupWorld);
        if ( 0 == rank() ) {
            enQ_getTime( evQ, &m_stopTime );
        } 
    }
    
    return false;
}
