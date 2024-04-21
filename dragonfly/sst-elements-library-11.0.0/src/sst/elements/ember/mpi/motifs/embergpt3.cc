#include <sst_config.h>
#include "embergpt3.h"

using namespace SST::Ember;

//#define RUNS 128
#define RUNS 1
#define NUM_L 96
#define MODEL_SHARDS 4
#define ACC_STEP_SCALE 2

#define PIPE_P2P_SIZE 25165824
#define MP_ALLREDUCE_SIZE 25165824
#define DP_ALLREDUCE_SIZE 452984832

/*
#define PIPE_P2P_SIZE 8192
#define MP_ALLREDUCE_SIZE 4096
#define DP_ALLREDUCE_SIZE 8192
*/

#define FWD_RT 15915*1000
#define BWD_RT 31830*1000

/*#define FWD_RT 1
#define BWD_RT 1*/

bool EmberGPT3Generator::progress_iteration(std::queue<EmberEvent *> &evQ)
{
    switch (m_iteration_state) 
    {
    case INIT:
    {
        printf("[%d] init\n", rank());
        if (m_stage_id % 2 == 0) {
            enQ_irecv(evQ, m_bwd_recv_buff, PIPE_P2P_SIZE, FLOAT, m_stage_id+1, 1, m_pp_p2p_comm, &m_reqs[0]);
            enQ_compute(evQ, FWD_RT);
            count_compute_time += FWD_RT;
        }
        else {
            enQ_irecv(evQ, m_fwd_recv_buff, PIPE_P2P_SIZE, FLOAT, m_stage_id-1, 2, m_pp_p2p_comm, &m_reqs[1]);
            enQ_compute(evQ, BWD_RT);
            count_compute_time += BWD_RT;
        }
        m_iteration_state = ALLREDUCE_1;  
        return false;
    }
    case ALLREDUCE_1:
    {
        printf("[%d] allreduce1\n", rank());
        if (!m_mp_allreduce->progress(evQ)) return false;
        m_mp_allreduce->reset();
        m_iteration_state = ALLREDUCE_2;  
        // no break
    }
    case ALLREDUCE_2:
    {
        printf("[%d] allreduce2\n", rank());
        if (!m_mp_allreduce->progress(evQ)) return false;
        m_mp_allreduce->reset();
        m_iteration_state = P2P;
        // no break
    }  
    case P2P:
    {
        printf("[%d] p2p\n", rank());
        if(m_stage_id % 2 == 0) 
        {
            enQ_isend(evQ, m_fwd_send_buff, PIPE_P2P_SIZE, FLOAT, m_stage_id+1, 2, m_pp_p2p_comm, &m_reqs[1]);
        }
        else
        {
            enQ_isend(evQ, m_bwd_send_buff, PIPE_P2P_SIZE, FLOAT, m_stage_id-1, 1, m_pp_p2p_comm, &m_reqs[0]);
        }
        m_iteration_state = P2P_WAIT;
        return false;
    }
    case P2P_WAIT:
    {
        printf("[%d] p2p wait\n", rank());
        enQ_waitall(evQ, 2, &m_reqs[0]);
        return true;
    }
    default: assert(0);
    }

    assert(0);
}

bool EmberGPT3Generator::setup_comms(std::queue<EmberEvent *> &evQ)
{
    // void rank( Queue& q, Communicator comm, uint32_t* rankPtr)
    // void size( Queue& q, Communicator comm, int* sizePtr)

    int world_size = size();
    int my_rank = rank();
    assert(world_size % (m_num_stage * MODEL_SHARDS) == 0);
    
    switch (m_setup_stage)
    {
    case 0:
    {
        int dp_allreduce_group_color = my_rank % (m_num_stage * MODEL_SHARDS);
        /// MPI_Comm_split(MPI_COMM_WORLD, dp_allreduce_group_color, rank, &dp_allreduce_comm);
        printf("[%d] STAGE 0: m_dp_allreduce_comm (color: %d; key: %d)\n", rank(), dp_allreduce_group_color, my_rank);
        enQ_commSplit(evQ, GroupWorld, dp_allreduce_group_color, my_rank, &m_dp_allreduce_comm);
        m_setup_stage++;
        return false;
    }
    case 1:
    {
        printf("[%d] STAGE 1\n", rank());
        // MPI_Comm_rank(dp_allreduce_comm, &dp_allreduce_group_rank);
        enQ_rank(evQ, m_dp_allreduce_comm, &m_dp_allreduce_group_rank);
        // MPI_Comm_size(dp_allreduce_comm, &dp_allreduce_group_size);
        enQ_size(evQ, m_dp_allreduce_comm, &m_dp_allreduce_group_size);

        m_setup_stage++;
        return false;
    }
    case 2:
    {
        printf("[%d] STAGE 2: m_dp_allreduce_comm: m_dp_allreduce_group_rank: %d; m_dp_allreduce_group_size: %d\n", rank(), m_dp_allreduce_group_rank, m_dp_allreduce_group_size);
        printf("[%d] STAGE 2: SPLIT m_mp_pp_comm (color: %d; key: %d)\n", rank(), m_dp_allreduce_group_rank, my_rank);
        // MPI_Comm_split(MPI_COMM_WORLD, dp_allreduce_group_rank, rank, &mp_pp_comm);
        enQ_commSplit(evQ, GroupWorld, m_dp_allreduce_group_rank, my_rank, &m_mp_pp_comm);

        m_setup_stage++;
        return false;
    }
    case 3:
    {
        printf("[%d] STAGE 3\n", rank());
        // MPI_Comm_rank(mp_pp_comm, &mp_pp_group_rank);
        enQ_rank(evQ, m_mp_pp_comm, &m_mp_pp_group_rank);
        // MPI_Comm_size(mp_pp_comm, &mp_pp_group_size);
        enQ_size(evQ, m_mp_pp_comm, &m_mp_pp_group_size);

        m_setup_stage++;
        return false;
    }
    case 4:
    {
        int mp_allreduce_group_color = m_mp_pp_group_rank % m_num_stage;

        printf("[%d] STAGE 4: m_mp_pp_comm: m_mp_pp_group_rank: %d; m_mp_pp_group_size: %d\n", rank(), m_mp_pp_group_rank, m_mp_pp_group_size);
        printf("[%d] STAGE 4: SPLIT m_mp_allreduce_comm (color: %d; key: %d)\n", rank(), mp_allreduce_group_color, m_mp_pp_group_rank);

        // MPI_Comm_split(mp_pp_comm, mp_allreduce_group_color, mp_pp_group_rank, &mp_allreduce_comm);
        enQ_commSplit(evQ, m_mp_pp_comm, mp_allreduce_group_color, m_mp_pp_group_rank, &m_mp_allreduce_comm);

        m_setup_stage++;
        return false;
    }
    case 5:
    {
        printf("[%d] STAGE 5\n", rank());
        // MPI_Comm_rank(mp_allreduce_comm, &mp_allreduce_group_rank);
        enQ_rank(evQ, m_mp_allreduce_comm, &m_mp_allreduce_group_rank);
        // MPI_Comm_size(mp_allreduce_comm, &mp_allreduce_group_size);
        enQ_size(evQ, m_mp_allreduce_comm, &m_mp_allreduce_group_size);

        m_setup_stage++;
        return false;
    }
    case 6:
    {
        printf("[%d] STAGE 6: m_mp_allreduce_comm: m_mp_allreduce_group_rank: %d; m_mp_allreduce_group_size: %d\n", rank(), m_mp_allreduce_group_rank, m_mp_allreduce_group_size);
        printf("[%d] STAGE 6: SPLIT m_pp_p2p_comm (color: %d; key: %d)\n", rank(), m_mp_allreduce_group_rank, m_mp_pp_group_rank);

        // MPI_Comm_split(mp_pp_comm, mp_allreduce_group_rank, mp_pp_group_rank, &pp_p2p_comm);
        enQ_commSplit(evQ, m_mp_pp_comm, m_mp_allreduce_group_rank, m_mp_pp_group_rank, &m_pp_p2p_comm);

        m_setup_stage++;
        return false;
    }
    case 7:
    {
        printf("[%d] STAGE 7\n", rank());
        // MPI_Comm_rank(pp_p2p_comm, &pp_p2p_group_rank);
        enQ_rank(evQ, m_pp_p2p_comm, &m_pp_p2p_group_rank);
        // MPI_Comm_size(pp_p2p_comm, &pp_p2p_group_size);
        enQ_size(evQ, m_pp_p2p_comm, &m_pp_p2p_group_size);

        m_setup_stage++;
        return false;
    }
    case 8:
    {
        printf("[%d] STAGE 8: m_pp_p2p_comm: m_pp_p2p_group_rank: %d; m_pp_p2p_group_size: %d\n", rank(), m_pp_p2p_group_rank, m_pp_p2p_group_size);

        //MPI_Allreduce(mp_fwd_inter_ptrs[0], sum_mp_fwd_inter_ptrs[0], MP_ALLREDUCE_SIZE, MPI_FLOAT, MPI_SUM, mp_allreduce_comm);   
        //MPI_Allreduce(grad_ptr, sum_grad_ptr, DP_ALLREDUCE_SIZE, MPI_FLOAT, MPI_SUM, dp_allreduce_comm);
        if (!all_reduce_type.compare("05D")) {
            m_mp_allreduce = new EmberRingAllreduce05D(*this, MP_ALLREDUCE_SIZE, m_mp_allreduce_group_rank, m_mp_allreduce_group_size, m_mp_allreduce_comm, m_aggregation_cost_ns, false);
            m_dp_allreduce = new EmberRingAllreduce05D(*this, DP_ALLREDUCE_SIZE, m_dp_allreduce_group_rank, m_dp_allreduce_group_size, m_dp_allreduce_comm, m_aggregation_cost_ns, false);
        } else if (!all_reduce_type.compare("2D")) {
            m_mp_allreduce = new EmberRingAllreduce2D(*this, MP_ALLREDUCE_SIZE, m_mp_allreduce_group_rank, m_mp_allreduce_group_size, m_mp_allreduce_comm, m_aggregation_cost_ns, false, px);
            m_dp_allreduce = new EmberRingAllreduce2D(*this, DP_ALLREDUCE_SIZE, m_dp_allreduce_group_rank, m_dp_allreduce_group_size, m_dp_allreduce_comm, m_aggregation_cost_ns, false, px);
        } else if (!all_reduce_type.compare("25D")) {
            printf("Size %d - MPGroup Rank %d - m_mp_allreduce_group_size %d - \n", MP_ALLREDUCE_SIZE, m_mp_allreduce_group_rank, m_mp_allreduce_group_size); fflush(stdout);
            m_mp_allreduce = new EmberRingAllreduce25D(*this, MP_ALLREDUCE_SIZE, m_mp_allreduce_group_rank, m_mp_allreduce_group_size, m_mp_allreduce_comm, m_aggregation_cost_ns, false, px);
            printf("Size %d - MPGroup Rank %d - m_mp_allreduce_group_size %d - \n", DP_ALLREDUCE_SIZE, m_dp_allreduce_group_rank, m_dp_allreduce_group_size); fflush(stdout);
            m_dp_allreduce = new EmberRingAllreduce25D(*this, DP_ALLREDUCE_SIZE, m_dp_allreduce_group_rank, m_dp_allreduce_group_size, m_dp_allreduce_comm, m_aggregation_cost_ns, false, px);
        } else {
            printf("Unexpected branch with all reduce type! Exiting!\n");
            exit(EXIT_FAILURE);
        }
        printf("Using %s All Reduce\n", all_reduce_type.c_str());

        m_stage_id = m_pp_p2p_group_rank;

        enQ_barrier(evQ, GroupWorld);

        m_setup_stage++; // we increase it anyway so we go to assert(0) if this gets erronously called again
        return true;
    }
    default: assert(0);
    }
    assert(0);
}

bool EmberGPT3Generator::generate(std::queue<EmberEvent *> &evQ)
{
    switch (m_state) {
    case SETUP:
        if (!setup_comms(evQ)) return false;
        m_state = ITERATE;
        // no break
    case ITERATE:
        if (!progress_iteration(evQ)) return false;
        return true;
    default: assert(0);
    }
    assert(0);
}

EmberGPT3Generator::EmberGPT3Generator(SST::ComponentId_t id, Params &params)
    : EmberHxMeshGenerator(id, params, "GPT3"), 
      m_state(SETUP), 
      m_setup_stage(0), 
      m_grad_acc_step_idx(0), 
      m_iter_idx(0),
      m_iteration_state(INIT)
{
    m_aggregation_cost_ns = (double)params.find("arg.aggregation_cost_ns", 0.01);

    m_num_stage = (uint32_t)params.find("arg.num_stage", NUM_L);
    m_acc_step_scale = (uint32_t)params.find("arg.acc_step_stale", ACC_STEP_SCALE);
    m_grad_acc_step = (uint32_t)params.find("arg.grad_acc_step", m_num_stage * m_acc_step_scale);

    px = (uint32_t)params.find("arg.px", 0);

    all_reduce_type = params.find<std::string>("arg.all_reduce_type", "05D");
    if (all_reduce_type.compare("05D") && all_reduce_type.compare("2D") && all_reduce_type.compare("25D")) {
        printf("Error, non valid all reduce type!\n"); 
        exit(EXIT_FAILURE);
    }

    m_fwd_send_buff = (float *) memAlloc(PIPE_P2P_SIZE*sizeof(float));
    m_fwd_recv_buff = (float *) memAlloc(PIPE_P2P_SIZE*sizeof(float));
    m_bwd_send_buff = (float *) memAlloc(PIPE_P2P_SIZE*sizeof(float));
    m_bwd_recv_buff = (float *) memAlloc(PIPE_P2P_SIZE*sizeof(float));

}

EmberGPT3Generator::~EmberGPT3Generator()
{
    printf("\nRank %d - Total Compute time %" PRIu64 " \n", rank(), count_compute_time);
    delete m_dp_allreduce;
    delete m_mp_allreduce;

    memFree(m_fwd_send_buff);
    memFree(m_fwd_recv_buff);
    memFree(m_bwd_send_buff);
    memFree(m_bwd_recv_buff);
}
