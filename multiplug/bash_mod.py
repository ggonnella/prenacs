import sh
import importlib
from multiplug.error import InterfaceRequirementError
from pathlib import Path
import sys
from multiplug.plugin_api import enforce_plugin_api

def _is_array(filename, cname):
  try:
    sh.bash("-c", f". {filename}; [[ \"$(declare -p {cname})\" "+\
            "=~ \"declare -a\" ]]")
    return True
  except sh.ErrorReturnCode_1:
    return False

def _get_constant(filename, cname):
  is_array = _is_array(filename, cname)
  if is_array:
    value = sh.bash("-c", f". {filename}; " +\
       f"for elem in ${{{cname}[@]}}; do echo -e $elem; done").\
            rstrip().split("\n")
    has_tabs = any("\t" in v for v in value)
    if has_tabs:
      value = [v.split("\t") for v in value]
  else:
    value = sh.bash("-c", f". {filename}; echo -e ${cname}").rstrip()
  return value

def _list_attributes(m, filename, verbose):
  before = sh.mktemp().rstrip()
  after = sh.mktemp().rstrip()
  sh.bash("-c", f"set > {before}")
  sh.bash("-c", f". {filename}; set > {after}")
  varnames=set(sh.bash("-c", f"diff {before} {after} |"+\
      "grep '^>' | cut -c3- | grep '^[A-Za-z]' | grep '=' | "+\
      "grep -o '^[^=]*'; true").rstrip().split("\n"))
  funcnames=set(sh.bash("-c", f"diff {before} {after} |"+\
      "grep '^>' | cut -c3- | grep '^[A-Za-z]' | grep -v '=' | grep '()' |"+\
      "grep -o '^[A-Za-z][A-Za-z0-9_]*'; true").rstrip().split("\n"))
  varnames -= {"BASH_REMATCH", "COMP_WORDBREAKS", "BASH_EXECUTION_STRING",
      "PIPESTATUS"}
  sh.rm(before)
  sh.rm(after)
  return varnames, funcnames


def _wrap_function(filename, funcname):
  def _fn(*args, **kwargs):
    args_str=" ".join(args)
    kwargs_str=" ".join([f"{k}={v}" for k, v in kwargs.items()])
    retval = str(sh.bash("-c",
      f". {filename}; {funcname} {args_str} {kwargs_str}", _err=sys.stderr))
    if len(retval) > 0 and retval[-1] == "\n":
      retval = retval[:-1]
    has_newlines = "\n" in retval
    has_tabs = "\t" in retval
    if has_newlines and has_tabs:
      retval = [l.split("\t") for l in retval.split("\n")]
    elif has_newlines:
      retval = retval.split("\n")
    elif has_tabs:
      retval = retval.split("\t")
    return retval
  return _fn

def bash(filename, verbose=False, req_const=[], opt_const=[],
                                  req_func=[],  opt_func=[]):
  """
  Creates a Python module which wraps a shell script.
  """
  modulename=Path(filename).stem
  spec=importlib.machinery.ModuleSpec(modulename, None)
  m = importlib.util.module_from_spec(spec)

  varnames, funcnames = _list_attributes(m, filename, verbose)
  for v in varnames:
    setattr(m, v, _get_constant(filename, v))
  for f in funcnames:
    setattr(m, f, _wrap_function(filename, f))
  info = [f"# bash module {modulename} imported from file {filename}\n"]
  info += enforce_plugin_api(m, modulename, req_const=req_const,
                           opt_const=opt_const, req_func=req_func,
                           opt_func=opt_func)
  if verbose:
    sys.stderr.write("".join(info))
  m.__lang__ = "bash"
  return m
