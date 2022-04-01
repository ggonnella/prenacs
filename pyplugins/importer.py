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

def importer(filename, verbose=False):
  """
  Import a module "filename", which is either a pure Python module
  or an extension module written in Nim or Rust. Set the __lang__ attribute
  of the module to "nim" or "python" or "rust".

  Assumptions:
  - Rust modules file suffix is ".rs"

  Requirements:
  - see requirements of rust() and nim() methods
  """
  if Path(filename).suffix == ".rs":
    m = rust(filename, verbose)
  else:
    try:
      m = py(filename, verbose)
    except:
      m = nim(filename, verbose)
  return m
