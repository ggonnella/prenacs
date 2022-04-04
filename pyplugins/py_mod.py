#
# (c) Giorgio Gonnella, 2021-2022
#
"""
Programmatically import a Python module
"""

import sys
import importlib
from pathlib import Path
from pyplugins.api_config import apply_api_config

def py(filename, api_config = {}, verbose=False):
  """
  Programmatically import Python module "filename"
  """
  modulename = Path(filename).stem
  spec = importlib.util.spec_from_file_location(modulename, filename)
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)

  info = [f"# python module {modulename} imported from file {filename}\n"]
  info += apply_api_config(m, modulename, api_config, verbose)
  if verbose:
    sys.stderr.write("".join(info))
  m.__lang__ = "python"
  return m

