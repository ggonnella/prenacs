#
# (c) Giorgio Gonnella, 2021-2022
#
"""
Programmatically import a Python module and compile it on the
fly if it is an extension module written in Nim or Rust.
"""

from pathlib import Path
from multiplug.py_mod import py
from multiplug.rust_mod import rust, RUST_CONST_CLS
from multiplug.nim_mod import nim, NIM_CONST_PFX
from multiplug.bash_mod import bash
from multiplug.error import UnsupportedLangError

def importer(filename, verbose=False, req_const=[], opt_const=[],
             req_func=[], opt_func=[], rust_const_cls=RUST_CONST_CLS,
             nim_const_pfx=NIM_CONST_PFX, disable_bash=False):
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
  If ``disable_bash`` is set, then Bash scripts are not supported.

  Return value:
    the imported module

  Attributes added to the imported module:
    __lang__: the language of the module (one of "py", "rust", "nim", "bash")
    variables/constants:
      Python: as in normal module import
      Nim: constants passed to exportpy_consts or exportpy_consts_wpfx;
           functions exported to Python with name starting with ``py_const_``
           (or the value of ``nim_const_pfx``)
      Rust: constants defined in a Struct, exported to Python,
            named ``Constants`` (or the value of ``rust_const_cls``)
      Bash: variables whose name does not start with _
            (with the value they have after script execution)
    functions:
      Python: as in normal module import
      Nim: functions exported to Python --
           except those with name starting with ``py_const_``
           (or the value of ``nim_const_pfx``)
      Rust: functions exported to Python
      Bash: functions whose name does not start with _,
            wrapped in a function with parameters ``(*args, **kwargs)``
  """
  suffix = Path(filename).suffix
  if suffix == ".rs":
    m = rust(filename, verbose=verbose, req_const=req_const,
             opt_const=opt_const, req_func=req_func, opt_func=opt_func,
             const_cls=rust_const_cls)
  elif suffix == ".sh":
    if disable_bash:
      raise UnsupportedLangError("Bash scripts are not supported by this "+\
                                  "application")
    m = bash(filename, verbose=verbose, req_const=req_const,
             opt_const=opt_const, req_func=req_func, opt_func=opt_func)
  elif suffix == ".nim":
    m = nim(filename, verbose=verbose, req_const=req_const,
            opt_const=opt_const, req_func=req_func, opt_func=opt_func,
            const_pfx=nim_const_pfx)
  elif suffix == ".py":
    m = py(filename, verbose=verbose, req_const=req_const,
           opt_const=opt_const, req_func=req_func, opt_func=opt_func)
  else:
    raise UnsupportedLangError("Unsupported language, file suffix is: " \
                                 + suffix)
  return m
