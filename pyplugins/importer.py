#
# (c) Giorgio Gonnella, 2021-2022
#
"""
Programmatically import a Python module and compile it on the
fly if it is an extension module written in Nim or Rust.
"""

from pathlib import Path
from pyplugins.py_mod import py
from pyplugins.rust_mod import rust
from pyplugins.nim_mod import nim
from pyplugins.bash_mod import bash
from pyplugins.error import UnsupportedLangError

def importer(filename, api_config={}, verbose=False):
  """
  Import a module given its "filename".

  The module can be:
  - a pure Python module
  - an extension module written in Nim or Rust
    (which is automatically compiled if necessary)
  - a Bash script
    (for which a wrapper module is automatically generated)

  The language of the module is deducted from the filename extension, which
  must be one of: ".py", ".nim", ".rs", ".sh".

  If api_config["disable_bash"] is set, then Bash scripts
  are not supported.

  Return value:
  - the module, with:
    - an attribute __lang__ set to "python", "nim", "rust" or "bash"
    - the functions defined in the module (for "bash", a configuration is
      required, see below)
    - constants defined in the module (a configuration is required, except
      for Python modules)

  For the syntax of the API configuration dictionary, see the usage manual.

  Requirements:
  - Rust: see requirements in rust_mod.py
  - Nim: see requirements in nim_mod.py
  """
  suffix = Path(filename).suffix
  if suffix == ".rs":
    m = rust(filename, api_config, verbose)
  elif suffix == ".sh":
    if api_config.get("disable_bash", False):
      raise UnsupportedLangError("Bash scripts are not supported by this "+\
                                  "application")
    m = bash(filename, api_config, verbose)
  elif suffix == ".nim":
    m = nim(filename, api_config, verbose)
  elif suffix == ".py":
    m = py(filename, api_config, verbose)
  else:
    raise UnsupportedLangError("Unsupported language, file suffix is: " \
                                 + suffix)
  return m
