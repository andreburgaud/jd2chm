import os
import sys

import jd2chm_log
import jd2chm_conf

logging = None
config = None

def getAppDir():
  if hasattr(sys, "frozen"): # py2exe
    return os.path.dirname(sys.executable)
  return os.path.dirname(sys.argv[0])

def getLogging(level=2):
  global logging
  if not logging:
    logging = jd2chm_log.Jd2chmLogging(level)
  return logging

def getLog():
  """Faciliate sharing the logger accross the different modules."""
  return getLogging().logger

def getConf():
  global config
  if not config:
    config = jd2chm_conf.Jd2chmConfig()
    config.init()
  return config