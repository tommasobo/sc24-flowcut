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
using namespace SST::Interfaces;

#define DEBUG_MINE 0 

void Nic::SendMachine::streamInit( SendEntryBase* entry )
{
    MsgHdr hdr;
    msg_id++;
    //printf("ID %d - MsgCount %d\n", m_nic.m_myNodeId, msg_id); fflush(stdout);

#ifdef NIC_SEND_DEBUG
    ++m_msgCount;
#endif
    hdr.op = entry->getOp();
    hdr.id_msg = number_msg_sent;

    m_dbg.debug(CALL_INFO,1,NIC_DBG_SEND_MACHINE,
        "%p setup hdr, srcPid=%d, destNode=%d dstPid=%d bytes=%lu\n", entry,
        entry->local_vNic(), entry->dest(), entry->dst_vNic(), entry->totalBytes() ) ;

    FireflyNetworkEvent* ev = new FireflyNetworkEvent(m_pktOverhead );
    
    ev->setDestPid( entry->dst_vNic() );
    ev->setSrcPid( entry->local_vNic() );
    ev->setHdr();

    entry->m_start = m_nic.getCurrentSimTimeNano();
    if ( entry->isCtrl() || entry->isAck() ) {
        ev->setCtrl();
        entry->is_data = false;
    }

    ev->bufAppend( &hdr, sizeof(hdr) ); 
    ev->bufAppend( entry->hdr(), entry->hdrSize() );

    
    m_nic.schedCallback( std::bind( &Nic::SendMachine::getPayload, this, entry, ev ), entry->txDelay() );

}

void Nic::SendMachine::getPayload( SendEntryBase* entry, FireflyNetworkEvent* ev )
{
    int pid = entry->local_vNic();
    ev->setDestPid( entry->dst_vNic() );
    ev->setSrcPid( pid );

    
    
    if (!m_inQ->isFull()) {
	    std::vector< MemOp >* vec = new std::vector< MemOp >;
        entry->copyOut( m_dbg, m_packetSizeInBytes, *ev, *vec );
        ev->index_msg = number_msg_sent;
        m_dbg.debug(CALL_INFO,2,NIC_DBG_SEND_MACHINE, "enque load from host, %lu bytes\n",ev->bufSize());
        

        std::string flow_id = std::to_string(m_nic.m_myNodeId) + "@" + std::to_string(entry->dest()) + "@" + std::to_string(this->msg_id);

        if (DEBUG_MINE) printf("NIC %d - Draining is %d - Full is %d - Size is %d -- %s@%d \n",m_nic.m_myNodeId, m_nic.draining_map[flow_id], m_inQ->isFull(), ev->bufSize(), flow_id.c_str(), this->packet_id_in_message + 1); fflush(stdout);
        
        if (m_nic.draining_map[flow_id]) {
            if (DEBUG_MINE) printf("Returning %s\n",flow_id.c_str());
            m_nic.schedCallback( std::bind( &Nic::SendMachine::getPayload, this, entry, ev ), 100);
            return;
        }

        packet_id++;
        packet_id_in_message = this->msg_list[msg_id];
        this->msg_list[msg_id]++;
        ev->packet_id_in_message = this->packet_id_in_message;
        ev->packet_id = this->packet_id;
        ev->msg_id = this->msg_id;

        if ( entry->isDone() ) {
            ev->setTail();
            m_inQ->enque( m_unit, pid, vec, ev, entry->vn(), entry->dest(), std::bind( &Nic::SendMachine::streamFini, this, entry ) );
        } else {
            m_inQ->enque( m_unit, pid, vec, ev, entry->vn(), entry->dest() );
            if (DEBUG_MINE) printf("Sending Packet1 %d - %d@%d@%d@%d - %ld\n", ev->bufSize(), m_nic.m_myNodeId,  entry->dest(), ev->msg_id, ev->packet_id_in_message, m_nic.getCurrentSimTimeNano());
            m_nic.schedCallback( std::bind( &Nic::SendMachine::getPayload, this, entry, new FireflyNetworkEvent(m_pktOverhead) ), 82);
        }

    } else {
        //printf("Draining %d - Full %d\n", m_nic.draining, m_inQ->isFull()); fflush(stdout);
        m_dbg.debug(CALL_INFO,2,NIC_DBG_SEND_MACHINE, "blocked by host\n");
        m_inQ->wakeMeUp( std::bind( &Nic::SendMachine::getPayload, this, entry, ev ) );
    }
}
void Nic::SendMachine::streamFini( SendEntryBase* entry )
{
    m_dbg.debug(CALL_INFO,1,NIC_DBG_SEND_MACHINE, "%p sendMachine=%d pid=%d bytes=%zu latency=%" PRIu64 "\n",entry,m_id, entry->local_vNic(),
            entry->totalBytes(), m_nic.getCurrentSimTimeNano() - entry->m_start);

    ++m_numSent;
    //printf("Nic Send Machine5 %ld\n", m_nic.getCurrentSimTimeNano()); fflush(stdout);
    if ( m_I_manage ) {
        m_sendQ.pop();
        if ( ! m_sendQ.empty() )  {
            streamInit( m_sendQ.front() );
        }
    } else {
        m_activeEntry = NULL;
        m_nic.notifySendDone( this, entry );
    }

    if ( entry->shouldDelete() ) {
        m_dbg.debug(CALL_INFO,2,NIC_DBG_SEND_MACHINE, "%p delete SendEntry entry, pid=%d\n",entry, entry->local_vNic());
        delete entry;
    }
}

void  Nic::SendMachine::InQ::enque( int unit, int pid, std::vector< MemOp >* vec,
            FireflyNetworkEvent* ev, int vn, int dest, Callback callback )
{
    //printf("Here 1\n"); fflush(stdout);
    ++m_numPending;
	m_nic.m_sendStreamPending->addData( m_numPending );

    m_dbg.verbosePrefix(prefix(), CALL_INFO,2,NIC_DBG_SEND_MACHINE, "get timing for packet %" PRIu64 " size=%lu numPending=%d\n",
                 m_pktNum,ev->bufSize(), m_numPending);

    m_nic.dmaRead( unit, pid, vec,
		std::bind( &Nic::SendMachine::InQ::ready, this,  ev, vn, dest, callback, m_pktNum++ )
    );
	// don't put code after this, the callback may be called serially
}

void Nic::SendMachine::InQ::ready( FireflyNetworkEvent* ev, int vn, int dest, Callback callback, uint64_t pktNum )
{
    //printf("Here 2\n"); fflush(stdout);
    m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "packet %" PRIu64 " is ready, expected=%" PRIu64 "\n",pktNum,m_expectedPkt);
    assert(pktNum == m_expectedPkt++);

    //if (ev->bufSize() > 50)
        //printf("Nic Send Machine2 %ld\n", m_nic.getCurrentSimTimeNano()); fflush(stdout);
    if ( m_pendingQ.empty() && ! m_outQ->isFull() ) {
        ready2( ev, vn, dest, callback );
    } else  {
        m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "blocked by OutQ\n");
        m_pendingQ.push( Entry( ev, vn, dest, callback, pktNum ) );
        if ( 1 == m_pendingQ.size() )  {
            m_outQ->wakeMeUp( std::bind( &Nic::SendMachine::InQ::processPending, this ) );
        }
    }
}

void Nic::SendMachine::InQ::ready2( FireflyNetworkEvent* ev, int vn, int dest, Callback callback )
{
    //printf("Here 3\n"); fflush(stdout);
    m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "pass packet to OutQ numBytes=%lu\n", ev->bufSize() );
    --m_numPending;
    m_outQ->enque( ev, vn, dest, callback );
    //if (ev->bufSize() > 50)
        //printf("Nic Send Machine3 %ld\n", m_nic.getCurrentSimTimeNano()); fflush(stdout);
    
    if ( m_callback ) {
        m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "wakeup send machine\n");
        m_callback( );
        m_callback = NULL;
    }
}

void Nic::SendMachine::InQ::processPending( )
{
    //printf("Here 4\n"); fflush(stdout);
    m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "size=%lu\n", m_pendingQ.size());
    Entry& entry = m_pendingQ.front();
    ready2( entry.ev, entry.vn, entry.dest, entry.callback );

    m_pendingQ.pop();
    if ( ! m_pendingQ.empty() ) {
        if ( ! m_outQ->isFull() ) {
            //printf("Nic Send Machine4a %ld\n", m_nic.getCurrentSimTimeNano()); fflush(stdout);
            m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "schedule next\n");
            m_nic.schedCallback( std::bind( &Nic::SendMachine::InQ::processPending, this ) );
        } else {
            //printf("Nic Send Machine4b %ld\n", m_nic.getCurrentSimTimeNano()); fflush(stdout);
            m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "schedule wakeup\n");
            m_outQ->wakeMeUp( std::bind( &Nic::SendMachine::InQ::processPending, this ) );
        }
    }
}

void Nic::SendMachine::OutQ::enque( FireflyNetworkEvent* ev, int vn, int dest, Callback callback )
{
	SimTime_t now = Simulation::getSimulation()->getCurrentSimCycle();
	if ( now > m_lastEnq ) {
		m_lastEnq = now;
		m_enqCnt = 0;
	}
	++m_enqCnt;
    
    //printf("Here 5 - Size %ld - Msg %d - MsgID %d\n", ev->bufSize(), ev->msg_id, ev->packet_id_in_message); fflush(stdout);

	PriorityX* px = new PriorityX( m_lastEnq, m_enqCnt, new X( std::bind( &Nic::SendMachine::OutQ::pop, this, callback ), ev, dest ) );

	++m_qCnt;
	m_dbg.verbosePrefix(prefix(),CALL_INFO,2,NIC_DBG_SEND_MACHINE, "qCnt=%d priority=%" PRIu64 ".%d\n", m_qCnt, m_lastEnq, m_enqCnt);

    ev->sent_time_ns = m_nic.getCurrentSimTimeNano();
    //if (ev->bufSize() > 50)
    //    printf("Nic Send Machine1 %ld\n", m_nic.getCurrentSimTimeNano()); fflush(stdout);
	m_nic.notifyHavePkt( px, vn );
}
