#
# (c) Giorgio Gonnella, 2021-2022
#
"""
Programmatically import a Python module
"""

import sys
import importlib
from pathlib import Path

def py(filename, verbose=False):
  """
  Programmatically import Python module "filename"
  """
  modulename = Path(filename).stem
  spec = importlib.util.spec_from_file_location(modulename, filename)
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  if verbose:
    sys.stderr.write(
        f"# python module {modulename} imported from file {filename}\n")
  m.__lang__ = "python"
  return m

