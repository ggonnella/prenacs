#
# (c) Giorgio Gonnella, 2021-2022
#
"""
Programmatically import a Nim module and compile it on the
fly if necessary.
"""

import sh
import sys
import importlib
from pathlib import Path
import nimporter
import os
from contextlib import contextmanager
from multiplug.plugin_api import enforce_plugin_api

NIM_CONST_PFX="py_const_"

def _import_constants(m, prefix):
  for k in list(m.__dict__.keys()):
    if k.startswith(prefix):
      c = k[len(prefix):]
      setattr(m, c, getattr(m, k)())
      delattr(m, k)

def nim(filename, verbose=False, req_const=[], opt_const=[],
        req_func=[],  opt_func=[], const_pfx=NIM_CONST_PFX):
  """
  Import (and compile if necessary) a module written in Nim and
  based on Nimpy.
  """
  modulename = Path(filename).stem
  parent = Path(filename).parent
  m = nimporter.Nimporter.import_nim_module(modulename, [parent])
  info = [f"# nim module {modulename} imported from file {filename}\n"]
  if len(const_pfx) > 0:
    _import_constants(m, const_pfx)
    info += enforce_plugin_api(m, modulename, req_func=req_func,
                             opt_func=opt_func, req_const=req_const,
                             opt_const=opt_const)
  else:
    assert len(req_const) == 0
    info += enforce_plugin_api(m, modulename, req_func=req_func,
                             opt_func=opt_func, opt_const=opt_const)
    info.append("# constants definition mechanism disabled\n")
  if verbose:
    sys.stderr.write("".join(info))
  m.__lang__ = "nim"
  return m

