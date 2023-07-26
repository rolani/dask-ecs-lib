import json
import logging.config
import logging
from pathlib import Path

LOG_CONFIG = Path(__file__).parent / 'log.json'
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class RemoveLevelFilter:
    def __init__(self, level_to_skip):
        self.level = level_to_skip

    def filter(self, record):
        return record.levelno < logging.getLevelName(self.level)


def set_log_config():
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('aiobotocore').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    with LOG_CONFIG.open('rb') as stream:
        config = json.load(stream)
    logging.config.dictConfig(config)
