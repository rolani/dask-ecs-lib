# dask_ecs_lib

A Python library for easily creating and managing Dask clusters on AWS ECS (Elastic Container Service) using Fargate, or running locally for development and testing. This library simplifies the process of deploying distributed computing tasks using Dask, allowing you to focus on your data processing logic rather than infrastructure management.

## Overview

`dask_ecs_lib` provides a high-level interface to create Dask clusters that can run user-defined functions in a distributed manner. It supports two main modes:

- **Local Mode**: Creates a local Dask cluster for development and testing on your machine.
- **Fargate Mode**: Provisions an AWS ECS Fargate cluster for production workloads, automatically handling cluster lifecycle, scaling, and cleanup.

The library integrates with `dask-cloudprovider` for ECS management and provides logging, error handling, and cost estimation utilities.

### Key Features

- **Simple API**: Single function call to create and run on a Dask cluster
- **Flexible Deployment**: Local development or cloud production with AWS Fargate
- **Automatic Cleanup**: Clusters are automatically terminated after task completion
- **Configurable Resources**: Customize CPU, memory, and worker count
- **Built-in Logging**: Comprehensive logging with configurable levels
- **Cost Estimation**: Utility functions to estimate AWS costs
- **Dashboard Access**: Provides URLs for Dask dashboard monitoring

## Installation

### Prerequisites

- Python 3.7 or higher
- For Fargate mode: AWS credentials configured and appropriate IAM permissions for ECS
- Docker (for local development with matching images)

### Install from Source

```bash
git clone https://github.com/rolani/dask-ecs-lib.git
cd dask-ecs-lib
pip install -e .
```

### Dependencies

The library requires the following packages (automatically installed):

- dask
- distributed
- dask-cloudprovider
- boto3
- requests
- pyyaml
- sqlalchemy
- numpy
- And others (see `requirements.txt`)

### Client Environment Matching

For optimal compatibility, ensure your client environment matches the versions in the Dask worker images. The recommended versions are:

| Package      | Version      |
|--------------|--------------|
| blosc        | 1.10.6       |
| cloudpickle  | 2.2.1        |
| dask         | 2023.3.0     |
| distributed  | 2023.3.0     |
| lz4          | 4.3.2        |
| msgpack      | 1.0.4        |
| numpy        | 1.24.2       |
| pandas       | 1.5.3        |
| toolz        | 0.12.0       |
| tornado      | 6.2          |
| python       | 3.8.0        |

Check `client_requirements_py38.txt` for the complete list.

## Usage

### Basic Import

```python
import dask_ecs_lib
from dask_ecs_lib import daskfunctions
```

### Running a Task

The main entry point is the `runTask` function:

```python
daskfunctions.runTask(mode, func, num_workers=3, worker_vcpu=4096, worker_memory=8192, return_result=False)
```

#### Parameters

- `mode` (str, required): Execution mode. Options:
  - `"local"`: Run on local cluster
  - `"fargate"`: Run on AWS ECS Fargate cluster
- `func` (callable, required): The function to execute on the cluster. Should be a function that can be serialized and executed remotely.
- `num_workers` (int, optional): Number of worker nodes. Default: 3
- `worker_vcpu` (int, optional): CPU allocation per worker in milli-CPU (1/1024 of a vCPU). Default: 4096 (4 vCPUs)
- `worker_memory` (int, optional): Memory allocation per worker in MB. Default: 8192 (8 GB)
- `return_result` (bool, optional): Whether to return the function's result. Default: False

### Examples

#### Local Mode

```python
def my_computation():
    import dask.array as da
    x = da.random.random((10000, 10000), chunks=(1000, 1000))
    return (x + x.T).sum().compute()

# Run locally with 4 workers
daskfunctions.runTask("local", my_computation, num_workers=4)
```

#### Fargate Mode

```python
def data_processing():
    import dask.dataframe as dd
    df = dd.read_csv('s3://my-bucket/data-*.csv')
    result = df.groupby('category').value.sum().compute()
    return result

# Run on Fargate with custom resources
result = daskfunctions.runTask(
    "fargate", 
    data_processing, 
    num_workers=5, 
    worker_vcpu=2048,  # 2 vCPUs
    worker_memory=4096,  # 4 GB
    return_result=True
)
```

### Function Requirements

Your function should be designed for distributed execution:

1. **Import Dependencies Inside Function**: Import all required modules within the function to ensure they're available on worker nodes.

2. **Use Dask Backends**: For libraries like scikit-learn, use Dask backends:

```python
def ml_training():
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    
    # Your data loading and preprocessing
    X, y = load_data()
    
    with joblib.parallel_backend("dask"):
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X, y)
    
    return model
```

3. **Serializable Objects**: Ensure all objects used in the function are serializable.

### Configuration

#### Environment Variables

Set these environment variables for Fargate mode:

- `SECURITY_GROUP`: AWS security group ID that allows traffic between cluster tasks and access to ports 8786-8787
- `DEFAULT_AWS_REGION`: AWS region for cluster deployment

#### Logging

The library provides comprehensive logging. Logs include:
- Cluster creation and startup times
- Dask dashboard URLs
- Task execution times
- Error details

Logging configuration is defined in `log.json` and can be customized.

## API Reference

### daskfunctions.runTask

Creates and manages a Dask cluster to execute the provided function.

**Signature:**
```python
def runTask(mode, func, num_workers=3, worker_vcpu=4096, worker_memory=8192, return_result=False)
```

**Parameters:**
- See usage section above

**Returns:**
- If `return_result=True`: The return value of `func`
- Otherwise: `None`

### Utility Functions

#### utils.parse_url(cluster_str)

Parses cluster information to extract the Dask dashboard URL.

**Parameters:**
- `cluster_str` (str): String representation of cluster object

**Returns:**
- `str`: Dashboard URL (e.g., "http://cluster-address:8787")

#### utils.estimate_cost(rate_per_hour, elapsed_seconds)

Estimates AWS costs for cluster usage.

**Parameters:**
- `rate_per_hour` (float): Cost per hour for the cluster configuration
- `elapsed_seconds` (float): Total runtime in seconds

**Returns:**
- `float`: Estimated cost in currency units

## Development

### Running Tests

```bash
pytest tests/
```

### Building Documentation

The README serves as the primary documentation. For API documentation, see docstrings in the source code.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[Specify license if available]

## Support

For issues and questions:
- Open an issue on GitHub
- Check the Dask documentation: https://docs.dask.org/
- AWS ECS documentation: https://docs.aws.amazon.com/ecs/

## Changelog

### Version 1.0
- Initial release
- Support for local and Fargate clusters
- Basic logging and error handling
- Cost estimation utilities
