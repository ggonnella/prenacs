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

def _retvals_to_module_attrs(m, prefix):
  for k in list(m.__dict__.keys()):
    if k.startswith(prefix):
      c = k[len(prefix):]
      setattr(m, c, getattr(m, k)())
      delattr(m, k)

def nim(filename, verbose=False, import_constants=True):
  """
  Import (and compile if necessary) a module written in Nim and
  based on Nimpy.

  Requirements:
  - Nim compiler
  - Nimporter

  import_constants option:
    if True, the return value of functions of the module whose name starts with
    "py_const_" (called without arguments) is stored as an attribute of the
    module (named without the aforementioned prefix), and the function is
    deleted from the module. This is a mechanism aimed at creating module-level
    constants.
  """
  modulename = Path(filename).stem
  parent = Path(filename).parent
  m = nimporter.Nimporter.import_nim_module(modulename, [parent])
  if import_constants:
    _retvals_to_module_attrs(m, "py_const_")
  if verbose:
    sys.stderr.write(
        f"# nim module {modulename} imported from file {filename}\n")
  m.__lang__ = "nim"
  return m

