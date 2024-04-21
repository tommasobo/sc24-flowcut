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


#ifndef COMPONENTS_HR_ROUTER_HR_ROUTER_H
#define COMPONENTS_HR_ROUTER_HR_ROUTER_H

#include <sst/core/clock.h>
#include <sst/core/component.h>
#include <sst/core/event.h>
#include <sst/core/link.h>
#include <sst/core/output.h>
#include <sst/core/timeConverter.h>

#include <sst/core/statapi/stataccumulator.h>
#include <sst/core/shared/sharedArray.h>

#include <queue>

#include "sst/elements/merlin/router.h"

using namespace SST;

namespace SST {
namespace Merlin {

class AckInfo {      
public:           
    int packet_source = 50;        
    int packet_dest; 
    int expected_previous_port; 
    int next_port_ack; 
    int msg_id;
    int packet_id_in_message;
    internal_router_event* ev;
    int vc;
    AckInfo(int packet_source, int packet_destt, int expected_previous_port, int next_port_ack, internal_router_event* ev, int index_msg, int packet_id_in_message, int vc) { 
      this->packet_source = packet_source;
      this->packet_dest = packet_destt;
      this->expected_previous_port = expected_previous_port;
      this->next_port_ack = next_port_ack;
      this->ev = ev;
      this->msg_id = index_msg;
      this->packet_id_in_message = packet_id_in_message;
      this->vc = vc;
    }
};

class FctStats {      
public:           
    int packets_sent;      
    int acks_received; 
    uint64_t time_start; 
    uint64_t time_stop; 
    FctStats(int packets_sent, int acks_received, uint64_t time_start, uint64_t time_stop) { 
      this->packets_sent = packets_sent;
      this->acks_received = acks_received;
      this->time_start = time_start;
      this->time_stop = time_stop;
    }
};

class PortControlBase;

class hr_router : public Router {

public:

    SST_ELI_REGISTER_COMPONENT(
        hr_router,
        "merlin",
        "hr_router",
        SST_ELI_ELEMENT_VERSION(1,0,0),
        "High radix router",
        COMPONENT_CATEGORY_NETWORK)

    SST_ELI_DOCUMENT_PARAMS(
        {"id",                 "ID of the router."},
        {"num_ports",          "Number of ports that the router has"},
        {"topology",           "Name of the topology subcomponent that should be loaded to control routing."},
        {"xbar_arb",           "Arbitration unit to be used for crossbar.","merlin.xbar_arb_lru"},
        {"link_bw",            "Bandwidth of the links specified in either b/s or B/s (can include SI prefix)."},
        {"flit_size",          "Flit size specified in either b or B (can include SI prefix)."},
        {"xbar_bw",            "Bandwidth of the crossbar specified in either b/s or B/s (can include SI prefix)."},
        {"input_latency",      "Latency of packets entering switch into input buffers.  Specified in s (can include SI prefix)."},
        {"output_latency",     "Latency of packets exiting switch from output buffers.  Specified in s (can include SI prefix)."},
        {"input_buf_size",     "Size of input buffers specified in b or B (can include SI prefix)."},
        {"output_buf_size",    "Size of output buffers specified in b or B (can include SI prefix)."},
        {"network_inspectors", "Comma separated list of network inspectors to put on output ports.", ""},
        {"oql_track_port",     "Set to true to track output queue length for an entire port.  False tracks per VC.", "false"},
        {"oql_track_remote",   "Set to true to track output queue length including remote input queue.  False tracks only local queue.", "false"},
        {"num_vns",            "Number of VNs.","2"},
        {"vn_remap",           "Array that specifies the vn remapping for each node in the systsm."},
        {"vn_remap_shm",       "Name of shared memory region for vn remapping.  If empty, no remapping is done", ""},
        {"debug",              "Turn on debugging for router. Set to 1 for on, 0 for off.", "0"}
    )

    SST_ELI_DOCUMENT_STATISTICS(
        { "send_bit_count",     "Count number of bits sent on link", "bits", 1},
        { "send_packet_count",  "Count number of packets sent on link", "packets", 1},
        { "output_port_stalls", "Time output port is stalled (in units of core timebase)", "time in stalls", 1},
        { "xbar_stalls",        "Count number of cycles the xbar is stalled", "cycles", 1},
        { "idle_time",          "Amount of time spent idle for a given port", "units of core timebase", 1},
        { "width_adj_count",    "Number of times that link width was increased or decreased", "width adjustment count", 1}
    )

    SST_ELI_DOCUMENT_PORTS(
        {"port%(num_ports)d",  "Ports which connect to endpoints or other routers.", { "merlin.RtrEvent", "merlin.internal_router_event", "merlin.topologyevent", "merlin.credit_event" } }
    )

    SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS(
        {"topology", "Topology object to control routing", "SST::Merlin::Topology" },
        {"XbarArb", "Crossbar arbitration", "SST::Merlin::XbarArbitration" },
        {"portcontrol", "PortControl blocks", "SST::Merlin::PortInterface" }
    )

private:
    static int num_routers;
    static int print_debug;
    int id;
    int num_ports;
    int num_vns;
    std::string vn_remap_shm;
    int vn_remap_shm_size;
    int num_vcs;
    std::vector<int> vcs_per_vn;
    std::vector<int> draining_per_host;
    std::unordered_map<std::string,  bool> draining_status_map;
    uint64_t total_clocks = 0;
    uint64_t total_clocks_alternative = 0;
    uint64_t* busy_clocks;
    uint64_t* busy_clocks_alternative;
    uint64_t* busy_clocks_alternative2;
    int temp_counter = 0;

    uint64_t** port_utilization;

    uint64_t* port_utilization_time;

    Topology* topo;
    XbarArbitration* arb;

    PortInterface** ports;
    internal_router_event** vc_heads;
    int* xbar_in_credits;
    int* pending_credits;
    int* output_queue_lengths;
    int* port_credits_out;


    std::unordered_map<int, int> previous_port_for_ack;


    std::vector<AckInfo> ack_list;

    std::vector<float> list_global_avg;
    std::vector<float> list_intra_avg;
    std::vector<float> list_host_avg;

    // <Src, Dest> -> <Sent Data, Received Acks>
    std::unordered_map<std::string,  std::pair<int, int>> list_ack_status;
    std::unordered_map<std::string,  uint64_t> exponential_avg;
    std::unordered_map<std::string,  uint64_t> min_latency;
    std::unordered_map<std::string,  uint64_t> latest_rtt;
    std::unordered_map<std::string,  int> latest_hop_count;
    std::unordered_map<int,  uint64_t> reference_rtt;

    std::unordered_map<std::string,  uint64_t> latest_ingress_timestamp;
    std::unordered_map<std::string,  float> exponential_avg_send_rate;
    std::unordered_map<std::string,  uint64_t> latest_egress_timestamp;
    std::unordered_map<std::string,  uint64_t> exponential_avg_recv_rate;


    std::unordered_map<std::string,  uint64_t> list_fct_start;
    std::unordered_map<std::string,  uint64_t> list_fct_stop;

    std::unordered_map<std::string,  int> packet_sent_fct;
    std::unordered_map<std::string,  int> packet_ack_fct;

    std::unordered_map<std::string,  FctStats> list_fct_data;
    // 
    int sent_packets = 0;
    int received_packets = 0;

    int active_flows = 0;
    int max_active_flows = 0;


#if VERIFY_DECLOCKING
    bool clocking;
#endif

    int* in_port_busy;
    int* out_port_busy;
    int* progress_vcs;

    UnitAlgebra input_buf_size;
    UnitAlgebra output_buf_size;

    Cycle_t unclocked_cycle;
    std::string xbar_bw;
    TimeConverter* xbar_tc;
    Clock::Handler<hr_router>* my_clock_handler;

    std::vector<std::string> inspector_names;

    bool clock_handler(Cycle_t cycle);
    bool needs_drain(internal_router_event* ev, std::string toHash);
    static void sigHandler(int signal);

    void init_vcs();
    Statistic<uint64_t>** xbar_stalls;

    Output& output;

    Shared::SharedArray<int> shared_array;

public:
    hr_router(ComponentId_t cid, Params& params);
    ~hr_router();

    void init(unsigned int phase);
    void complete(unsigned int phase);
    void setup();
    void finish();

    void notifyEvent();
    int const* getOutputBufferCredits() {return xbar_in_credits;}
    int const* getOutputQueueLengths() {return output_queue_lengths;}

    void sendCtrlEvent(CtrlRtrEvent* ev, int port = -1);
    void recvCtrlEvent(int port, CtrlRtrEvent* ev);

    void dumpState(std::ostream& stream);
    void printStatus(Output& out);

    void reportIncomingEvent(internal_router_event* ev);

};

}
}

#endif // COMPONENTS_HR_ROUTER_HR_ROUTER_H
