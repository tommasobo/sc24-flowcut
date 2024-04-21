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

#include "sst_config.h"

#include "nic.h"

using namespace SST;
using namespace SST::Firefly;

void Nic::RecvMachine::processPkt( FireflyNetworkEvent* ev ) {

	m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE," got a network pkt from node=%d pid=%d for pid=%d size=%zu\n",
                        ev->getSrcNode(),ev->getSrcPid(), ev->getDestPid(), ev->bufSize() );

    std::string flow_id = std::to_string(ev->original_source) + "@" + std::to_string(ev->original_destination) + "@" + std::to_string(ev->msg_id);
    if (ev->is_drain_control) {
        printf("Start Draining has been received, size is %ld - nic %d - %d@%d - time %ld -- %s@%d \n", ev->bufSize(), m_nic.m_myNodeId, ev->original_source, ev->original_destination, m_nic.getCurrentSimTimeNano(), flow_id.c_str(), ev->packet_id_in_message); fflush(stdout);
        m_nic.draining_map[flow_id] = true;
        //m_nic.draining = true;
        m_nic.latest_drain_start = m_nic.getCurrentSimTimeNano();
    }

    if (ev->drain_stop) {
        printf("Stop Draining has been received, size is %ld - nic %d - vn %d - time %ld -- %s@%d \n", ev->bufSize(), m_nic.m_myNodeId, m_vn, m_nic.getCurrentSimTimeNano(), flow_id.c_str(), ev->packet_id_in_message); fflush(stdout);
        m_nic.draining_map[flow_id] = false;
        //m_nic.draining = false;
        m_nic.time_draining = m_nic.time_draining + (m_nic.getCurrentSimTimeNano() - m_nic.latest_drain_start);
    }



    /*
    OLD DRAINING
    if (ev->is_drain_control) {
        printf("Draining control has been received, size is %ld - nic %d - %d@%d - time %ld \n", ev->bufSize(), m_nic.m_myNodeId, ev->original_source, ev->original_destination, m_nic.getCurrentSimTimeNano()); fflush(stdout);
        m_nic.draining = true;
    }

    if (ev->drain_stop) {
        printf("Draining stop has been received, size is %ld - nic %d - vn %d - time %ld \n", ev->bufSize(), m_nic.m_myNodeId, m_vn, m_nic.getCurrentSimTimeNano()); fflush(stdout);
        m_nic.draining = false;
        m_nic.sendNotify(m_vn);
    }*/
    
    if (ev->is_data_packet) {

        // Overll Bandwidth calculation, including pauses
        if (m_nic.packets_received_overall == 0) {
            m_nic.first_packet_time = ev->sent_time_ns;
            m_nic.time_passed = m_nic.getCurrentSimTimeNano() - ev->sent_time_ns;
            m_nic.packets_received_overall += ev->bufSize();
        } else {
            m_nic.time_passed = m_nic.getCurrentSimTimeNano() - m_nic.first_packet_time;
            m_nic.packets_received_overall += ev->bufSize();
        }

        // Update Flow Bandwidth
        std::string toHash = std::to_string(ev->original_source) + "@" + std::to_string(ev->original_destination) + "@" + std::to_string(ev->msg_id);
        m_nic.list_fct_size[toHash] += ev->bufSize();
        //printf("Size now %d - %d\n", m_nic.list_fct_size[toHash], ev->packet_id_in_message);
        if (ev->packet_id_in_message == 0 || ev->packet_id_in_message == 1 ) {
            m_nic.list_fct_first_time[toHash] = ev->sent_time_ns;
            m_nic.list_fct_last_time[toHash] = m_nic.getCurrentSimTimeNano();
        } else {
            m_nic.list_fct_last_time[toHash] = m_nic.getCurrentSimTimeNano();
        }

        /*if (ev->msg_id == 2 && ev->packet_id_in_message==0) {
            printf("Size of this is %ld\n", ev->bufSize());
        }*/

        ev->received_time_ns = m_nic.getCurrentSimTimeNano();
        //printf("Sent Time %" PRIu64 " - Recv Time %" PRIu64 " - Diff %" PRIu64 "\n",ev->sent_time_ns, ev->received_time_ns, ev->received_time_ns - ev->sent_time_ns); fflush(stdout);
        /*if (ev->is_ooo) {
            printf("\nLatency OOO is: %" PRIu64 " %f\n", ev->received_time_ns - ev->sent_time_ns, (float)ev->bufSize() / (ev->received_time_ns - ev->sent_time_ns)); fflush(stdout);
        } else {
            printf("\nLatency is: %" PRIu64 " %f - From %d to %d - Size %d - Sent %ld - Received %ld - Nic %d - Msg ID %d - ID %d\n", ev->received_time_ns - ev->sent_time_ns, ev->original_source, ev->original_destination, (float)ev->bufSize() / (ev->received_time_ns - ev->sent_time_ns), ev->bufSize(), ev->sent_time_ns, m_nic.getCurrentSimTimeNano(), m_nic.m_myNodeId, ev->msg_id, ev->packet_id_in_message); fflush(stdout);
        }*/
    } else if (ev->bufSize() != 49) {
        //printf("There was hope %d\n", ev->bufSize());
    }

    //printf("Max Stram is %d\n", m_maxActiveStreams);
    
    if ( ev->isCtrl() ) {
		m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE,"got a control message\n");
        if (!ev->is_drain_control) {
            m_ctxMap[ ev->getDestPid() ]->newStream( ev );
        } else {
            //m_numActiveStreams--;
        }
    } else {
        if (!ev->is_drain_control) {
            processStdPkt( ev );
        } else {
            //m_numActiveStreams--;
        }
        
    }
}

void Nic::RecvMachine::processStdPkt( FireflyNetworkEvent* ev ) {
    bool blocked = false;
    ProcessPairId id = getPPI( ev );

    //printf("WHY %d %d %d - %d\n", ev->bufSize(), ev->msg_id, ev->packet_id_in_message, m_nic.draining); fflush(stdout);
    if (ev->drain_stop) {
        //m_numActiveStreams--;
        return;
    }

    if (ev->is_drain_control) {
        return;
    }

    StreamBase* stream;
    int pid = ev->getDestPid();

    if ( ev->isHdr() ) {
        if ( m_streamMap.find( id ) != m_streamMap.end() ) {
            //printf("Breaking at %d %d %d - id %d - %d@%d \n", ev->msg_id, ev->packet_id_in_message, ev->bufSize(), id, ev->original_source, ev->original_destination); fflush(stdout);
            m_dbg.fatal(CALL_INFO,-1,"no stream for cnode=%d pid=%d for pid=%d\n",ev->getSrcNode(),ev->getSrcPid(), ev->getDestPid());
        }
        stream = m_ctxMap[pid]->newStream( ev );
        m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE,"new stream %p %s node=%d pid=%d for pid=%d\n",stream, ev->isTail()? "single packet stream":"",
               ev->getSrcNode(),ev->getSrcPid(), pid );

        if ( ! ev->isTail() ) {
            m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE,"multi packet stream, set streamMap PPI=0x%" PRIx64 "\n",id );
            m_streamMap[id] = stream;
        }

    } else {
        if (m_streamMap.find( id ) == m_streamMap.end()) {
            //printf("Breaking at %d %d %d - id %d - %d@%d \n", ev->msg_id, ev->packet_id_in_message, ev->bufSize(), id, ev->original_source, ev->original_destination); fflush(stdout);
        } else {
            //printf("Working at %d %d %d - id %d - %d@%d \n", ev->msg_id, ev->packet_id_in_message, ev->bufSize(), id, ev->original_source, ev->original_destination); fflush(stdout);
        }
        
        assert ( m_streamMap.find( id ) != m_streamMap.end() );

        stream = m_streamMap[id];

        if ( ev->isTail() ) {
            m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE,"tail pkt, clear streamMap PPI=0x%" PRIx64 "\n",id );
            m_streamMap.erase(id);
        } else {
            m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE,"body packet stream=%p\n",stream );
        }

        if ( stream->isBlocked() ) {
            m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE,"stream is blocked stream=%p\n",stream );
            stream->setWakeup(
                [=]() {
                    m_dbg.debug(CALL_INFO_LAMBDA,"processStdPkt",1,NIC_DBG_RECV_MACHINE,"stream is unblocked stream=%p\n",stream );
                    stream->processPktBody( ev );
                }
            );
        } else {
            m_dbg.debug(CALL_INFO,1,NIC_DBG_RECV_MACHINE,"\n" );
            stream->processPktBody(ev);
        }
    }
}

void Nic::RecvMachine::printStatus( Output& out ) {
#ifdef NIC_RECV_DEBUG
    if ( m_nic.m_linkControl->requestToReceive( 0 ) ) {
        out.output( "%lu: %d: RecvMachine `%s` msgCount=%d runCount=%d,"
            " net event avail %d\n",
            Simulation::getSimulation()->getCurrentSimCycle(),
            m_nic. m_myNodeId, state( m_state), m_msgCount, m_runCount,
            m_nic.m_linkControl->requestToReceive( 0 ) );
    }
#endif
}
