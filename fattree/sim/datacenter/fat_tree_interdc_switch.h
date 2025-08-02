// -*- c-basic-offset: 4; indent-tabs-mode: nil -*-
#ifndef _FATTREESWITCH_H_INTER
#define _FATTREESWITCH_H_INTER

#include "callback_pipe.h"
#include "switch.h"
#include <unordered_map>

class FatTreeInterDCTopology;

/*
 * Copyright (C) 2013-2014 Universita` di Pisa. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *   1. Redistributions of source code must retain the above copyright
 *      notice, this list of conditions and the following disclaimer.
 *   2. Redistributions in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

/*
 * Shamelessly copied from FreeBSD
 */

/* ----- FreeBSD if_bridge hash function ------- */

/*
 * The following hash function is adapted from "Hash Functions" by Bob Jenkins
 * ("Algorithm Alley", Dr. Dobbs Journal, September 1997).
 *
 * http://www.burtleburtle.net/bob/hash/spooky.html
 */

#define MIX(a, b, c)                                                                                                   \
    do {                                                                                                               \
        a -= b;                                                                                                        \
        a -= c;                                                                                                        \
        a ^= (c >> 13);                                                                                                \
        b -= c;                                                                                                        \
        b -= a;                                                                                                        \
        b ^= (a << 8);                                                                                                 \
        c -= a;                                                                                                        \
        c -= b;                                                                                                        \
        c ^= (b >> 13);                                                                                                \
        a -= b;                                                                                                        \
        a -= c;                                                                                                        \
        a ^= (c >> 12);                                                                                                \
        b -= c;                                                                                                        \
        b -= a;                                                                                                        \
        b ^= (a << 16);                                                                                                \
        c -= a;                                                                                                        \
        c -= b;                                                                                                        \
        c ^= (b >> 5);                                                                                                 \
        a -= b;                                                                                                        \
        a -= c;                                                                                                        \
        a ^= (c >> 3);                                                                                                 \
        b -= c;                                                                                                        \
        b -= a;                                                                                                        \
        b ^= (a << 10);                                                                                                \
        c -= a;                                                                                                        \
        c -= b;                                                                                                        \
        c ^= (b >> 15);                                                                                                \
    } while (/*CONSTCOND*/ 0)

#undef MIX

class FlowletInfoInterDC {
  public:
    uint32_t _egress;
    simtime_picosec _last;

    FlowletInfoInterDC(uint32_t egress, simtime_picosec lasttime) {
        _egress = egress;
        _last = lasttime;
    };
};

struct FlowInfo
{
    int in_flight_bytes   = 0;   // outstanding packets/bytes/… in flight
    int source_port = 0;   // TCP/UDP source port
    std::string source_name;
};


class FatTreeInterDCSwitch : public Switch {
  public:
    enum switch_type { NONE = 0, TOR = 1, AGG = 2, CORE = 3, BORDER = 4 };

    enum routing_strategy { NIX = 0, ECMP = 1, ADAPTIVE_ROUTING = 2, ECMP_ADAPTIVE = 3, RR = 4, RR_ECMP = 5 };

    enum sticky_choices { PER_PACKET = 0, PER_FLOWLET = 1 };

    FatTreeInterDCSwitch(EventList &eventlist, string s, switch_type t, uint32_t id, simtime_picosec switch_delay,
                         FatTreeInterDCTopology *ft, int);

    virtual void receivePacket(Packet &pkt);
    virtual Route *getNextHop(Packet &pkt, BaseQueue *ingress_port);
    virtual uint32_t getType() { return _type; }

    uint32_t adaptive_route(vector<FibEntry *> *ecmp_set, int8_t (*cmp)(FibEntry *, FibEntry *));
    uint32_t replace_worst_choice(vector<FibEntry *> *ecmp_set, int8_t (*cmp)(FibEntry *, FibEntry *),
                                  uint32_t my_choice);
    uint32_t adaptive_route_p2c(vector<FibEntry *> *ecmp_set, int8_t (*cmp)(FibEntry *, FibEntry *));

    static int8_t compare_pause(FibEntry *l, FibEntry *r);
    static int8_t compare_bandwidth(FibEntry *l, FibEntry *r);
    static int8_t compare_queuesize(FibEntry *l, FibEntry *r);
    static int8_t compare_pqb(FibEntry *l,
                              FibEntry *r);             // compare pause,queue, bw.
    static int8_t compare_pq(FibEntry *l, FibEntry *r); // compare pause, queue
    static int8_t compare_pb(FibEntry *l,
                             FibEntry *r); // compare pause, bandwidth
    static int8_t compare_qb(FibEntry *l,
                             FibEntry *r); // compare pause, bandwidth

    static int8_t (*fn)(FibEntry *, FibEntry *);

    virtual void addHostPort(int addr, int flowid, PacketSink *transport);

    virtual void permute_paths(vector<FibEntry *> *uproutes);

    static void set_strategy(routing_strategy s) {
        assert(_strategy == NIX);
        _strategy = s;
    }
    static void set_ar_fraction(uint16_t f) {
        assert(f >= 1);
        _ar_fraction = f;
    }

    static void set_precision_ts(int ts) { precision_ts = ts; }

    static routing_strategy _strategy;
    static uint16_t _ar_fraction;
    static uint16_t _ar_sticky;
    static simtime_picosec _sticky_delta;
    static double _ecn_threshold_fraction;
    static int precision_ts;
    static int flowcut_ratio;

  private:
    switch_type _type;
    Pipe *_pipe;
    FatTreeInterDCTopology *_ft;

    vector<pair<simtime_picosec, uint64_t>> _list_sent;

    // CAREFUL: can't always have a single FIB for all up destinations when
    // there are failures!
    vector<FibEntry *> *_uproutes;

    unordered_map<uint32_t, FlowletInfoInterDC *> _flowlet_maps;
    uint32_t _crt_route;
    uint32_t _hash_salt;
    simtime_picosec _last_choice;

    unordered_map<Packet *, bool> _packets;

    std::unordered_map<std::string, FlowInfo> _flowcut_table;
    std::unordered_map<std::string, simtime_picosec> _base_rtt_table;
    string getPreviousName(const std::string& key);
    void increaseFlowInFlight(const std::string& key, int port, std::string source_name, int increase_size);
    void decreaseFlowInFlight(const std::string& key, int port, std::string source_name, int decrease_size, simtime_picosec ts);
    bool checkRTTFlowcut(simtime_picosec ts, simtime_picosec base_rtt);
    void printfInfoFlowcutTable(bool is_increase, const Packet &pkt) {
        // Print the flowcut table for debugging purposes
        // This is useful to see how the flowcut table changes
        // when packets are sent or acknowledged.

        // Print the action taken (increase/decrease) and the current state of the table
      std::string action = is_increase ? "increased" : "decreased";
        //printf("I am Switch %s - Previous Hop %d vs Current %d (%s vs %s) - Flowcut Table (%d) :\n", _name.c_str(), pkt.previous_switch_id, _id, pkt.previous_switch_name.c_str(), _name.c_str(), _flowcut_table.size());
        for (const auto& [key, info] : _flowcut_table) {
            //printf("Flow %s: in_flight_bytes=%d, source_port=%d, action=%s\n", key.c_str(), info.in_flight_bytes, info.source_port, action.c_str());
        }
    }
};

#endif
