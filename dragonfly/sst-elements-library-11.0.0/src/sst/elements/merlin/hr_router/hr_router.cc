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
#include "hr_router/hr_router.h"

#include <sst/core/params.h>
#include <sst/core/simulation.h>
#include <sst/core/timeLord.h>
#include <sst/core/unitAlgebra.h>

#include <sstream>
#include <string>
#include <iterator>


#include <signal.h>


#include "merlin.h"
#include "sst/elements/firefly/merlinEvent.h"
#include "sst/elements/firefly/ctrlMsg.h"
#include "sst/elements/firefly/ctrlMsgCommReq.h"
#include "sst/elements/merlin/topology/dragonfly.h"
#include "sst/elements/firefly/nic.h"
#include "sst/elements/ember/mpi/motifs/embercommonvariables.h"

#define DEBUG_MINE 0

static SST::Firefly::CtrlMsg::MatchHdr* getMMMHdrFromEvent(SST::Merlin::internal_router_event* ev);
static SST::Firefly::FireflyNetworkEvent* getFFFromEvent(SST::Merlin::internal_router_event* ev);

SST::Firefly::FireflyNetworkEvent* SST::Merlin::getFF(internal_router_event* ev){
    SST::Interfaces::SimpleNetwork::Request* req = ev->inspectRequest();
    return dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(req->inspectPayload());
}


bool SST::Merlin::getTagAndCountFromMMMHdr(SST::Merlin::internal_router_event* ev, uint64_t& tag, uint32_t& count){
    SST::Firefly::CtrlMsg::MatchHdr* mmmHdr = getMMMHdrFromEvent(ev); 
    if(mmmHdr){
        tag = mmmHdr->tag;
        count = mmmHdr->count;

        return true;
    }else{
        return false;
    }
}

static bool checkLongMsgCtrl(SST::Firefly::FireflyNetworkEvent* ffevent) {
    if (ffevent->bufSize() == 19 || ffevent->bufSize() == 17) {
        char* buffer = ((char*) ffevent->bufPtr());
        unsigned char c = ((char*)buffer)[5] ;
        if (c == 0x01 or c == 0x02) {
            return true;
        } 
    } else {
        //printf("Sus %d\n", ffevent->bufSize());
    }
    return false;
}

bool SST::Merlin::is_control_packet(SST::Merlin::internal_router_event* ev) {
    SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
    if(!ffevent){
        return NULL;
    }
    char* buffer = ((char*) ffevent->bufPtr());
    if(!buffer){
        return NULL;
    }

    if (ev->is_ack) {
        return false;
    }

    if (checkLongMsgCtrl(ffevent)) {
        return true;
    }

    if (ffevent->bufSize() >= (sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr))) {
                SST::Firefly::CtrlMsg::MatchHdr* mmmHdr = (SST::Firefly::CtrlMsg::MatchHdr*) (buffer + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr));
        if (mmmHdr->tag == CONTROL_TAG_FULL || mmmHdr->tag == CONTROL_TAG_FULL_ALTERNATIVE) {
            ev->is_control = true;
            return true;
        }
        if (mmmHdr->tag == TAG && (ffevent->bufSize() == (sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr)))) {
            ev->is_control = true;
            return true;
        }
        return false;
    } else {
        return false;
    }
}

bool SST::Merlin::is_desired_payload(SST::Merlin::internal_router_event* ev) {
    SST::Firefly::FireflyNetworkEvent* ffevent = getFFFromEvent(ev);
    if(!ffevent){
        return NULL;
    }
    char* buffer = ((char*) ffevent->bufPtr());
    if(!buffer){
        return NULL;
    }

    int header_size = sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr) + sizeof(SST::Firefly::Nic::MsgHdr);
    // We check first 4 and last 4 bytes to see if there is a match
    for (int in = header_size; in < ffevent->bufSize(); in++) {
        if (buffer[in] != 'A') {
            return false;
        }
    }
    return true;
}

int SST::Merlin::getSizePkt(internal_router_event* ev){
    SST::Interfaces::SimpleNetwork::Request* req = ev->inspectRequest();
    SST::Firefly::FireflyNetworkEvent* event = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(req->inspectPayload());
    return event->calcPayloadSizeInBits() / 8;
}

bool SST::Merlin::setTagAndCountFromMMMHdr(SST::Merlin::internal_router_event* ev, uint64_t tag, uint32_t count){
    SST::Firefly::CtrlMsg::MatchHdr* mmmHdr = getMMMHdrFromEvent(ev); 
    SST::Firefly::FireflyNetworkEvent* ffevent = getFFFromEvent(ev);

    int header_size = sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr) + sizeof(SST::Firefly::Nic::MsgHdr);
    if (ffevent->bufSize() <= header_size) {
        return false;
    }

    if(mmmHdr){
        mmmHdr->tag = tag;
        //mmmHdr->count = mmmHdr->count; // Double check this later on 
        return true;
    }else{
        return false;
    }
}

using namespace SST::Merlin;
using namespace SST::Interfaces;
using namespace std;

int hr_router::num_routers = 0;
int hr_router::print_debug = 0;

// Helper functions used only in this file
static string trim(string str)
{
    // Find whitespace in front
    int front_index = 0;
    while ( isspace(str[front_index]) ) front_index++;

    // Find whitespace in back
    int back_index = str.length() - 1;
    while ( isspace(str[back_index]) ) back_index--;

    return str.substr(front_index,back_index-front_index+1);
}

static void split(string input, string delims, vector<string>& tokens) {
    if ( input.length() == 0 ) return;
    size_t start = 0;
    size_t stop = 0;;
    vector<string> ret;

    do {
        stop = input.find_first_of(delims,start);
        tokens.push_back(input.substr(start,stop-start));
        start = stop + 1;
    } while (stop != string::npos);

    for ( unsigned int i = 0; i < tokens.size(); i++ ) {
        tokens[i] = trim(tokens[i]);
    }
}

static std::string getLogicalGroupParam(const Params& params, Topology* topo, int port,
                                        std::string param, std::string default_val = "") {
    // Use topology object to get the group for the port
    std::string group = topo->getPortLogicalGroup(port);

    // Create fully qualified key name
    std::string key = param;
    key.append(std::string(":")).append(group);

    std::string value = params.find<std::string>(key);

    if ( value == "" ) {
        // Look for default value
        value = params.find<std::string>(param, default_val);
        if ( value == "" ) {
            // Abort
            merlin_abort.fatal(CALL_INFO, -1, "hr_router requires %s to be specified\n", param.c_str());
        }
    }
    return value;
}

static UnitAlgebra getLogicalGroupParamUA(const Params& params, Topology* topo, int port,
                                          std::string param, std::string default_val = "") {

    std::string value = getLogicalGroupParam(params,topo,port,param,default_val);

    UnitAlgebra ua(value);
    // If units were in Bytes, convert to bits
    if ( ua.hasUnits("B") || ua.hasUnits("B/s") ) {
        ua *= UnitAlgebra("8b/B");
    }

    return ua;
}

static void printBuffer(SST::Firefly::FireflyNetworkEvent* ffevent) {
    printf("\n");
    char* buffer = ((char*) ffevent->bufPtr());
    for (int i = 0; i < ffevent->bufSize(); i++) {
        unsigned char c = ((char*)buffer)[i] ;
        printf ("%02x ", c) ;
    }
    printf("\n");
}

// Start class functions
hr_router::~hr_router()
{
    printf("\nTotal Cycle - %d : %" PRIu64 "\n", id ,total_clocks);
    for (int i = 0; i < num_ports; i++) {
        printf("\nBusy Port - %d - %d : %" PRIu64 "\n", id, i, busy_clocks[i]);
    }
    if (max_active_flows > 1) {
        printf("\nRouter %d - Max Flows %d - Current Flows %d\n", id, max_active_flows, active_flows);
    }
    

    /*printf("\nTotal Altenrative Cycle - %d : %" PRIu64 "\n", id ,total_clocks_alternative);
    for (int i = 0; i < num_ports; i++) {
        printf("\nBusy Alternative Port - %d - %d : %" PRIu64 "\n", id, i, busy_clocks_alternative[i]);
    }

     printf("\nTotal Two Cycle - %d : %" PRIu64 "\n", id ,total_clocks_alternative);
    for (int i = 0; i < num_ports; i++) {
        printf("\nBusy Two Port - %d - %d : %" PRIu64 "\n", id, i, busy_clocks_alternative2[i]);
    }

    ("Final size is %d\n", ack_list.size());*/


    // Printf FCT 
    /*for (auto x : list_fct_start) {}
        if (list_fct_start[i] > 0) {
            printf("\nFCT %d %d - %ld %ld %ld - %d %d\n", packet_sent_fct[i], packet_ack_fct[i], list_fct_start[i], list_fct_stop[i], list_fct_stop[i] - list_fct_start[i], id, i); fflush(stdout);
        }
    }*/

    // Get list keys
    std::vector<std::string> key;
    for (auto& it: packet_sent_fct) {
        key.push_back(it.first);
    }

    for (int i = 0; i < key.size(); i++) {
        if (list_fct_start[key[i]] > 0 && packet_sent_fct[key[i]] > 1) {
            printf("\nFCT %s - %d %d - %ld %ld %ld - %d %d\n", key[i].c_str(), packet_sent_fct[key[i]], packet_ack_fct[key[i]], list_fct_start[key[i]], list_fct_stop[key[i]], list_fct_stop[key[i]] - list_fct_start[key[i]], id, i); fflush(stdout);
        }
    }

    for (int i = 0; i < key.size(); i++) {
        if (list_fct_start[key[i]] > 0 && packet_sent_fct[key[i]] > 1) {
            printf("\nFINAL BDW %d %d - %ld %ld %ld - %d %d\n", packet_sent_fct[key[i]], packet_ack_fct[key[i]], list_fct_start[key[i]], list_fct_stop[key[i]], list_fct_stop[key[i]] - list_fct_start[key[i]], id, i); fflush(stdout);
        }
    }
    
    /*for (int i = 0; i < list_fct_start.size(); i++) {
        if (list_fct_start[i] > 0) {
            printf("\nFCT %d %d - %ld %ld %ld - %d %d\n", packet_sent_fct[i], packet_ack_fct[i], list_fct_start[i], list_fct_stop[i], list_fct_stop[i] - list_fct_start[i], id, i); fflush(stdout);
        }
    }*/

    delete [] in_port_busy;
    delete [] out_port_busy;
    delete [] progress_vcs;
    delete [] busy_clocks;
    delete [] busy_clocks_alternative;
    delete [] busy_clocks_alternative2;
    delete [] port_utilization_time;

    for ( int i = 0 ; i < num_ports ; i++ ) {
        delete ports[i];
    }
    delete [] ports;

    delete topo;
    delete arb;
}

hr_router::hr_router(ComponentId_t cid, Params& params) :
    Router(cid),
    num_vcs(-1),
    output(Simulation::getSimulation()->getSimulationOutput())
{

    // Get the options for the router
    id = params.find<int>("id",-1);
    if ( id == -1 ) {
        merlin_abort.fatal(CALL_INFO, -1, "hr_router requires id to be specified\n");
    }

    num_ports = params.find<int>("num_ports",-1);
    if ( num_ports == -1 ) {
        merlin_abort.fatal(CALL_INFO, -1, "hr_router requires num_ports to be specified\n");
    }

    // Try to make it persistent
    //registerAsPrimaryComponent();
    //primaryComponentDoNotEndSim();

    // Get the number of VNs
    num_vns = params.find<int>("num_vns",2);
    vcs_per_vn.resize(num_vns);

    // Get the topology
    topo = (Topology*)loadUserSubComponent<SST::Merlin::Topology>
        ("topology", ComponentInfo::SHARE_NONE, num_ports, id, num_vns);

    if ( !topo ) {
        merlin_abort.fatal(CALL_INFO_LONG, 1, "hr_router requires topology to be specified in input file\n");
    }

    topo->getVCsPerVN(vcs_per_vn);
    printf("Num hosts is %d \n", topo->num_port_hosts);
    for (int i = 0; i < topo->num_port_hosts; i++) {
        draining_per_host.push_back(0);
    }
    num_vcs = 0;
    for ( int vcs : vcs_per_vn ) num_vcs += vcs;

    //printf("VCS -> %d\n",num_vcs);

    // Check to see if remap is on
    vn_remap_shm = params.find<std::string>("vn_remap_shm","");
    if ( vn_remap_shm != "" ) {
        // If I'm id 0, create the shared region
        std::vector<int> vec;
        params.find_array<int>("vn_remap",vec);
        if ( vec.size() == 0 ) {
            merlin_abort.fatal(CALL_INFO, 1, "if vn_remap_shm is specified, a map must be supplied using vn_remap\n");
        }
        vn_remap_shm_size = vec.size() * sizeof(int);
        if ( id == 0 ) {
            shared_array.initialize(vn_remap_shm, vn_remap_shm_size);
            for ( int i = 0; i < vec.size(); ++i ) {
                shared_array.write(i,vec[i]);
            }
            shared_array.publish();
        }
    }

    // Parse all the timing parameters

    // Flit size
    std::string flit_size_s = params.find<std::string>("flit_size");
    if ( flit_size_s == "" ) {
        merlin_abort.fatal(CALL_INFO, -1, "hr_router requires flit_size to be specified\n");
        abort();
    }
    UnitAlgebra flit_size(flit_size_s);

    if ( flit_size.hasUnits("B") ) {
        // Need to convert to bits per second
        flit_size *= UnitAlgebra("8b/B");
    }

    // Link BW default.  Can be overwritten using logical groups
    std::string link_bw_s = params.find<std::string>("link_bw");
    UnitAlgebra link_bw(link_bw_s);

    if ( link_bw.hasUnits("B/s") ) {
        // Need to convert to bits per second
        link_bw *= UnitAlgebra("8b/B");
    }

    // Cross bar bandwidth
    std::string xbar_bw_s = params.find<std::string>("xbar_bw");
    if ( xbar_bw_s == "" ) {
        merlin_abort.fatal(CALL_INFO, -1, "hr_router requires xbar_bw to be specified\n");
    }

    UnitAlgebra xbar_bw_ua(xbar_bw_s);
    if ( xbar_bw_ua.hasUnits("B/s") ) {
        // Need to convert to bits per second
        xbar_bw_ua *= UnitAlgebra("8b/B");
    }

    UnitAlgebra xbar_clock;
    xbar_clock = xbar_bw_ua / flit_size;

    //printf("Xbar bw is %d\n", xbar_bw_ua.getValue());

    std::string input_latency = params.find<std::string>("input_latency", "0ns");
    std::string output_latency = params.find<std::string>("output_latency", "0ns");


    // Create all the PortControl blocks
    ports = new PortInterface*[num_ports];

    std::string input_buf_size = params.find<std::string>("input_buf_size", "0");
    std::string output_buf_size = params.find<std::string>("output_buf_size", "0");


    // Naming convention is from point of view of the xbar.  So,
    // in_port_busy is >0 if someone is writing to that xbar port and
    // out_port_busy is >0 if that xbar port being read.
    in_port_busy = new int[num_ports];
    out_port_busy = new int[num_ports];
    busy_clocks = new uint64_t[num_ports];
    busy_clocks_alternative = new uint64_t[num_ports];
    busy_clocks_alternative2 = new uint64_t[num_ports];
    port_utilization_time = new uint64_t[num_ports];
    for (int i = 0; i < num_ports; i++) {
        busy_clocks[i] = 0;
        busy_clocks_alternative[i] = 0;
        busy_clocks_alternative2[i] = 0;
        port_utilization_time[i] = 0;
        //port_utilization[i] = new uint64_t[100];
    }

    topo->timestamp_flow_start = std::vector<long long int>(50000);

    progress_vcs = new int[num_ports];

    std::string inspector_config = params.find<std::string>("network_inspectors", "");
    split(inspector_config,",",inspector_names);

    bool oql_track_port = params.find<bool>("oql_track_port","false");
    bool oql_track_remote = params.find<bool>("oql_track_remote","false");

    oql_track_port = true;
    oql_track_remote = true;
    params.enableVerify(false);

    Params pc_params = params.get_scoped_params("portcontrol");

    pc_params.insert("flit_size", flit_size.toStringBestSI());
    if (pc_params.contains("network_inspectors")) pc_params.insert("network_inspectors", params.find<std::string>("network_inspectors", ""));
    pc_params.insert("oql_track_port", params.find<std::string>("oql_track_port","false"));
    pc_params.insert("oql_track_remote", params.find<std::string>("oql_track_remote","false"));

    for ( int i = 0; i < num_ports; i++ ) {
        in_port_busy[i] = 0;
        out_port_busy[i] = 0;
        progress_vcs[i] = -1;

        std::stringstream port_name;
        port_name << "port";
        port_name << i;

        // For each port, some default parameters can be overwritten
        // by logical group parameters (link_bw, input_buf_size,
        // output_buf_size, input_latency, output_latency).

        pc_params.insert("port_name", port_name.str());
        pc_params.insert("link_bw", getLogicalGroupParam(params,topo,i,"link_bw") );
        pc_params.insert("input_latency", getLogicalGroupParam(params,topo,i,"input_latency","0ns"));
        pc_params.insert("output_latency", getLogicalGroupParam(params,topo,i,"output_latency","0ns"));
        pc_params.insert("input_buf_size", getLogicalGroupParam(params,topo,i,"input_buf_size"));
        pc_params.insert("output_buf_size", getLogicalGroupParam(params,topo,i,"output_buf_size"));
        pc_params.insert("dlink_thresh", getLogicalGroupParam(params,topo,i,"dlink_thresh", "-1"));
        pc_params.insert("vn_remap_shm", vn_remap_shm);
        pc_params.insert("vn_remap_shm_size", std::to_string(vn_remap_shm_size));
        pc_params.insert("num_vns", std::to_string(num_vns));

        ports[i] = loadAnonymousSubComponent<PortInterface>
            ("merlin.portcontrol","portcontrol", i, ComponentInfo::SHARE_PORTS | ComponentInfo::SHARE_STATS | ComponentInfo::INSERT_STATS,
             pc_params,this,id,i,topo);

    }
    params.enableVerify(true);

    // Get the Xbar arbitration
    std::string xbar_arb = params.find<std::string>("xbar_arb","merlin.xbar_arb_rr");
    xbar_arb = "merlin.xbar_arb_lru";

    Params empty_params; // Empty params sent to subcomponents
    arb =
        loadAnonymousSubComponent<XbarArbitration>(xbar_arb, "XbarArb", 0, ComponentInfo::INSERT_STATS, empty_params);

    my_clock_handler = new Clock::Handler<hr_router>(this,&hr_router::clock_handler);
    xbar_tc = registerClock( xbar_clock, my_clock_handler);
    num_routers++;

#if VERIFY_DECLOCKING
    clocking = true;
#endif

    // Check to make sure that the xbar BW is equal to or greater than
    // the link BW, otherwise the model runs into problems
    // if ( xbar_tc->getFactor() > link_tc->getFactor() ) {
    if ( xbar_bw_ua < link_bw  ) {
        merlin_abort.fatal(CALL_INFO_LONG,1,"ERROR: hr_router requires xbar_bw to be greater than or equal to link_bw\n"
              "  xbar_bw = %s, link_bw = %s\n",
              xbar_bw_ua.toStringBestSI().c_str(), link_bw.toStringBestSI().c_str());
    }
    // Register statistics
    xbar_stalls = new Statistic<uint64_t>*[num_ports];
    for ( int i = 0; i < num_ports; i++ ) {
        std::string port_name("port");
        port_name = port_name + std::to_string(i);
        xbar_stalls[i] = registerStatistic<uint64_t>("xbar_stalls",port_name);
    }

    init_vcs();

    // Ref RTT
    reference_rtt[1] = 1000;
    reference_rtt[2] = 2000;
    reference_rtt[3] = 3000;
    reference_rtt[4] = 4000;
    reference_rtt[5] = 5000;
}


void
hr_router::notifyEvent()
{
    setRequestNotifyOnEvent(false);

#if VERIFY_DECLOCKING
    clocking = true;
    Cycle_t next_cycle = getNextClockCycle( xbar_tc );
#else
    Cycle_t next_cycle = reregisterClock( xbar_tc, my_clock_handler);
#endif

    int64_t elapsed_cycles = next_cycle - unclocked_cycle;


#if !VERIFY_DECLOCKING
    // Fix up the busy variables
    for ( int i = 0; i < num_ports; i++ ) {
    	// Should stop at zero, need to find a clean way to do this
    	// with no branch.  For now it should work.
        int64_t tmp = in_port_busy[i] - elapsed_cycles;
    	if ( tmp < 0 ) in_port_busy[i] = 0;
        else in_port_busy[i] = tmp;
        tmp = out_port_busy[i] - elapsed_cycles;
    	if ( tmp < 0 ) out_port_busy[i] = 0;
        else {
            out_port_busy[i] = tmp;
        }
    }
#endif
    // Report skipped cycles to arbitration unit.
    arb->reportSkippedCycles(elapsed_cycles);
}

void
hr_router::sigHandler(int signal)
{
    print_debug = num_routers * 5;
}

void
hr_router::dumpState(std::ostream& stream)
{
    stream << "Router id: " << id << std::endl;
    for ( int i = 0; i < num_ports; i++ ) {
	ports[i]->dumpState(stream);
	stream << "  Output_busy: " << out_port_busy[i] << std::endl;
	stream << "  Input_Busy: " <<  in_port_busy[i] << std::endl;
    }

}

void
hr_router::printStatus(Output& out)
{
    out.output("Start Router:  id = %d\n", id);
    for ( int i = 0; i < num_ports; i++ ) {
        ports[i]->printStatus(out, out_port_busy[i], in_port_busy[i]);
    }
    out.output("End Router: id = %d\n", id);
}

bool is_control_tag(internal_router_event* ev) {
    SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
    if(!ffevent){
        return NULL;
    }
    char* buffer = ((char*) ffevent->bufPtr());
    if(!buffer){
        return NULL;
    }

    if (ev->is_ack) {
        return false;
    }

    if (checkLongMsgCtrl(ffevent)) {
        return true;
    }

    if (ffevent->bufSize() >= (sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr))) {
                SST::Firefly::CtrlMsg::MatchHdr* mmmHdr = (SST::Firefly::CtrlMsg::MatchHdr*) (buffer + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr));
        
        // Fix this, hack
        if (ffevent->bufSize() == 49 && mmmHdr->tag == 0x0) {
            return true;
        }
        
        if (mmmHdr->tag == CONTROL_TAG_FULL || mmmHdr->tag == CONTROL_TAG_FULL_ALTERNATIVE) {
            ev->is_control = true;
            return true;
        }
        if (mmmHdr->tag == TAG && (ffevent->bufSize() == (sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr)))) {
            ev->is_control = true;
            return true;
        }
        return false;
    } else {
        return false;
    }
}


bool is_control_tag2(internal_router_event* ev) {
    SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
    if(!ffevent){
        return NULL;
    }

    //printf("Size is %d %d %d", ev->getEncapsulatedEvent()->getSizeInBits() / 8, ffevent->bufSize(), ffevent->payloadSize());
    char* buffer = ((char*) ffevent->bufPtr());
    if(!buffer){
        return NULL;
    }

    if (ev->is_ack) {
        return false;
    }

    


    //printf("Size Tag %d", sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr)); fflush(stdout);
    if (ffevent->bufSize() >= (sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr))) {
                SST::Firefly::CtrlMsg::MatchHdr* mmmHdr = (SST::Firefly::CtrlMsg::MatchHdr*) (buffer + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr));
        if (mmmHdr->tag == CONTROL_TAG_FULL || mmmHdr->tag == CONTROL_TAG_FULL_ALTERNATIVE) {
            ev->is_control = true;
            return true;
        }
        if (mmmHdr->tag == TAG && (ffevent->bufSize() == (sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr)))) {
            ev->is_control = true;
            return true;
        }
        return false;
    } else {
        return false;
    }
}

bool is_background_traffic(internal_router_event* ev) {
    return false;
    /*SST::Firefly::FireflyNetworkEvent* ffevent = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());
    if(!ffevent){
        return NULL;
    }
    char* buffer = ((char*) ffevent->bufPtr());
    if(!buffer){
        return NULL;
    }

    int header_size = sizeof(SST::Firefly::CtrlMsg::MatchHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr) + sizeof(SST::Firefly::Nic::MsgHdr);
    if (ffevent->bufSize() > header_size) {
        for (int i = header_size; i < ffevent->bufSize(); i++) {
            if (buffer[i] != OTHER_MESSAGE) {
                return false;
            }
        }
        return true;
    } else {
        for (int i = 0; i < ffevent->bufSize(); i++) {
            if (buffer[i] != OTHER_MESSAGE) {
                return false;
            }
        }
        return true;
    }*/
}

bool isAck(internal_router_event* ev) {
    return ev->is_ack;
}

bool hr_router::needs_drain(internal_router_event* ev, std::string toHash) {
    //printf("Algo is %s\n", topo->routing_name.c_str());
    if (topo->routing_name != "slingshot"/* || id != 8*/) {
        return false;
    }
    //printf("Proceeding\n");
    //printf("Size Current Flowcut %d- %s \n", topo->size_flowcut[toHash], toHash.c_str());
    int draining_strategy = topo->flowcut_mode;
    //printf("Flowcut Mode %d - Flowcut Value %d \n", topo->flowcut_mode, topo->flowcut_value);

    switch(draining_strategy) {
        case 0: // MFD
            return topo->size_flowcut[toHash] > topo->flowcut_value;
        case 1: // MQL
            return output_queue_lengths[ev->getNextPort()] > 10;
        case 2: {// MPR
            if (latest_hop_count[toHash] < 1 || topo->size_flowcut[toHash] < 20000) {
                return false;
            }
            //printf("latest_hop_count[toHash] %d %s\n", latest_hop_count[toHash], toHash.c_str());
            float ratio = (double)exponential_avg[toHash] / min_latency[toHash];
            if (DEBUG_MINE) printf("Ratio is %f, Avg %ld\n", ratio, exponential_avg[toHash]);
            //return false;
            return (ratio > topo->flowcut_max_ratio);
        }
        case 3: { // MPRG
        if (latest_hop_count[toHash] < 1) {
                return false;
            }
            float ratio_gradient = latest_rtt[toHash] / exponential_avg[toHash];
            return (ratio_gradient > 10 || ratio_gradient < 0.1);
        }
        case 4: // MRM (Maximum Rate Mismatch)
            return true;
        case 5: // MRMG (Maximum Rate Mismatch Gradient)
            return false;
        case 6:
            return false;
        default:
            printf("Should never reach this, draining strategy option error\n");
            exit(0);
    }

}

bool
hr_router::clock_handler(Cycle_t cycle)
{
    // If there are no events in the input queues, then we can remove
    // ourselves from the clock queue, as long as the arbitration unit
    // says it's okay.

    //printf("Switch %d - Sent %d - Received %d \n",id, sent_packets, received_packets);
    //primaryComponentOKToEndSim();
    /*primaryComponentDoNotEndSim();
    if (sent_packets == 1) {
        
    }
    if ((sent_packets == received_packets)) {
        primaryComponentOKToEndSim();
    }*/

    /*if ( get_vcs_with_data() == 0 ) {
#if VERIFY_DECLOCKING
        if ( clocking ) {
            if ( arb->isOkayToPauseClock() ) {
                setRequestNotifyOnEvent(true);
                unclocked_cycle = cycle;
                clocking = false;
            }
        }
#else
        if ( arb->isOkayToPauseClock() ) {
            setRequestNotifyOnEvent(true);
            unclocked_cycle = cycle;
            return true;
        }
        else {
            return false;
        }

#endif
    }*/

    // All we need to do is arbitrate the crossbar
#if VERIFY_DECLOCKING
    arb->arbitrate(ports,in_port_busy,out_port_busy,progress_vcs,clocking);
#else
    arb->arbitrate(ports,in_port_busy,out_port_busy,progress_vcs);
#endif

    // Normal Count
    if ( get_vcs_with_data() != 0) {
        total_clocks_alternative++;
    }

    /*for ( int i = 0; i < num_ports; i++) {
        if ((total_clocks % SAMPLING_RATE_PORT_OCCUPANCY) == 0) {
            //printf("\nPort Utilization is %d %d %d\n", id, i, port_utilization_time[i]);
            port_utilization_time[i] = 0;
        }
        if (i >= topo->num_port_hosts) {
            if(out_port_busy[i] > 0) {
                busy_clocks[i]++;
                port_utilization_time[i]++;
                if ( get_vcs_with_data() != 0 ) {
                    busy_clocks_alternative[i]++;
                } 
            }
        } else {
            if(in_port_busy[i] > 0) {
                busy_clocks[i]++;
                port_utilization_time[i]++;
                if ( get_vcs_with_data() != 0 ) {
                    busy_clocks_alternative[i]++;
                } 
            }
        }
    }*/

    total_clocks++;

    // Create Array to check if we have already used that input port
    bool port_already_considered[num_ports]; 
    internal_router_event* ev_received[num_ports]; 
    std::fill_n(port_already_considered, num_ports, false);

    if (topo->ackMode) {
        // First for for ACK
        for ( int i = 0; i < num_ports; i++ ) {
            if ( progress_vcs[i] > -1 ) {
                internal_router_event* ev = ports[i]->recv(progress_vcs[i]); 
                ev_received[i] = ev;
                
                /*if (!isAck(ev)) {
                    printf("Data Switch %d - Size %d - Sending %d - From %d to %d\n", id, ev->getEncapsulatedEvent()->getSizeInBits() / 8 ,sent_packets, ev->getSrc(), ev->getDest());
                }*/

                // Check if the packet we want to send is an ACK or a DATA packet
                if (is_control_tag(ev)) {
                    //printf("Control\n");
                    continue;
                }

                if (isAck(ev)) { // Check if IS ACK
                    //printf("Ack Ack \n");
                    topo_dragonfly* topo_d = static_cast<topo_dragonfly*>(topo);
                    port_already_considered[i] = true;
                    int next_ack_port, previous_ack_port, next_vc;
                    
                    SST::Firefly::FireflyNetworkEvent* ff_temp = getFF(ev);

                    //printf("Router ID %d - ACK\n", id);
                    for (int i = 0; i < ack_list.size(); i++) {
                        //printf("Router %d - Wanted src %d, actual %d - Wanted Dest %d, actual dest %d\n", id, ack_list[i].packet_source,ev->getSrc(), ack_list[i].packet_dest,ev->getDest());
                        if (ack_list[i].packet_source == ev->getSrc() && ack_list[i].packet_dest == ev->getDest()/* && ack_list[i].msg_id == ff_temp->msg_id  && ack_list[i].packet_id_in_message == ff_temp->packet_id_in_message*/) {
                            next_ack_port = ack_list[i].next_port_ack;
                            next_vc = ack_list[i].vc;
                            previous_ack_port = ack_list[i].expected_previous_port;
                            ack_list.erase(ack_list.begin()+i);
                            break;
                        }
                    }
                    char* buffer = ((char*) ff_temp->bufPtr());
                    SST::Firefly::Nic::MsgHdr* mmmHdr = (SST::Firefly::Nic::MsgHdr*) (buffer);
                    int msg_id = ff_temp->msg_id;
                    std::string toHash = std::to_string(ev->getSrc()) + "@" + std::to_string(ev->getDest()) + "@" + std::to_string(msg_id);
                    //std::string toHash = std::to_string(ev->getSrc()) + "@" + std::to_string(ev->getDest());
                    //topo->list_ack_status[toHash].second++;
                    if ( topo->getPortState(next_ack_port) == Topology::R2N) {
                        //printf("Ack Switch %d - Size %d - Src %d - Dest %d - Origi %d\n", id, ev->getEncapsulatedEvent()->getSizeInBits() / 8 , ev->getSrc(), ev->getDest(), ff_temp->original_packet_size);
                        
                        //topo->list_ack_status[toHash].second++;
                        packet_ack_fct[toHash]++;
                        if (ff_temp->original_packet_size > 50) {
                            ff_temp->ingress_switch_ack_received = getCurrentSimTimeNano();
                            uint64_t diff = ff_temp->ingress_switch_ack_received - ff_temp->ingress_switch_sent;
                            uint64_t diffOnlySend = ff_temp->egress_switch_ack_sent - ff_temp->ingress_switch_sent;
                            
                            latest_hop_count[toHash] = ff_temp->hop_count_ingress;
                            uint64_t current_value;
                            if(exponential_avg.count(toHash) == 0) {
                                current_value = 0;
                                min_latency[toHash] = 99999999999;
                            } else {
                                current_value = exponential_avg[toHash];
                                if (diffOnlySend < min_latency[toHash]) {
                                    min_latency[toHash] = diffOnlySend;
                                }
                            }
                            // Exp Avg Formula, check alpha later for tuning
                            exponential_avg[toHash] = (topo->exponential_alpha * diffOnlySend) + ((1 - topo->exponential_alpha) * current_value);
                            
                            if (DEBUG_MINE) printf("Latest hop count %s@%d - Hop %d - RTT %ld - Min %ld - Ratio %ld - Sent Time %ld - S %d R %d\n", toHash.c_str(), ff_temp->packet_id_in_message, ff_temp->hop_count_ingress, diff, min_latency[toHash], exponential_avg[toHash] / min_latency[toHash], ff_temp->egress_switch_ack_sent - ff_temp->ingress_switch_sent, topo->list_ack_status[toHash].first, topo->list_ack_status[toHash].second);
                            //printf("Ack Reached final node!, (%s) srcd %d dest %d, size %d, lat %" PRIu64  " %" PRIu64 " - hop %d - glo ID %d - orig %d - %d %d - %d\n", toHash.c_str(), ev->getSrc(), ev->getDest(), ev->getEncapsulatedEvent()->getSizeInBits() / 8, diff, exponential_avg[toHash], latest_hop_count[toHash], id, ff_temp->original_packet_size, topo->list_ack_status[toHash].first, topo->list_ack_status[toHash].second, ff_temp->msg_id); fflush(stdout);
                            list_fct_stop[toHash] = getCurrentSimTimeNano();

                            // Calculate ACK receival rate
                            // Exp Avg Formula, check alpha later for tuning
                            float bdw_recv = (float)ff_temp->original_packet_size / ((getCurrentSimTimeNano() - latest_egress_timestamp[toHash]));
                            exponential_avg_recv_rate[toHash] = (0.3 * bdw_recv) + ((1 - 0.3) * exponential_avg_recv_rate[toHash]);
                            latest_egress_timestamp[toHash] = getCurrentSimTimeNano();
                            //printf("ACK Bandwidth %f %f\n", bdw_recv, exponential_avg_recv_rate[toHash]);
                        }
                        
                        received_packets++;

                        if (topo->list_ack_status[toHash].first == topo->list_ack_status[toHash].second) {
                            if (ff_temp->packet_id_in_message > 1 && ff_temp->ingress_switch_id == id) {
                                if (DEBUG_MINE) printf("Flowcut Finished1  %ld - %lld\n",getCurrentSimTimeNano(), getCurrentSimTimeNano() - topo->timestamp_flow_start[msg_id]);
                            }
                            // Delete entry in table if flowcut does not have in-flight packets
                            topo->list_ack_status.erase(toHash);
                            topo->size_flowcut.erase(toHash);
                            exponential_avg.erase(toHash);
                            exponential_avg_recv_rate.erase(toHash);
                            exponential_avg_send_rate.erase(toHash);
                            active_flows--;
                            //printf("Deleting Stuff, Id %d - %s - %d \n", id, toHash.c_str(), topo->size_flowcut[toHash]);

                            // FINISHING THE CURRENT DRAIN, RESTARTING FLOW
                            if (draining_status_map[toHash] == true && ff_temp->ingress_switch_id == id && ff_temp->packet_id_in_message > 1) {
                                draining_status_map[toHash] = false;
                                SST::Firefly::FireflyNetworkEvent* ff = getFFFromEvent(ev);
                                internal_router_event* new_ev = ev->clone();
                                new_ev->setEncapsulatedEvent(ev->getEncapsulatedEvent()->clone());   
                                SST::Firefly::FireflyNetworkEvent* ffCopy = getFFFromEvent(new_ev);
                                int copyBufSize = 8;
                                ffCopy->setBufAck(copyBufSize);
                                ffCopy->index_msg = ff->index_msg;
                                new_ev->inspectRequest()->size_in_bits = copyBufSize * 8;
                                ffCopy->drain_stop = true;
                                ffCopy->msg_id = ff->msg_id;
                                ffCopy->original_destination = ev->getDest();
                                ffCopy->original_source = ev->getSrc();
                                ffCopy->packet_id_in_message = ff->packet_id_in_message;
                                new_ev->control_drain = true;
                                new_ev->getEncapsulatedEvent()->computeSizeInFlits(64);
                                //printf("Drain Control - Start - ID %d - %s - Port %d\n",id, toHash.c_str(), next_ack_port); fflush(stdout);
                                if (DEBUG_MINE) printf("Drain Control - Finishing a Drain - %s@%d - ID %d - Port %d\n", toHash.c_str(), ff->packet_id_in_message, id, i); fflush(stdout);                       
                                ports[next_ack_port]->send(new_ev,0);   
                            }
                        }


                    } else if (topo->getPortState(next_ack_port) == Topology::R2R) {
                        // Forward ACK
                        //topo->list_ack_status[toHash].second++;

                        if (topo->list_ack_status[toHash].first == topo->list_ack_status[toHash].second) {
                            if (ff_temp->packet_id_in_message > 1 && ff_temp->ingress_switch_id == id) {
                                if (DEBUG_MINE) printf("Flowcut Finished2  %ld - %ld\n",getCurrentSimTimeNano(), getCurrentSimTimeNano() - topo->timestamp_flow_start[msg_id]);

                            }
                            // Delete entry in table if flowcut does not have in-flight packets
                            topo->list_ack_status.erase(toHash);
                            topo->size_flowcut.erase(toHash);
                            exponential_avg.erase(toHash);
                            exponential_avg_recv_rate.erase(toHash);
                            exponential_avg_send_rate.erase(toHash);
                            active_flows--;
                        }

                        ev->setNextPort(next_ack_port);
                        ports[next_ack_port]->send(ev,0);

                        /*if ( in_port_busy[i] != 0 ) in_port_busy[i]--;
                        if ( out_port_busy[i] != 0 ) out_port_busy[i]--;*/
                    }
                // Data packet processing, not ACK
                } else { 
                    topo_dragonfly* topo_d = static_cast<topo_dragonfly*>(topo);
                    SST::Firefly::FireflyNetworkEvent* ffff = getFFFromEvent(ev);
                    ffff->original_source = ev->getSrc();
                    ffff->original_destination = ev->getDest();
                    //printf("Router ID %d - DATA - MsgID %d %d\n", id, ffff->msg_id, ffff->packet_id_in_message);
                    
                    SST::Firefly::FireflyNetworkEvent* ff_temp = getFFFromEvent(ev);
                    char* buffer = ((char*) ff_temp->bufPtr());
                    SST::Firefly::Nic::MsgHdr* mmmHdr = (SST::Firefly::Nic::MsgHdr*) (buffer);
                    int msg_id = ff_temp->msg_id;
                    //printf("value is %d\n", msg_id);
                    std::string toHash = std::to_string(ev->getSrc()) + "@" + std::to_string(ev->getDest()) + "@" + std::to_string(msg_id);
                    
                    // Check if there is already an active flowcut for this 
                    if(topo->list_ack_status.count(toHash) == 0 && topo->getPortState(ev->getNextPort()) != Topology::R2N) {
                        active_flows++;
                        if (active_flows > max_active_flows) {
                            max_active_flows = active_flows;
                        }
                    }

                    if (DEBUG_MINE) printf("Flow ID %s@%d - S %d R %d - Router %d\n", toHash.c_str(), ffff->packet_id_in_message,topo->list_ack_status[toHash].first, topo->list_ack_status[toHash].second, id);

                    // If Ingress switch
                    //list_fct_start_size[toHash] += ffff->bufSize();
                    if (topo->getPortState(i) == Topology::R2N) {  

                        ev->ingress_time = getCurrentSimTimeNano();
                        sent_packets++;
                        //printf("Ingress Switch %d - Size %d - Pkt ID %d - Msg ID %d - IDM %d - From %d to %d\n", id, ev->getEncapsulatedEvent()->getSizeInBits() / 8, ffff->packet_id, ffff->msg_id, ffff->packet_id_in_message, ev->getSrc(), ev->getDest());
                        // Check if we are first packet of new Flow, if yes set timestamp
                        if (ffff->packet_id_in_message == 0) {
                            topo->timestamp_flow_start[ffff->msg_id] = getCurrentSimTimeNano();
                            //printf("ID %d - Msg %d - Flow start time %ld\n", id, ffff->msg_id, getCurrentSimTimeNano());
                            list_fct_start[toHash] = getCurrentSimTimeNano();
                            //list_fct_data[toHash].time_start = getCurrentSimTimeNano();
                        }
                        ffff->ingress_switch_id = id;
                        ffff->ingress_switch_sent = getCurrentSimTimeNano();

                        // Exp Avg Formula, check alpha later for tuning
                        float bdw = (float)ffff->bufSize() / ((getCurrentSimTimeNano() - latest_ingress_timestamp[toHash]));
                        exponential_avg_send_rate[toHash] = (0.3 * bdw) + ((1 - 0.3) * exponential_avg_send_rate[toHash]);
                        latest_ingress_timestamp[toHash] = getCurrentSimTimeNano();
                        //"Current Bandwidth %f %f\n", bdw, exponential_avg_send_rate[toHash]);

                    }

                    if (topo->getPortState(ev->getNextPort()) == Topology::R2N) {
                        // Print Num Hops
                        ev->setNumHops(ev->getNumHops() + 1);
                    } else {
                        ev->setNumHops(ev->getNumHops() + 1);
                        ffff->hop_count_ingress++;
                    }
                    
                    if (topo->size_flowcut[toHash] > 0) {
                        topo->size_flowcut[toHash] += ff_temp->bufSize();
                    } else {
                        topo->size_flowcut[toHash] = ff_temp->bufSize();
                    }
                    //std::string toHash = std::to_string(ev->getSrc()) + "@" + std::to_string(ev->getDest());
                    
                    //if ((topo->getPortState(ev->getNextPort()) != Topology::R2N) || (topo->getPortState(i) != Topology::R2N)) { // if the packet has Src and Dest in the same switch
                        
                    if (topo->list_ack_status.find(toHash) == topo->list_ack_status.end()) {
                        // We create the pair, Src Dest for this router if it doesn't exist yet
                        if (topo->getPortState(ev->getNextPort()) == Topology::R2R) {
                            //topo->list_ack_status[toHash] = std::make_pair(1,0);
                            packet_sent_fct[toHash]++;
                        } else {
                            //topo->list_ack_status[toHash] = std::make_pair(1,1);
                            packet_sent_fct[toHash]++;
                            packet_ack_fct[toHash]++;
                        }
                    } else {
                        // Increase number of packets sent, we are waiting for matching ACK
                        if (topo->getPortState(ev->getNextPort()) == Topology::R2R) {
                            //topo->list_ack_status[toHash].first++;
                            if (DEBUG_MINE) printf("Increasing S %s@%d to %d\n",toHash.c_str(), ffff->packet_id_in_message, topo->list_ack_status[toHash].first);
                            packet_sent_fct[toHash]++;
                        } else if (topo->getPortState(ev->getNextPort()) == Topology::R2N){
                            //topo->list_ack_status[toHash].first++;
                            //topo->list_ack_status[toHash].second++;
                            packet_sent_fct[toHash]++;
                            packet_ack_fct[toHash]++;
                        }
                    } 
                    //printf("Final node!, srcd %d dest %d, size %d, routerAg %d - %d - glo ID %d - orig %d - %d %d - MsgID %d\n", ev->getSrc(), ev->getDest(), ev->getEncapsulatedEvent()->getSizeInBits() / 8, topo_d->router_id, topo_d->group_id, id, ff_temp->original_packet_size, topo->list_ack_status[toHash].first, topo->list_ack_status[toHash].second, ff_temp->msg_id); fflush(stdout);
                    //}

                    // Checking Draining. First check if applicable, then what strategy to use and finally execute it.
                    if ( topo->getPortState(i) == Topology::R2N && topo->getPortState(ev->getNextPort()) != Topology::R2N) {
                        //printf("Size Current Flowcut2 %d - %s@%d - rtr %d - needs_drain %d - port %d - size host %d - is_draining %d  \n", topo->size_flowcut[toHash], toHash.c_str(), ffff->packet_id_in_message ,id,  needs_drain(ev, toHash), i, topo->num_port_hosts, draining_per_host[i]);
                        //printf("Latest2 hop count %d - %s\n", ff_temp->hop_count_ingress, toHash.c_str());
                        if (draining_status_map[toHash] == false && needs_drain(ev, toHash)) {
                            draining_status_map[toHash] = true;
                            SST::Firefly::FireflyNetworkEvent* ff = getFFFromEvent(ev);
                            internal_router_event* new_ev = ev->clone();
                            new_ev->setEncapsulatedEvent(ev->getEncapsulatedEvent()->clone());   
                            SST::Firefly::FireflyNetworkEvent* ffCopy = getFFFromEvent(new_ev);
                            int copyBufSize = 8;
                            ffCopy->setBufAck(copyBufSize);
                            ffCopy->index_msg = ff->index_msg;
                            new_ev->inspectRequest()->size_in_bits = copyBufSize * 8;
                            ffCopy->msg_id = ff->msg_id;
                            ffCopy->is_drain_control = true;
                            new_ev->control_drain = true;
                            ffCopy->packet_id_in_message = ff->packet_id_in_message;
                            ffCopy->original_destination = ev->getDest();
                            ffCopy->original_source = ev->getSrc();
                            new_ev->getEncapsulatedEvent()->computeSizeInFlits(64);

                            // Try Setting new stuff here
                            //new_ev->inspectRequest()->setTraceID();
                            //new_ev->set


                            ports[i]->send(new_ev,0); 
                            if (DEBUG_MINE) printf("Drain Control - Starting a Drain - %s@%d - ID %d - Port %d\n", toHash.c_str(), ff->packet_id_in_message, id, i); fflush(stdout);                       
                            
                        }  
                    }

                    // We are at the last router, let's create the ACK and start sending it back
                    if ( topo->getPortState(ev->getNextPort()) == Topology::R2N) {
                        // Check ID MSG

                        SST::Firefly::FireflyNetworkEvent* ff = getFFFromEvent(ev);
                        //printf("Packett -> %ld\n", ev->egress_time - ev->ingress_time);
                        //printf("\n\nTiming (%s) Rou %d - Msg %d - id %d - size %d - start %ld - stop %ld - diff %ld %ld\n", toHash.c_str(), id, ffff->msg_id, ffff->packet_id_in_message, ffff->bufSize(), ffff->ingress_switch_sent, getCurrentSimTimeNano(), getCurrentSimTimeNano() - ffff->ingress_switch_sent, getCurrentSimTimeNano() - ffff->ingress_switch_sent_alt);

                        // If packet SRC adn DEST is withing the same switch then we can just ignore it for ACKs.
                        if ((topo->getPortState(ev->getNextPort()) == Topology::R2N) && (topo->getPortState(i) == Topology::R2N)) { // if the packet has Src and Dest in the same switch
                            //printf("EDGE CASE, src %d, dest %d, size %d, hops %d\n", ev->getSrc(), ev->getDest(), ff->bufSize(), ev->getNumHops());
                            //topo->list_ack_status[toHash].second++;
                            ff->is_data_packet = true;
                            continue;
                        }

                        //printf("Sending back ACK\n"); fflush(stdout);
                        // Clone Data packet Event, fill ACK packet, send it back
                        ff->is_data_packet = true;
                        //printf("I am a Data, preparing ACK 4\n"); fflush(stdout);
                        internal_router_event* new_ev = ev->clone();
                        size_t copyBufSize = 0;
                        //printf("I am a Data, preparing ACK 3\n"); fflush(stdout);
                        //printf("Before changing len ev: %ld -- len clone %ld\n", ev->getEncapsulatedEvent()->getSizeInBits(), new_ev->getEncapsulatedEvent()->getSizeInBits()); fflush(stdout);
                        
                        new_ev->setEncapsulatedEvent(ev->getEncapsulatedEvent()->clone());   
                        SST::Firefly::FireflyNetworkEvent* ffCopy = getFFFromEvent(new_ev);
                        //printf("Before1 changing len ev: %ld -- len clone %ld\n", ff->bufSize(),  ffCopy->bufSize()); fflush(stdout);
                        copyBufSize = 8;
                        //printf("I am a Data, preparing ACK 5\n"); fflush(stdout);
                        //printf("Middle changing len ev: %ld -- len clone %ld\n", ev->getEncapsulatedEvent()->getSizeInBits(), new_ev->getEncapsulatedEvent()->getSizeInBits()); fflush(stdout);
                        new_ev->inspectRequest()->size_in_bits = 10;
                        //printf("After changing len ev: %ld -- len clone %ld\n", ev->getEncapsulatedEvent()->getSizeInBits(), new_ev->getEncapsulatedEvent()->getSizeInBits()); fflush(stdout);
                        //char* copyBuf = (char*) malloc(copyBufSize);
                        //memcpy((char*) copyBuf, (char*) ff->bufPtr(), copyBufSize);
                        //memset( copyBuf, ACK_MSG, copyBufSize );
                        //printf("I am a Data, preparing ACK 6\n"); fflush(stdout);
                        // Overwrite Firefly buffer
                        ffCopy->setBufAck(4);
                        ffCopy->index_msg = ff->index_msg;
                        ffCopy->original_packet_size = ev->getEncapsulatedEvent()->getSizeInBits() / 8;
                        ffCopy->msg_id = ff->msg_id;
                        ffCopy->packet_id_in_message = ff->packet_id_in_message;
                        ffCopy->packet_id = ff->packet_id;
                        ffCopy->ingress_switch_id = ff->ingress_switch_id;
                        ffCopy->ingress_switch_sent = ff->ingress_switch_sent;
                        ffCopy->egress_switch_ack_sent = getCurrentSimTimeNano();
                        ffCopy->hop_count_ingress = ff->hop_count_ingress;

                        if (DEBUG_MINE) printf("Creating ACK %d@%d@%d@%d - Time %ld - S %d R %d - Router %d\n", ff->original_source, ff->original_destination, ff->msg_id, ff->packet_id_in_message, getCurrentSimTimeNano(), topo->list_ack_status[toHash].first, topo->list_ack_status[toHash].second, id);

                        //ffCopy->bufAppend(copyBuf, copyBufSize);                    
                        new_ev->inspectRequest()->size_in_bits = 8 * 8;
                        new_ev->is_ack = true;
                        new_ev->getEncapsulatedEvent()->computeSizeInFlits(64);
                        //int size_ev = (int)(copyBufSize * 8);
                        //printf("ACKR2N - Src %d - Dest %d - Data Size %d - I am router %d (G %d - ID %d), size %d \n", ev->getSrc(), ev->getDest(), ev->getEncapsulatedEvent()->getSizeInBits() / 8 ,id, topo_d->group_id, topo_d->router_id, int(new_ev->getEncapsulatedEvent()->getSizeInBits() / 8)); fflush(stdout);
                        new_ev->setNextPort(i);
                        ports[i]->send(new_ev,0);   
                        //topo->list_ack_status[toHash].second++;
                        //printf("Second\n");
                        //printf("Msg id %d - si %d\n", ff_temp->index_msg, ff_temp->bufSize());
                        //printf("Reached last router %d %d %d\n", id, new_ev->getFlitCount(), new_ev->getEncapsulatedEvent()->getSizeInFlits());
                        /*if ( in_port_busy[i] != 0 ) in_port_busy[i]--;
                        if ( out_port_busy[i] != 0 ) out_port_busy[i]--;*/
                    } else if (topo->getPortState(ev->getNextPort()) == Topology::R2R) {
                        SST::Firefly::FireflyNetworkEvent* fftemp = getFFFromEvent(ev);
                        ack_list.push_back(AckInfo(ev->getSrc(),ev->getDest(),ev->getNextPort(),i,ev->clone(),fftemp->msg_id,fftemp->packet_id_in_message, ev->getVC()));                      
                    }
                }
            }
            else if ( progress_vcs[i] == -2 ) {
                busy_clocks_alternative2[i]++;
                xbar_stalls[i]->addData(1);
            }

            // Should stop at zero, need to find a clean way to do this
            // with no branch.  For now it should work.
            //if (port_already_considered[i] == true) {
            //}
            
        }
    }
    
    // Move the events and decrement the busy values
    for ( int i = 0; i < num_ports; i++ ) {
        // If not already done above
        if ( progress_vcs[i] > -1 ) {
            internal_router_event* ev;
            if (port_already_considered[i] && topo->ackMode) {
                continue;
            } else if (!topo->ackMode) {
                ev = ports[i]->recv(progress_vcs[i]);
                SST::Firefly::FireflyNetworkEvent* ff = getFFFromEvent(ev);

                if (!is_control_tag(ev) && !is_background_traffic(ev)) {

                    ff->is_data_packet = true;
                    ff->original_source = ev->getSrc();
                    ff->original_destination = ev->getDest();
                    if (topo->getPortState(ev->getNextPort()) == Topology::R2N) {
                        // Print Num Hops
                        ev->setNumHops(ev->getNumHops() + 1);
                        //printf("\nNum Hops: %d\n", ev->getNumHops()); fflush(stdout);
                    } else {
                        ev->setNumHops(ev->getNumHops() + 1);
                    }

                } else if (is_background_traffic(ev)) {
                    ff->is_bg_traffic = true;
                }
            } else if (!port_already_considered[i] && topo->ackMode) {
                ev = ev_received[i];
            } else {
                printf("Should never reach this point");
            }
            
            

            SST::Firefly::FireflyNetworkEvent* ffff = dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(ev->inspectRequest()->inspectPayload());

            ev->router_hops++;
            ev->visited_routers.push_back(id);
            if (ev->intermediate_latencies.size() == 0) {
                ev->intermediate_latencies.push_back(getCurrentSimTimeNano());
            } else {
                ev->intermediate_latencies.push_back(getCurrentSimTimeNano());
            }
            
            if ( topo->getPortState(i) == Topology::R2N) {
                ev->ingress_time = getCurrentSimTimeNano();
            }
            
            if ( topo->getPortState(ev->getNextPort()) == Topology::R2N) {
                ev->egress_time = getCurrentSimTimeNano();
                if (ev->getEncapsulatedEvent()->getSizeInBits() / 8 > 50) { // Quick hack to avoid control packets
                    std::stringstream result;
                    std::copy(ev->visited_routers.begin(), ev->visited_routers.end(), std::ostream_iterator<int>(result, " "));
                    //printf("Packet Latency -> %ld (Hops %d - %s) - Current RtrID %d - From/to %d@%d@%d@%d\n", ev->egress_time - ev->ingress_time, ev->router_hops, result.str().c_str(), id, ev->getSrc(), ev->getDest(), ffff->msg_id, ffff->packet_id_in_message);
                    if (ev->egress_time - ev->ingress_time > 147686) {
                        std::stringstream result2;
                        std::copy(ev->intermediate_latencies.begin(), ev->intermediate_latencies.end(), std::ostream_iterator<uint64_t>(result2, " "));
                        //printf("Packet Alert Latency -> %ld (%s) - (Hops %d - %s) - Current RtrID %d - From/to %d@%d@%d@%d\n", ev->egress_time - ev->ingress_time, result2.str().c_str(), ev->router_hops, result.str().c_str(), id, ev->getSrc(), ev->getDest(), ffff->msg_id, ffff->packet_id_in_message);
                    }
                }
            }
            
            ports[ev->getNextPort()]->send(ev,ev->getVC());

            if ( ev->getTraceType() == SimpleNetwork::Request::FULL ) {
                output.output("TRACE(%d): %" PRIu64 " ns: Copying event (src = %d, dest = %d) "
                              "over crossbar in router %d (%s) from port %d, VC %d to port"
                              " %d, VC %d.\n",
                              ev->getTraceID(),
                              getCurrentSimTimeNano(),
                              ev->getSrc(),
                              ev->getDest(),
                              id,
                              getName().c_str(),
                              i,
                              progress_vcs[i] ,
                              ev->getNextPort(),
                              ev->getVC());
            }
        }
        else if ( progress_vcs[i] == -2 ) {
            busy_clocks_alternative2[i]++;
            xbar_stalls[i]->addData(1);
        } 
        // Should stop at zero, need to find a clean way to do this
        // with no branch.  For now it should work.
        //if (port_already_considered[i] == false) {
        if ( in_port_busy[i] != 0 ) in_port_busy[i]--;
        if ( out_port_busy[i] != 0 ) out_port_busy[i]--;
        //}
    }


    return false;
}


void hr_router::setup()
{
    for ( int i = 0; i < num_ports; i++ ) {
    	ports[i]->setup();
    }
}

void hr_router::finish()
{
    for ( int i = 0; i < num_ports; i++ ) {
    	ports[i]->finish();
    }

}

void
hr_router::init(unsigned int phase)
{
    for ( int i = 0; i < num_ports; i++ ) {
        ports[i]->init(phase);
        Event *ev = NULL;
        while ( (ev = ports[i]->recvInitData()) != NULL ) {
            internal_router_event *ire = dynamic_cast<internal_router_event*>(ev);
            if ( ire == NULL ) {
                ire = topo->process_InitData_input(static_cast<RtrEvent*>(ev));
            }
            std::vector<int> outPorts;
            topo->routeInitData(i, ire, outPorts);
            for ( std::vector<int>::iterator j = outPorts.begin() ; j != outPorts.end() ; ++j ) {
                /* Little tricky here.  Need to clone both the event, and the
                 * encapsulated event.
                 */
                switch ( topo->getPortState(*j) ) {
                case Topology::R2N:
                    ports[*j]->sendUntimedData(ire->getEncapsulatedEvent()->clone());
                    break;
                case Topology::R2R:
                // Ignore failed links during init
                case Topology::FAILED: {
                    internal_router_event *new_ire = ire->clone();
                    new_ire->setEncapsulatedEvent(ire->getEncapsulatedEvent()->clone());
                    ports[*j]->sendUntimedData(new_ire);
                    break;
                }
                default:
                    break;
                }
            }
            delete ire;
        }
    }


    // Always do the above.  A few specific things to do during init

    // After phase 1, all the PortControl blocks will have reported
    // the requested VNs.  Now we need to translate this to the number
    // of VCs needed.
    // if ( phase == 1 ) {
    //     num_vcs = topo->computeNumVCs(requested_vns);
    //     init_vcs();
    // }

}

void
hr_router::complete(unsigned int phase)
{
    for ( int i = 0; i < num_ports; i++ ) {
        ports[i]->complete(phase);
        Event *ev = NULL;
        while ( (ev = ports[i]->recvInitData()) != NULL ) {
            internal_router_event *ire = dynamic_cast<internal_router_event*>(ev);
            if ( ire == NULL ) {
                ire = topo->process_InitData_input(static_cast<RtrEvent*>(ev));
            }
            std::vector<int> outPorts;
            topo->routeInitData(i, ire, outPorts);
            for ( std::vector<int>::iterator j = outPorts.begin() ; j != outPorts.end() ; ++j ) {
                /* Little tricky here.  Need to clone both the event, and the
                 * encapsulated event.
                 */
                switch ( topo->getPortState(*j) ) {
                case Topology::R2N:
                    ports[*j]->sendUntimedData(ire->getEncapsulatedEvent()->clone());
                    break;
                case Topology::R2R:
                // Ignore failed links during init
                case Topology::FAILED: {
                    internal_router_event *new_ire = ire->clone();
                    new_ire->setEncapsulatedEvent(ire->getEncapsulatedEvent()->clone());
                    ports[*j]->sendUntimedData(new_ire);
                    break;
                }
                default:
                    break;
                }
            }
            delete ire;
        }
    }
}

void
hr_router::sendCtrlEvent(CtrlRtrEvent* ev, int port) {

    if ( port == -1 ) {
        // Need to route packet
        port = topo->routeControlPacket(ev);
    }

    if ( port >= num_ports ) {
        auto dest = ev->getDest();
    }
    // Event just gets forwarded to appropriate PortControl object
    ports[port]->sendCtrlEvent(ev);
}

void
hr_router::recvCtrlEvent(int port, CtrlRtrEvent* ev) {
    // Check to see what type of event it is
    switch ( ev->getCtrlType() ) {
    case CtrlRtrEvent::TOPOLOGY:
        // Event just gets sent on to topolgy object
        topo->recvTopologyEvent(port,static_cast<TopologyEvent*>(ev));
        break;
    default:
        // Route the ctrl event
        const auto& dest = ev->getDest();
        int port = topo->routeControlPacket(ev);
        if ( port == -1 ) {
            // Destined for this router
            if ( dest.addr_is_router ) {
                // Packet was sent to me, but I don't know what to do with
                // it
                fatal(CALL_INFO_LONG,-1,"ERROR: router %d received unknown ctrl event\n",id);
            }
            else {
                auto d = topo->getDeliveryPortForEndpointID(dest.addr);
                ports[d.second]->recvCtrlEvent(ev);
            }
        }
        else {
            int port = topo->routeControlPacket(ev);
            ports[port]->sendCtrlEvent(ev);
        }
        break;
    }
}


void
hr_router::init_vcs()
{
    vc_heads = new internal_router_event*[num_ports*num_vcs];
    xbar_in_credits = new int[num_ports*num_vcs*2];
    pending_credits = &(xbar_in_credits[num_ports*num_vcs]);
    output_queue_lengths = new int[num_ports*num_vcs];
    port_credits_out = new int[num_ports*num_vcs];
    for ( int i = 0; i < num_ports*num_vcs; i++ ) {
        vc_heads[i] = NULL;
        xbar_in_credits[i] = 0;
        output_queue_lengths[i] = 0;
        port_credits_out[i] = 0;
    }

    for ( int i = 0; i < num_ports*num_vcs*2; i++ ) {
        xbar_in_credits[i] = 0;
    }

    for ( int i = 0; i < num_ports; i++ ) {
        ports[i]->initVCs(num_vns,vcs_per_vn.data(),&vc_heads[i*num_vcs],&xbar_in_credits[i*num_vcs],&output_queue_lengths[i*num_vcs], pending_credits, &port_credits_out[i*num_vcs]);
    }

    topo->setOutputBufferCreditArray(xbar_in_credits, num_vcs);
    topo->setOutputQueueLengthsArray(output_queue_lengths, num_vcs);
    topo->setCreditBufferArray(port_credits_out, num_vcs);

    // Now that we have the number of VCs we can finish initializing
    // arbitration logic
    arb->setPorts(num_ports,num_vcs);


}

void
hr_router::reportIncomingEvent(internal_router_event* ev)
{
    // If this is destined for this router, let appropriate
    // PortControl know
    auto dest = topo->getDeliveryPortForEndpointID(ev->getDest());
    if ( dest.first == id ) {
        ports[dest.second]->reportIncomingEvent(ev);
    }
}

static SST::Firefly::FireflyNetworkEvent* getFFFromEvent(internal_router_event* ev){
    SST::Interfaces::SimpleNetwork::Request* req = ev->inspectRequest();
    return dynamic_cast<SST::Firefly::FireflyNetworkEvent*>(req->inspectPayload());
}

static SST::Firefly::CtrlMsg::MatchHdr* getMMMHdrFromEvent(internal_router_event* ev){   
    SST::Firefly::FireflyNetworkEvent* ffevent = getFFFromEvent(ev);
    if(!ffevent){
        return NULL;
    }
    char* buffer = ((char*) ffevent->bufPtr());
    /*printf("\nPayload Size %d, bufSize %ld", ffevent->payloadSize(), ffevent->bufSize());

    for (int in = 0; in < 512; in++) {
        uint8_t num = *((uint8_t*)buffer + in);
        printf(" -- %d Payload8 %d\n", in, num);
        uint32_t num1 = *((uint32_t*)buffer + in);
        printf(" -- %d Payload32 %d\n", in, num1);
        uint64_t num2 = *((uint64_t*)buffer + in);
        printf(" -- %d Payload64 %ld\n", in, num2);
    }

    for (int in = 0; in < ffevent->bufSize(); in++) {
        if (ffevent->bufSize() > 45) {
            printf(" -- %d Payload %c\n", in, buffer[in]);
        }
    }

    for (int i = 0; i < ffevent->bufSize(); i++) {
        if (ffevent->bufSize() > 45) {
            unsigned char c = ((char*)buffer)[i] ;
            printf ("%02x ", c) ;
        }
    }*/
    //printf("Size1 %d\n",  ffevent->payloadSize());

    if(!buffer){
        return NULL;
    }
    SST::Firefly::Nic::MsgHdr* mHdr = (SST::Firefly::Nic::MsgHdr*) buffer;
    if(mHdr->op != SST::Firefly::Nic::MsgHdr::Msg){
        return NULL;
    }

    SST::Firefly::Nic::MatchMsgHdr* mmHdr = (SST::Firefly::Nic::MatchMsgHdr*) (buffer + sizeof(SST::Firefly::Nic::MsgHdr));
    return (SST::Firefly::CtrlMsg::MatchHdr*) (buffer + sizeof(SST::Firefly::Nic::MsgHdr) + sizeof(SST::Firefly::Nic::MatchMsgHdr));   
}
