#
# (c) Giorgio Gonnella, 2021-2022
#
"""
Programmatically import a Python module
"""

import sys
import importlib
from pathlib import Path
from multiplug.plugin_api import enforce_plugin_api

def py(filename, verbose=False, req_const=[], opt_const=[],
                                req_func=[],  opt_func=[]):
  """
  Programmatically import Python module "filename"
  """
  modulename = Path(filename).stem
  spec = importlib.util.spec_from_file_location(modulename, filename)
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)

  info = [f"# python module {modulename} imported from file {filename}\n"]
  info += enforce_plugin_api(m, modulename, req_const=req_const,
                           opt_const=opt_const, req_func=req_func,
                           opt_func=opt_func)
  if verbose:
    sys.stderr.write("".join(info))
  m.__lang__ = "python"
  return m

