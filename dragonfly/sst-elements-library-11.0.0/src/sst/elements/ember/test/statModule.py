import sst

def init( outputFile ):

	sst.setStatisticLoadLevel(9)

	sst.setStatisticOutput("sst.statOutputCSV")
	sst.setStatisticOutputOptions({
    	"filepath" : outputFile,
    	"separator" : ", "
	})

	'''STATISTIC 0 = send_bit_count [Count number of bits sent on link] (bits) Enable level = 1
	STATISTIC 1 = send_packet_count [Count number of packets sent on link] (packets) Enable level = 1
	STATISTIC 2 = output_port_stalls [Time output port is stalled (in units of core timebase)] (time in stalls) Enable level = 1
	STATISTIC 3 = xbar_stalls [Count number of cycles the xbar is stalled] (cycles) Enable level = 1
	STATISTIC 4 = idle_time [Amount of time spent idle for a given port] (units of core timebase) Enable level = 1
	STATISTIC 5 = width_adj_count [Number of times that link width was increased or decreased] (width adjustment count) Enable level = 1'''


	sst.enableStatisticForComponentType("merlin.hr_router", 'send_packet_count', {"type":"sst.AccumulatorStatistic","rate":"0ns"})
	sst.enableStatisticForComponentType("merlin.hr_router", 'send_bit_count', {"type":"sst.AccumulatorStatistic","rate":"0ns"})
	sst.enableStatisticForComponentType("merlin.linkcontrol", 'packet_latency', {"type":"sst.HistogramStatistic","rate":"0ns"})
	#sst.enableStatisticForComponentType("firefly.nic",'mem_num_stores',{"type":"sst.AccumulatorStatistic","rate":"0ns"})
	#sst.enableStatisticForComponentType("firefly.nic",'mem_num_loads',{"type":"sst.AccumulatorStatistic","rate":"0ns"})

	sst.enableStatisticForComponentType("firefly.nic",'mem_addrs',
	{"type":"sst.HistogramStatistic",
		"rate":"0ns",
		"binwidth":"4096",
		"numbins":"512"}
	)
