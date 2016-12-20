"""
Log functional tests
"""

import sys
# To be able to run from the test folder
sys.path.append('..')

import logging # To display the logging values
import jd2chm_utils

def testLog(log, level):
  print("Logging level = {}".format(level))
  log.debug('Testing debug ({})'.format(logging.DEBUG))
  log.info('Testing info ({})'.format(logging.INFO))
  log.warning('Testing warning ({})'.format(logging.WARNING))
  log.error('Testing error ({})'.format(logging.ERROR))
  log.critical('Testing critical ({})'.format(logging.CRITICAL))

def test():
  print ("Testing {}...".format(sys.argv[0]))
  jd2chm_logging = jd2chm_utils.get_logging(1)
  log = jd2chm_logging.logger
  for level in range(6):
    jd2chm_logging.setLevel(level)
    testLog(log, level)
  jd2chm_logging.shutdown()

if __name__ == '__main__':
  test()
