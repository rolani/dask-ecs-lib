import time
import logging
import dask_ecs_lib.utils as svutils
import os
from datetime import datetime
from dask_ecs_lib.logger import set_log_config
from dask.distributed import Client, LocalCluster
from dask_cloudprovider.aws import FargateCluster


# security group that allows all traffic between tasks and access to ports 8786 and 8787 from anywhere
sg_group = os.environ('SECURITY_GROUP') 


set_log_config()
logger = logging.getLogger(__name__)


worker_args = ["--local-directory", "/scratch", 
                "--nthreads", "1", 
                "--worker-port", "8786", 
                "--memory-limit", "0"]
scheduler_args = ["--port", "8786"]
scheduler_vcpu = 4096
scheduler_memory = 8192
scheduler_t_out = "3600"

env = {
    'AWS_DEFAULT_REGION': os.environ.get('DEFAULT_AWS_REGION'),
}

tags_ = {
    'app': 'dask_ecs_lib',
    'createdWhen': str(datetime.now())
}

# function to expose params 
def runTask(mode, func, num_workers=3, worker_vcpu=4096, worker_memory=8192, return_result=False):
    """
    Creates a dask cluster and runs the function provided.
    Arguments include
    :param mode -> string -> "local", "gpu" or "fargate"
    :param func -> function -> The function to run in the cluster.
    :param num_workers -> int -> Number of workers to start on cluster creation. Default 3
    :param worker_vcpu -> int -> The amount of CPU to request for worker tasks in milli-cpu (1/1024). Valid options (1024, 2048, 4096, etc). Default 4096.
    :param worker_memory -> int -> The amount of memory to request for worker tasks in MB. Default 8192.
    :param return_result -> boolean -> Whether to return the results of the ran function.
    """
    
    dask_image = 'daskdev/dask:2023.3.0-py3.8'
    
    if mode == "local":
        logger.info("Running dask cluster in local mode!")
        createLocalContext(func, num_workers, return_result)
    elif mode == "fargate":
        logger.info("running dask cluster in ECS using fargate!")
        createFargateContext(func, num_workers, dask_image, worker_vcpu, worker_memory, return_result)
    else:
        logger.info("mode has to be local or fargate")

def createFargateContext(func, num_workers, dask_image, worker_vcpu, worker_memory, return_result):
    """
    Creates a Fargate cluster on ECS and runs the provided function. 

    The cluster gets closed upon completion of the function. 
    """
    begin = time.time()

    cluster_ran = False

    elapsed_time_ = 0
    start = 0
    logger.info("creating Fargate ECS cluster")
    try:
        # create cluster 
        with FargateCluster(image=dask_image, 
                    n_workers=num_workers,                
                    worker_cpu=worker_vcpu,
                    worker_mem=worker_memory,
                    worker_extra_args=worker_args,
                    scheduler_cpu=scheduler_vcpu,
                    scheduler_mem=scheduler_memory,
                    scheduler_timeout=scheduler_t_out,
                    scheduler_extra_args=scheduler_args,
                    security_groups = sg_group,
                    environment=env,
                    tags=tags_
                ) as cluster:

            logger.info("cluster created")
            logger.info("cluster startup time is {:.3f} seconds".format(time.time() - begin))
    

            logger.info("use the following url to visit dask dashboard: {}".format(svutils.parse_url(str(cluster))))
            start = time.time()
            # create client to connect to cluster
            with Client(cluster) as client:    
                if return_result == True:
                    logger.info("Running in return mode")
                    return func()  
                else: 
                    logger.info("Running in normal mode")        
                    func()   
                cluster_ran = True         
    except Exception as e:
        logger.error("Task did not run to completion!!!")
        logger.error(e)
    finally:
        if cluster_ran:
            elapsed_time_ = time.time() - start
            logger.info( "runtime of the program is {:.3f} seconds".format(elapsed_time_))
    logger.info("stopping workers...! Closing cluster")
    

def createLocalContext(func, num_workers, return_result):
    """
    Creates a local dask cluster and runs the function provided on it.  
    """
    with LocalCluster(n_workers=num_workers, threads_per_worker=1) as local_cluster:
        with Client(local_cluster) as client:
            start = time.time()
            if return_result == True:
                logger.info("Running in return mode")
                return func()  
            else:   
                logger.info("Running in normal mode")    
                func()
            logger.info(f"Runtime of the program is {time.time() - start} seconds")