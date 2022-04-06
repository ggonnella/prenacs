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
from multiplug.plugin_api import enforce_plugin_api

RUST_CONST_CLS = "Constants"

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

def _import_constants(m, membername):
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

def rust(filename, verbose=False, req_const=[], opt_const=[],
         req_func=[],  opt_func=[], const_cls=RUST_CONST_CLS):
  """
  Import a Rust module written using pyo3, compiling it with maturin.

  If no Cargo.toml is present (in the parent directory of <filename>),
  one is created by automatically (see _create_cargo_toml
  for details). In this case Cargo.toml and Cargo.lock are
  deleted after running the method.

  The "target" subdirectory (in the parent directory of <filename>) is not
  removed, so that unnecessary recompilations are avoided. You may want to add
  "target" to .gitignore.
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
  if len(const_cls) > 0:
    _import_constants(m, const_cls)
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
  m.__lang__ = "rust"
  return m
