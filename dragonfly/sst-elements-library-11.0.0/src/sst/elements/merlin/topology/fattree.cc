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
#include "fattree.h"
#include <random>
#include "merlin.h"


#include "sst/elements/firefly/merlinEvent.h"
#include <algorithm>
#include <unordered_map>
#include <stdlib.h>

#define FORCE_ADAPTIVE
#define USE_PENDING
#define RANDOMIZE_TIES

#define DEBUG_MINE 0

using namespace SST::Merlin;
using namespace std;

int rangeRandomAlg2 (int min, int max){
    int n = max - min + 1;
    int remainder = RAND_MAX % n;
    int x;
    do{
        x = rand();
    }while (x >= RAND_MAX - remainder);
    return min + x % n;
}

void
topo_fattree::parseShape(const std::string &shape, int *downs, int *ups) const
{
    size_t start = 0;
    size_t end = 0;

    int levels = std::count(shape.begin(), shape.end(), ':') + 1;
    for ( int i = 0; i < levels; i++ ) {
        end = shape.find(':',start);
        size_t length = end - start;
        std::string sub = shape.substr(start,length);
        
        // Get the up and down
        size_t comma = sub.find(',');
        string down;
        string up;
        if ( comma == string::npos ) {
            down = sub;
            up = "0";
        }
        else {
            down = sub.substr(0,comma);
            up = sub.substr(comma+1);
        }
        
        downs[i] = strtol(down.c_str(), NULL, 0);
        ups[i] = strtol(up.c_str(), NULL, 0);

        // Get things ready to look at next level
        start = end + 1;
    }
}


topo_fattree::topo_fattree(ComponentId_t cid, Params& params, int num_ports, int rtr_id, int num_vns) :
    Topology(cid),
    id(rtr_id),
    num_ports(num_ports),
    num_vns(num_vns),
    num_vcs(-1)
{
    srand(time(NULL));
    string shape = params.find<std::string>("shape");

    vns = new vn_info[num_vns];

    std::vector<std::string> vn_route_algos;
    if ( params.is_value_array("routing_alg") ) {
        params.find_array<std::string>("routing_alg", vn_route_algos);
        if ( vn_route_algos.size() != num_vns ) {
            fatal(CALL_INFO, -1, "ERROR: When specifying routing algorithms per VN, algorithm list length must match number of VNs (%d VNs, %lu algorithms).\n",num_vns,vn_route_algos.size());        
        }
    }
    else {
        std::string route_algo = params.find<std::string>("algorithm", "adaptive");
        for ( int i = 0; i < num_vns; ++i ) vn_route_algos.push_back(route_algo);
    }

    int curr_vc = 0;
    for ( int i = 0; i < num_vns; ++i ) {
        printf("Current Algo is %s\n", vn_route_algos[i].c_str());
        vns[i].start_vc = curr_vc;
        if ( vn_route_algos[i] == "adaptive" ) {
            vns[i].allow_adaptive = true;
            vns[i].num_vcs = 1;
        }
        else if ( vn_route_algos[i] == "deterministic" ) {
            vns[i].allow_adaptive = false;
            vns[i].num_vcs = 1;
        }
        else if ( vn_route_algos[i] == "random" ) {
            vns[i].allow_random = true;
            vns[i].allow_adaptive = false;
            vns[i].num_vcs = 1;
        }
        else if ( vn_route_algos[i] == "ecmp" ) {
            vns[i].allow_ecmp = true;
            vns[i].allow_adaptive = false;
            vns[i].num_vcs = 1;
        } else if ( vn_route_algos[i] == "slingshot" ) {
            vns[i].allow_slingshot = true;
            vns[i].allow_adaptive = false;
            vns[i].num_vcs = 1;
        }
        else {
            output.fatal(CALL_INFO,-1,"Unknown routing mode specified: %s\n",vn_route_algos[i].c_str());
        }
        curr_vc += vns[i].num_vcs;
    }
    adaptive_threshold = params.find<double>("adaptive_threshold", 0.75);

    printf("Threshold is %f\n", adaptive_threshold);
    
    int levels = std::count(shape.begin(), shape.end(), ':') + 1;
    int* ups = new int[levels];
    int* downs= new int[levels];

    parseShape(shape, downs, ups);

    int total_hosts = 1;
    for ( int i = 0; i < levels; i++ ) {
        total_hosts *= downs[i];
    }

    int* routers_per_level = new int[levels];
    routers_per_level[0] = total_hosts / downs[0];

    for ( int i = 1; i < levels; i++ ) {
        routers_per_level[i] = routers_per_level[i-1] * ups[i-1] / downs[i];
    }

    int count = 0;
    rtr_level = -1;
    int routers_per_level_group = 1;
    for ( int i = 0; i < levels; i++ ) {
        int lid = id - count;
        count += routers_per_level[i];
        if ( id < count ) {
            rtr_level = i;
            level_id = lid;
            level_group = lid / routers_per_level_group;
            break;
        }
        routers_per_level_group *= ups[i];
    }

    down_ports = downs[rtr_level];
    up_ports = ups[rtr_level];
    
    // Compute reachable IDs
    int rid = 1;
    for ( int i = 0; i <= rtr_level; i++ ) {
        rid *= downs[i];
    }
    down_route_factor = rid / downs[rtr_level];

    low_host = level_group * rid;
    high_host = low_host + rid - 1;
    
}


topo_fattree::~topo_fattree()
{
    delete[] vns;
}

void topo_fattree::route_adaptive(int port1, int vc1, internal_router_event* ev) {
    int next_port = ev->getNextPort();
    int vc = ev->getVC();
    int index  = next_port*num_vcs + vc;
    if ( outputCredits[index] >= thresholds[index] ) return;
    
    // Send this on the least loaded port.  For now, just look at
    // current VC, later we may look at overall port loading.  Set
    // the max to be the "natural" port and only adaptively route
    // if it's not the best one (ties go to natural port)
    int max = outputCredits[index];
    // If all ports have zero credits left, then we just set
    // it to the port that it would normally go to without
    // adaptive routing.
    int port = next_port;
    for ( int i = (down_ports * num_vcs) + vc; i < num_ports * num_vcs; i += num_vcs ) {
        if ( outputCredits[i] > max ) {
            max = outputCredits[i];
            port = i / num_vcs;
        }
    }
    ev->setNextPort(port);
}

void topo_fattree::route_ecmp(int port, int vc, internal_router_event* ev)  {
    int dest = ev->getDest();
    // Down routes
    if ( dest >= low_host && dest <= high_host ) {
        ev->setNextPort((dest - low_host) / down_route_factor);
    }
    // Up routes
    else {
        SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
        std::string toHash = std::to_string(ev->getSrc()) + "@" + std::to_string(ev->getDest()) + "@" + std::to_string(ffevent->msg_id);
        ev->setNextPort(down_ports + ((std::hash<std::string>{}(toHash) / down_route_factor) % up_ports));
    }
}

void topo_fattree::route_random(int port, int vc, internal_router_event* ev)  {
    int dest = ev->getDest();
    // Down routes
    if ( dest >= low_host && dest <= high_host ) {
        ev->setNextPort((dest - low_host) / down_route_factor);
    }
    // Up routes
    else {
        ev->setNextPort(down_ports + ((rand()) % up_ports));
        //ev->setNextPort(10);
    }
}

void topo_fattree::route_deterministic(int port, int vc, internal_router_event* ev)  {
    int dest = ev->getDest();
    // Down routes
    if ( dest >= low_host && dest <= high_host ) {
        ev->setNextPort((dest - low_host) / down_route_factor);
    }
    // Up routes
    else {
        ev->setNextPort(down_ports + ((dest / down_route_factor) % up_ports));
    }
}


void topo_fattree::route_slingshot(int port, int vc, internal_router_event* ev) {
    
    if (!ackMode) {
        printf("Error, can't have slingshot without ACK");
        exit(0);
    }

    bool changeRoute = true; 
    bool samePath = true;   
    SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
    int msg_id = ffevent->msg_id;
    std::string toHashAck = std::to_string(ev->getSrc()) + "@" + std::to_string(ev->getDest()) + "@" + std::to_string(msg_id);

    if(list_ack_status.count(toHashAck) == 0) {
        samePath = false;            
        //if (DEBUG_MINE) printf("Starting new - Changing Path ID %s@%d - Pkt Sent %d - Received %d - Src %d - Dest %d - Size %d - ID %d - Group %d - UID %d - Size Map %d - Time %ld \n", toHashAck.c_str(), ff_temp->packet_id_in_message, 0, 0, srcIp, destIp, ev->inspectRequest()->size_in_bits / 8, router_id, group_id, 0, list_ack_status.size(), getCurrentSimTimeNano()); fflush(stdout);
    } else if ((list_ack_status.at(toHashAck).first == list_ack_status.at(toHashAck).second)) {
        samePath = false;
        //if (DEBUG_MINE) printf("Starting new - Equal S/R - ID %s@%d - Pkt Sent %d - Received %d - Src %d - Dest %d - Size %d - ID %d - Group %d - UID %d - Size Map %d - Time %ld \n", toHashAck.c_str(), ff_temp->packet_id_in_message, this->list_ack_status.at(toHashAck).first, this->list_ack_status.at(toHashAck).second, srcIp, destIp, ev->inspectRequest()->size_in_bits / 8, router_id, group_id, 0, list_ack_status.size(), getCurrentSimTimeNano()); fflush(stdout);
    } else {
        samePath = true;
        //if (DEBUG_MINE) printf("Same Path - ID %s@%d  - Time %ld \n", toHashAck.c_str(), ff_temp->packet_id_in_message, getCurrentSimTimeNano());
    }

    if (samePath) { //Use same path as before
        changeRoute = false;
        ev->setNextPort(map_cached_ports[toHashAck].second);
        ev->setVC(map_cached_vcs[toHashAck]);
    }
    
    // Change route if we have a packet belonging to a new flowlet
    if (changeRoute) {
        //printf("Changed Route\n");
        route_adaptive(port, vc, ev);
        // Cache port and vc
        map_cached_ports[toHashAck] = std::make_pair(0, ev->getNextPort());
        map_cached_vcs[toHashAck] = ev->getVC(); 
    }
}

void topo_fattree::route_packet(int port, int vc, internal_router_event* ev)
{
    if (ev->is_ack) {
        // We update the ACK count 
        SST::Firefly::FireflyNetworkEvent* ff_ack = getFF(ev);
        int msg_id = ff_ack->msg_id;
        std::string hashAckPkt = std::to_string(ev->getSrc()) + "@" + std::to_string(ev->getDest()) + "@" + std::to_string(msg_id);
        this->list_ack_status[hashAckPkt].second++;
        //printf("Increasing ACK of %s@%d to %d (Router %d)\n",hashAckPkt.c_str(),ff_ack->packet_id_in_message, this->list_ack_status[hashAckPkt].second, router_id);
        return;
    }
    route_deterministic(port,vc,ev);

    if (vns[ev->getVN()].allow_ecmp) {
        route_ecmp(port,vc,ev);
    } else if (vns[ev->getVN()].allow_random) {
        route_random(port,vc,ev);
    } else if (vns[ev->getVN()].allow_slingshot) {
        route_slingshot(port, vc, ev);
    }
    
    int dest = ev->getDest();
    // Down routes are always deterministic and are already done in route
    if ( dest >= low_host && dest <= high_host ) {
        return;
    }
    // Up routes can be adaptive, so things can change from the normal path
    else {
        int vn = ev->getVN();
        // If we're not adaptive, then we're already routed
        if ( !vns[vn].allow_adaptive ) {
            SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
            int index  = ev->getNextPort() * num_vcs + ev->getVC();
            int output_credits = outputCredits[index]/* - pendingCredits[index]*/;
            if (ev->getEncapsulatedEvent()->getSizeInBits() > 500/* && id == 0*/) {
                //printf("Routing in Rtr %d - %d@%d@%d@%d - Port %d - Credits %d (Pending %d) (InBufC %d) - Queue %d - Time %ld\n", id, ev->getSrc(), ev->getDest(), ffevent->msg_id, ffevent->packet_id_in_message, ev->getNextPort(), outputCredits[index], output_credits, port_credit_array[index], output_queue_lengths[index], getCurrentSimTimeNano());
            }
            return;
        }

        // If the port we're supposed to be going to has a buffer with
        // fewer credits than the threshold, adaptively route
        route_ecmp(port,vc,ev);
        //ev->setNextPort(4);
        int next_port = ev->getNextPort();
        int vc = ev->getVC();
        int index  = next_port*num_vcs + vc;
        if ( port_credit_array[index] >= thresholds[index] ) return;
        
        // Send this on the least loaded port.  For now, just look at
        // current VC, later we may look at overall port loading.  Set
        // the max to be the "natural" port and only adaptively route
        // if it's not the best one (ties go to natural port)
        int output_credits_1 = port_credit_array[index]/* - pendingCredits[index]*/;
        int max = output_credits_1;
        // If all ports have zero credits left, then we just set
        // it to the port that it would normally go to without
        // adaptive routing.
        int port = next_port;
        printf("\n   Current Time -> %ld    \n", getCurrentSimTimeNano()); fflush(stdout);
        for ( int i = (down_ports * num_vcs) + vc; i < num_ports * num_vcs; i += num_vcs ) {
            int output_credits = port_credit_array[i]/* - pendingCredits[i]*/;
            if (ev->getEncapsulatedEvent()->getSizeInBits() > 500/* && id == 0*/) {
                SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
                //printf("Routing in Rtr %d - %d@%d@%d@%d - Time %ld - Port %d (Default %d) - Credits %d (Max %d) (Pend %d) (InBuC %d) - Queue %d\n", id, ev->getSrc(), ev->getDest(), ffevent->msg_id, ffevent->packet_id_in_message, getCurrentSimTimeNano(), i / num_vcs, port, outputCredits[i], max, output_credits, port_credit_array[i], output_queue_lengths[i]); fflush(stdout);
            }
            if ( output_credits > max /*|| ( outputCredits[i] == max && rand() % 2)*/ ) {
                //printf("changing %d %d\n", outputCredits[i], max);
                max = output_credits;
                port = i / num_vcs;
                
            } else {
                //printf("OutPut Credits %d - Max %d\n", outputCredits[i], max);
            }
        }

        SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
        if (port != next_port && ffevent->bufSize() > 50) {
            printf("Changed port from %d to %d (Rtr %d - %d@%d@%d@%d)\n", next_port, port, id, ev->getSrc(), ev->getDest(), ffevent->msg_id, ffevent->packet_id_in_message);
        } 

        
        if (ffevent->bufSize() > 50) {
            //printf("Rtr %d - %d@%d@%d@%d - Port %d\n", id, ev->getSrc(), ev->getDest(), ffevent->msg_id, ffevent->packet_id_in_message, port);
        }
            
        ev->setNextPort(port);
    }
}



internal_router_event* topo_fattree::process_input(RtrEvent* ev)
{
    internal_router_event* ire = new internal_router_event(ev);
    ire->setVC(ire->getVN());
    return ire;
}

void topo_fattree::routeInitData(int inPort, internal_router_event* ev, std::vector<int> &outPorts)
{

    if ( ev->getDest() == INIT_BROADCAST_ADDR ) {
        // Send to all my downports except the one it came from
        for ( int i = 0; i < down_ports; i++ ) {
            if ( i != inPort ) outPorts.push_back(i);
        }

        // If I'm not at the top level (no up_ports) an I didn't
        // receive this from an up_port, send to one up port
        if ( up_ports != 0 && inPort < down_ports ) {
            outPorts.push_back(down_ports+(inPort % up_ports));
        }
    }
    else {
        route_deterministic(inPort, 0, ev);
        outPorts.push_back(ev->getNextPort());
    }
}


internal_router_event* topo_fattree::process_InitData_input(RtrEvent* ev)
{
    return new internal_router_event(ev);
}

int
topo_fattree::getEndpointID(int port)
{
    return low_host + port;
}

Topology::PortState topo_fattree::getPortState(int port) const
{
    if ( rtr_level == 0 ) {
        if ( port < down_ports ) return R2N;
        else if ( port >= down_ports ) return R2R;
        else return UNCONNECTED;
    } else {
        return R2R;
    }
}

void topo_fattree::setOutputBufferCreditArray(int const* array, int vcs) {
        num_vcs = vcs;
        outputCredits = array;
        //printf("Credits pointer is %p\n", outputCredits);
        pendingCredits = &(array[num_vcs * num_ports]);
        thresholds = new int[num_vcs * num_ports];
        for ( int i = 0; i < num_vcs * num_ports; i++ ) {
            thresholds[i] = outputCredits[i] * adaptive_threshold;
        }       
}

void
topo_fattree::setOutputQueueLengthsArray(int const* array, int vcs)
{
    output_queue_lengths = array;
    num_vcs = vcs;
}

void
topo_fattree::setCreditBufferArray(int const* array, int vcs)
{
    port_credit_array = array;
    num_vcs = vcs;
}
