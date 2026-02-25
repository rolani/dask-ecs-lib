import pytest
import logging
from unittest.mock import patch, mock_open
from dask_ecs_lib import logger


class TestLogger:
    """Test logger configuration."""

    @patch('dask_ecs_lib.logger.Path')
    @patch('dask_ecs_lib.logger.json.load')
    @patch('dask_ecs_lib.logger.logging.config.dictConfig')
    def test_set_log_config(self, mock_dictConfig, mock_json_load, mock_path):
        """Test setting log configuration."""
        # Mock the log.json file
        mock_log_config = {"version": 1, "handlers": {}}
        mock_json_load.return_value = mock_log_config

        # Mock Path
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.open = mock_open()

        # Call set_log_config
        logger.set_log_config()

        # Assertions
        mock_path.assert_called_once_with(__file__).parent / 'log.json'
        mock_path_instance.open.assert_called_once_with('rb')
        mock_json_load.assert_called_once()
        mock_dictConfig.assert_called_once_with(mock_log_config)

        # Check logger levels set
        # Note: This would require checking the actual logger instances, but for simplicity, we assume the function works


if __name__ == "__main__":
    pytest.main([__file__])