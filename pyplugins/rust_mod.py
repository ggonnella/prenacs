#
# (c) Giorgio Gonnella, 2021-2022
#
"""
Programmatically import a Python module and compile it on the
fly if it is an extension module written in Nim or Rust.
"""

import sh
import sys
import importlib
from pathlib import Path
import os
from contextlib import contextmanager
from pyplugins.api_config import apply_api_config

_toml_content = """
[package]
authors = ["*"]
name = "{modulename}"
version = "1.0.0"
edition = "2018"

[dependencies]
pyo3 = {{ version = "0.13.2", features = ["abi3-py36", "extension-module"] }}
{more_dependencies}

[lib]
name = "{modulename}"
crate-type = ["cdylib"]
path = "{modulename}.rs"
"""

def _create_cargo_toml(filename):
  """
  Create Cargo.toml for a pyo3/maturin module in the parent directory of
  <filename>.

  If the Rust code needs any crate, you can add a comment like:
  // [dependencies] foobar = "1.2.3"
  and this is added automatically to the [dependencies] section of Cargo.toml
  """
  workingdir = Path(filename).parent
  modulename = Path(filename).stem
  try:
    more_dependencies=sh.grep('\/\/ \[dependencies\] .*',
                              filename, P=True)
    more_dependencies=str(more_dependencies)[18:]
  except sh.ErrorReturnCode_1:
    more_dependencies=""
  with open(workingdir/"Cargo.toml", "w") as f:
    f.write(_toml_content.format(modulename = modulename,
                                more_dependencies=more_dependencies))

@contextmanager
def _cargo_for(filename):
  """
  Makes sure that a Cargo.toml exists for a module.
  If not, creates one using create_cargo_toml().
  If created, it is also deleted (and the Cargo.lock file too).
  """
  workingdir = Path(filename).parent
  cargo_temporary = False
  if not os.path.exists(workingdir/"Cargo.toml"):
    cargo_temporary = True
    _create_cargo_toml(filename)
  try:
    yield workingdir/"Cargo.toml"
  finally:
    if cargo_temporary:
      sh.rm(workingdir/"Cargo.toml", workingdir/"Cargo.lock")

def _transfer_attrs_to_module(m, membername):
  """
  Transfer attributes of a member of a module to the module
  and delete the member.

  Attribute starting with "_" are not transfered.

  If the member does not exist, nothing is done, silently.
  """
  if hasattr(m, membername):
    member = getattr(m, membername)
    for k in list(member.__dict__.keys()):
      if not k.startswith("_"):
        setattr(m, k, getattr(member, k))
    delattr(m, membername)

def rust(filename, api_config = {}, verbose=False):
  """
  Import a Rust module written using pyo3, compiling it with maturin.

  If no Cargo.toml is present (in the parent directory of <filename>),
  one is created by automatically (see _create_cargo_toml
  for details). In this case Cargo.toml and Cargo.lock are
  deleted after running the method.

  The "target" subdirectory (in the parent directory of <filename>) is not
  removed, so that unnecessary recompilations are avoided. You may want to add
  "target" to .gitignore.

  Requirements:
  - rust compiler and cargo
  - pyo3 (the maturin binary must be in path)

  Constant definition mechanism:

    If a class "Constants" is defined in the module, all attributes of the class
    are moved to the module and the class is deleted (if import_constants is
    True); this mechanism is used in order to be able to define module-scoped
    constants.

    Example:

      #[pyclass] struct Constants {}
      #[pymethods]
        impl Constants { #[classattr] const FOO: &'static str = "bar"; }

    The name of the class ("Constants") can be changed setting the key
    rust_const_klass of api_config.

    If the key is set to an empty string, the constant definition
    mechanism is disabled.
  """
  workingdir = Path(filename).parent
  modulename = Path(filename).stem
  with _cargo_for(filename) as cargo:
    sh.maturin("build", release=True, m=cargo)
  libfilename = workingdir/f"{modulename}.so"
  sh.ln(f"target/release/lib{modulename}.so", libfilename, s=True, f=True)
  spec = importlib.util.spec_from_file_location(modulename, libfilename)
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  info = [f"# rust module {modulename} imported from file {filename}\n"]
  klass = api_config.get("rust_const_klass", "Constants")
  if len(klass) > 0:
    _transfer_attrs_to_module(m, klass)
    info += apply_api_config(m, modulename, api_config, True)
  else:
    info += apply_api_config(m, modulename, api_config, False)
    info.append("# constants definition mechanism disabled\n")
  if verbose:
    sys.stderr.write("".join(info))
  m.__lang__ = "rust"
  return m
