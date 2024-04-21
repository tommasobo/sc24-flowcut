debug = 0

netConfig = {
}


networkParams = {
    "packetSize" : "2048B",
    "link_bw" : "200Gb/s",
    "xbar_bw" : "200Gb/s",
    "link_lat" : "200ns",
    "input_latency" : "20ns",
    "output_latency" : "20ns",
    "flitSize" : "64B",
    "input_buf_size" : "128KB",
    "output_buf_size" : "128KB",
}

nicParams = {
	"detailedCompute.name" : "thornhill.SingleThread",
    "module" : "merlin.linkcontrol",
    "packetSize" : networkParams['packetSize'],
    "link_bw" : networkParams['link_bw'],
    "input_buf_size" : networkParams['input_buf_size'],
    "output_buf_size" : networkParams['output_buf_size'],
    "rxMatchDelay_ns" : 1,
    "txDelay_ns" : 1,
    "nic2host_lat" : "1ns",
    "useSimpleMemoryModel" : 0,
	"simpleMemoryModel.verboseLevel" : 0,
	"simpleMemoryModel.verboseMask" : -1,

	"simpleMemoryModel.memNumSlots" : 32,
	"simpleMemoryModel.memReadLat_ns" : 150, 
	"simpleMemoryModel.memWriteLat_ns" : 40, 

	"simpleMemoryModel.hostCacheUnitSize" : 32, 
	"simpleMemoryModel.hostCacheNumMSHR" : 32, 
	"simpleMemoryModel.hostCacheLineSize" : 64, 

	"simpleMemoryModel.widgetSlots" : 32, 

	"simpleMemoryModel.nicNumLoadSlots" : 16, 
	"simpleMemoryModel.nicNumStoreSlots" : 16, 

	"simpleMemoryModel.nicHostLoadSlots" : 1, 
	"simpleMemoryModel.nicHostStoreSlots" : 1, 

	"simpleMemoryModel.busBandwidth_Gbs" : 7.8,
	"simpleMemoryModel.busNumLinks" : 8,
	"simpleMemoryModel.detailedModel.name" : "firefly.detailedInterface",
	"maxRecvMachineQsize" : 100,
	"maxSendMachineQsize" : 100,

    #"numVNs" : 7,

    #"getHdrVN" : 1,
    #"getRespSmallVN" : 2,
    #"getRespLargeVN" : 3,
    #"getRespSize" : 15000,

    #"shmemAckVN": 1 ,
    #"shmemGetReqVN": 2,
    #"shmemGetLargeVN": 3,
    #"shmemGetSmallVN": 4,
    #"shmemGetThresholdLength": 8,
    #"shmemPutLargeVN": 5,
    #"shmemPutSmallVN": 6,
    #"shmemPutThresholdLength": 8,

}

emberParams = {
    "os.module"    : "firefly.hades",
    "os.name"      : "hermesParams",
    "api.0.module" : "firefly.hadesMP",
    "api.1.module" : "firefly.hadesSHMEM",
    "api.2.module" : "firefly.hadesMisc",
    'firefly.hadesSHMEM.verboseLevel' : 0,
    'firefly.hadesSHMEM.verboseMask'  : -1,
    'firefly.hadesSHMEM.enterLat_ns'  : 1,
    'firefly.hadesSHMEM.returnLat_ns' : 1,
    "verbose" : 0,
}

hermesParams = {
	"hermesParams.detailedCompute.name" : "thornhill.SingleThread",
	"hermesParams.memoryHeapLink.name" : "thornhill.MemoryHeapLink",
    "hermesParams.nicModule" : "firefly.VirtNic",

    "hermesParams.functionSM.defaultEnterLatency" : 1,
    "hermesParams.functionSM.defaultReturnLatency" : 1,

    #"hermesParams.functionSM.smallCollectiveVN" : 1,
    "hermesParams.fBandtrlMsg.shortMsgLength" : 120000000,
    "hermesParams.ctrlMsg.matchDelay_ns" : 1,

    "hermesParams.ctrlMsg.txSetupMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txSetupModParams.range.0" : "0-:0ns",

    "hermesParams.ctrlMsg.rxSetupMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.rxSetupModParams.range.0" : "0-:100ns",

    "hermesParams.ctrlMsg.txMemcpyMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txMemcpyModParams.op" : "Mult",
    "hermesParams.ctrlMsg.txMemcpyModParams.range.0" : "0-:1000ps",

    "hermesParams.ctrlMsg.rxMemcpyMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txMemcpyModParams.op" : "Mult",
    "hermesParams.ctrlMsg.rxMemcpyModParams.range.0" : "0-:1000ps",

    "hermesParams.ctrlMsg.sendAckDelay_ns" : 0,
    "hermesParams.ctrlMsg.regRegionBaseDelay_ns" : 0,
    "hermesParams.ctrlMsg.regRegionPerPageDelay_ns" : 0,
    "hermesParams.ctrlMsg.regRegionXoverLength" : 4096,
    "hermesParams.loadMap.0.start" : 0,
    "hermesParams.loadMap.0.len" : 2,
}

