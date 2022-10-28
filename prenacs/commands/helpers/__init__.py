#
# (c) 2022, Giorgio Gonnella, University of Goettingen, Germany
#

import prenacs
from .common import validate
from . import common
from . import report
from . import database

import sys
from pathlib import Path
import importlib.util

def setup_verbosity(args):
  if args["--quiet"]:
    prenacs.PROGRESS_ENABLED = False
    prenacs.logger.remove()
  else:
    prenacs.PROGRESS_ENABLED = True
    if args["--debug"]:
      level = "DEBUG"
    else:
      level = "INFO"
    prenacs.enable_logger(level)

