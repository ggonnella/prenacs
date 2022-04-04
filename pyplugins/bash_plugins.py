import sh
import imp
from pathlib import Path
from pyplugins.plugins import check_metadata_keys_defined

PLUGIN_FUNCTIONS = ["compute"]

PLUGIN_METADATA_SCALAR_KEYS = ["ID", "VERSION", "INPUT", "METHOD",
                               "IMPLEMENTATION", "REQ_SOFTWARE", "REQ_HARDWARE",
                               "ADVICE"]
PLUGIN_METADATA_LIST_KEYS = ["OUTPUT"]
PLUGIN_METADATA_TUPLES_LIST_KEYS = ["PARAMETERS"]

def _get_constant(filename, cname):
  return sh.bash("-c", f". {filename}; echo -e ${cname}").rstrip()

def _import_constants(m, filename):
  check_metadata_keys_defined()
  for cname in PLUGIN_METADATA_SCALAR_KEYS:
    setattr(m, cname, _get_constant(filename, cname))
  for cname in PLUGIN_METADATA_LIST_KEYS:
    setattr(m, cname, _get_constant(filename, "{"+cname+"[@]}").split(" "))
  for cname in PLUGIN_METADATA_TUPLES_LIST_KEYS:
    setattr(m, cname,
        [e.split("\t") for e in _get_constant(filename,
          "{"+cname+"[@]}").split("\n")])

def _def_function(filename, funcname):
  def _fn(*args, **kwargs):
    args_str=" ".join(args)
    kwargs_str=" ".join([f"{k}={v}" for k, v in kwargs.items()])
    retvals = \
        sh.bash("-c", f". {filename}; {funcname} {args_str} {kwargs_str}").\
               rstrip().split("\n", 1)
    if len(retvals) == 1:
      retvals.append("")
    return (retvals[0].split("\t"), retvals[1].split("\n"))
  return _fn

def check_plugin_functions_defined():
  """
  Check that a plugin functions list have been provided.
  """
  if "PLUGIN_FUNCTIONS" not in globals():
    raise Exception("Plugin function list not defined.\n" \
                "Please define the PLUGIN_FUNCTIONS constant.\n")

def bash(filename, verbose = False, import_constants = True):
  """
  Creates a Python module which wraps a shell script.

  The functions to be imported must be listed in the PLUGIN_FUNCTIONS
  constant.

  If import_constants is true, constants listed in PLUGIN_METADATA_SCALAR_KEYS,
  PLUGIN_METADATA_LIST_KEYS, PLUGIN_METADATA_TUPLES_LIST_KEYS are imported.
  """
  check_plugin_functions_defined()

  modulename=Path(filename).stem
  m=imp.new_module(modulename)

  for funcname in PLUGIN_FUNCTIONS:
    setattr(m, funcname, _def_function(filename, funcname))

  if import_constants:
    _import_constants(m, filename)

  if verbose:
    sys.stderr.write(
        f"# bash module {modulename} imported from file {filename}\n")
  m.__lang__ = "bash"
  return m
