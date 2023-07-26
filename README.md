# dask_ecs_lib
Create a dask cluster to run a provided function

 Package      scheduler      

 blosc  -->      1.10.6          
 cloudpickle  -->  2.2.1       
 dask  -->         2023.3.0     
 distributed  -->  2023.3.0     
 lz4  -->          4.3.2          
 msgpack  -->     1.0.4          
 numpy  -->        1.24.2      
 pandas  -->       1.5.3          
 python  -->       3.8.0.final.0 
 toolz  -->        0.12.0
 tornado -->      6.2

You will want the client (the environment you are launching the ECS cluster from) to have the above libraries and versions matched. Check client_requirements.txt.

### How do I get set up? ###

* Importing:

    ```
    import svclusterlib`

    from svclusterlib import daskfunctions
    ```

* Usage:
    ```
    daskfunctions.runTask(mode, func, project, num_workers, worker_vcpu, worker_memory, return_result)
    ```
    
    * param mode --> string --> "local", "ecsspot" or "fargate" --REQUIRED
    * param func --> function --> The function to be run in the cluster -- REQUIRED
    * param project --> string --> The project to run, which determines the image to use. "research", "data_quality" or "latest" --> default is "research" -- REQUIRED 
    * param num_workers --> int --> Number of workers to start on cluster creation. Default 3 --OPTIONAL
    * param worker_vcpu --> int --> The amount of CPU to request for worker tasks in milli-cpu (1/1024). Valid options (1024, 2048, 4096, etc). Default 4096 --OPTIONAL
    * param worker_memory --> int --> The amount of memory to request for worker tasks in MB. Default 8192 --OPTIONAL
    * param return_result -> boolean -> Whether to return the results of the ran function -- default is False

* Examples:
    * 
    ```
    daskfunctions.runTask("fargate", func, "research", 3, 2048, 8192)
    ``` 
    --> Creates a fargate cluster using research image with 3 workers, each with 2vCPUs and 8GB memory to run the function `func`.
    * 
    ```
    daskfunctions.runTask("fargate", func, "data_quality", 4, 2048, 4096)
    ``` 
    --> Creates a fargate cluster using data_quality image with 4 workers, each with 2vCPUs and 4GB memory to run the function `func`.
    * 
    ```
    daskfunctions.runTask("fargate", func, "latest", 4, 2048, 4096)
    ``` 
    --> Creates a fargate cluster using latest Dask image (currently py3.8) with 4 workers, each with 2vCPUs and 4GB memory to run the function `func`.
    * 
    ```
    daskfunctions.runTask("fargate", func, "research", 4, 2048, 4096, True)
    ``` 
    --> Creates a fargate cluster using research image with 4 workers, each with 2vCPUs and 4GB memory to run the function `func` and return the result of the function.
    * 
    ```
    daskfunctions.runTask("local", func, "research", 4)
    ``` 
    --> Creates a local dask cluster using research image with 4 workers to run the function `func`.

* Note:
    * The function to run must be include a joblib context.

        ```
        with joblib.parallel_backend("dask"):

            searcher.fit(X,y)
