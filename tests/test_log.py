"""
Log functional tests
"""

import os
import sys
import logging  # To display the logging values

sys.path.insert(0, os.path.abspath('.'))
import utils


def print_logs(logger, level):
    print("Testing log level: {}".format(level))
    logger.debug('Testing debug ({})'.format(logging.DEBUG))
    logger.info('Testing info ({})'.format(logging.INFO))
    logger.warning('Testing warning ({})'.format(logging.WARNING))
    logger.error('Testing error ({})'.format(logging.ERROR))
    logger.critical('Testing critical ({})'.format(logging.CRITICAL))


def test_logs():
    test_logging = utils.get_logging(1)
    logger = test_logging.logger
    for level in range(6):
        test_logging.set_level(level)
        print_logs(logger, level)
    test_logging.shutdown()

if __name__ == '__main__':
    test_logs()
