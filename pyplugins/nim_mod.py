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
from pyplugins.api_config import apply_api_config

def _retvals_to_module_attrs(m, prefix):
  for k in list(m.__dict__.keys()):
    if k.startswith(prefix):
      c = k[len(prefix):]
      setattr(m, c, getattr(m, k)())
      delattr(m, k)

def nim(filename, api_config = {}, verbose=False):
  """
  Import (and compile if necessary) a module written in Nim and
  based on Nimpy.

  Requirements:
  - Nim compiler
  - Nimporter

  Constants definition mechanism:

    In order to define module-level constants, functions are defined
    in the module, with arity 0 and a name starting with "py_consts_".

    This prefix is stripped from the function name and the function
    is called to get the value of the constant. The function is then
    deleted from the module.

    Example:

      proc py_const_VERSION(): string = { "1.0.0" }
      # in the returned module (m): m.VERSION == "1.0.0"

    Settings:

      The prefix must be exclusive for this purpose. The default prefix
      can be changed by setting the nim_const_pfx key of the api_config dict.

      To disable the constants definition mechanism, set
      api_config["nim_const_pfx"] to an empty string.
  """
  modulename = Path(filename).stem
  parent = Path(filename).parent
  m = nimporter.Nimporter.import_nim_module(modulename, [parent])
  info = [f"# nim module {modulename} imported from file {filename}\n"]
  pfx = api_config.get("nim_const_pfx", "py_const_")
  if len(pfx) > 0:
    imported = _retvals_to_module_attrs(m, pfx)
    info += apply_api_config(m, modulename, api_config, True)
  else:
    info += apply_api_config(m, modulename, api_config, False)
    info.append("# constants definition mechanism disabled\n")
  if verbose:
    sys.stderr.write("".join(info))
  m.__lang__ = "nim"
  return m

