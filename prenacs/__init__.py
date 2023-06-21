#
# (c) 2021-2023 Giorgio Gonnella, University of Goettingen, Germany
#
from .batch_computation import BatchComputation
from .plugin_interface_analyser import PluginInterfaceAnalyser
from .attribute_definitions_manager import AttributeDefinitionsManager
from .dbschema.attribute_definition import AttributeDefinition
from .dbschema.plugin_description import PluginDescription
from .dbschema.computation_report import ComputationReport
from .results_loader import ResultsLoader

__version__="1.2"

# setup loguru by disabling it, as expected for libraries
from loguru import logger
logger.disable(__name__)
import sys

def enable_logger(level):
  """
  Enables logging for the prenacs package with the specified level.

  Args:
    level: The logging level to set
      (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
  """
  logger.remove()
  logger.enable("prenacs")
  msgformat_prefix="<green><dim>{time:YYYY-MM-DD HH:mm:ss}</></>"
  msgformat_content="<level><normal>{level.name}: {message}</></>"
  logger.add(sys.stderr, format=f"{msgformat_prefix} {msgformat_content}",
       level=level)

# create a flag to enable/disable progress bar; disable it by default;
# the method tqdm will respect this flag and behave like tqdm.tqdm;
import tqdm as tqdm_module   # type: ignore
PROGRESS_ENABLED=False       # default value
tqdm = lambda *args, **kargs: \
    tqdm_module.tqdm(*args, **{**{"disable": not PROGRESS_ENABLED}, **kargs})

