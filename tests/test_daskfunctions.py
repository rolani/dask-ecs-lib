import pytest
from unittest.mock import patch, MagicMock
from dask_ecs_lib import daskfunctions
from dask_ecs_lib import utils


class TestUtils:
    """Test utility functions."""

    def test_parse_url(self):
        """Test parsing cluster URL from string."""
        cluster_str = "Cluster(cluster-abc123, tcp://10.0.0.1:8786, memory=8.00 GB, cores=4)"
        expected_url = "http://10.0.0.1:8787"
        assert utils.parse_url(cluster_str) == expected_url

    def test_estimate_cost(self):
        """Test cost estimation calculation."""
        rate_per_hour = 1.5
        elapsed_seconds = 3600  # 1 hour
        expected_cost = 1.5
        assert utils.estimate_cost(rate_per_hour, elapsed_seconds) == expected_cost

        # Test fractional hour
        elapsed_seconds = 1800  # 30 minutes
        expected_cost = 0.75
        assert utils.estimate_cost(rate_per_hour, elapsed_seconds) == expected_cost


class TestDaskFunctions:
    """Test daskfunctions module."""

    @patch('dask_ecs_lib.daskfunctions.LocalCluster')
    @patch('dask_ecs_lib.daskfunctions.Client')
    def test_run_task_local_mode(self, mock_client, mock_local_cluster):
        """Test runTask in local mode."""
        # Mock the cluster and client
        mock_cluster_instance = MagicMock()
        mock_local_cluster.return_value.__enter__.return_value = mock_cluster_instance
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # Define a test function
        def test_func():
            return "test result"

        # Call runTask in local mode without return_result
        result = daskfunctions.runTask("local", test_func, num_workers=2)

        # Assertions
        mock_local_cluster.assert_called_once_with(n_workers=2, threads_per_worker=1)
        mock_client.assert_called_once_with(mock_cluster_instance)
        mock_client_instance.close.assert_not_called()  # Should be called via context manager
        assert result is None  # No return since return_result=False

    @patch('dask_ecs_lib.daskfunctions.LocalCluster')
    @patch('dask_ecs_lib.daskfunctions.Client')
    def test_run_task_local_mode_with_return(self, mock_client, mock_local_cluster):
        """Test runTask in local mode with return_result=True."""
        mock_cluster_instance = MagicMock()
        mock_local_cluster.return_value.__enter__.return_value = mock_cluster_instance
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance

        def test_func():
            return "test result"

        result = daskfunctions.runTask("local", test_func, return_result=True)

        assert result == "test result"

    @patch('dask_ecs_lib.daskfunctions.FargateCluster')
    @patch('dask_ecs_lib.daskfunctions.Client')
    @patch('dask_ecs_lib.daskfunctions.time')
    @patch('dask_ecs_lib.daskfunctions.svutils.parse_url')
    def test_run_task_fargate_mode(self, mock_parse_url, mock_time, mock_client, mock_fargate_cluster):
        """Test runTask in fargate mode."""
        # Mock time
        mock_time.time.side_effect = [0, 1, 2]  # start, cluster ready, end

        # Mock cluster
        mock_cluster_instance = MagicMock()
        mock_cluster_instance.__str__ = MagicMock(return_value="cluster_info")
        mock_fargate_cluster.return_value.__enter__.return_value = mock_cluster_instance

        # Mock client
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # Mock parse_url
        mock_parse_url.return_value = "http://dashboard:8787"

        def test_func():
            return "fargate result"

        # Mock environment variables
        with patch.dict('os.environ', {'SECURITY_GROUP': 'sg-123', 'DEFAULT_AWS_REGION': 'us-east-1'}):
            result = daskfunctions.runTask("fargate", test_func, num_workers=3, worker_vcpu=2048, worker_memory=4096)

        # Assertions
        mock_fargate_cluster.assert_called_once()
        call_args = mock_fargate_cluster.call_args
        assert call_args[1]['n_workers'] == 3
        assert call_args[1]['worker_cpu'] == 2048
        assert call_args[1]['worker_mem'] == 4096
        assert result is None

    def test_run_task_invalid_mode(self):
        """Test runTask with invalid mode."""
        def test_func():
            return "result"

        with patch('dask_ecs_lib.daskfunctions.logger') as mock_logger:
            result = daskfunctions.runTask("invalid", test_func)
            mock_logger.info.assert_called_with("mode has to be local or fargate")
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__])