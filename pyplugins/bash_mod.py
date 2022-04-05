import sh
import importlib
from pyplugins.error import InterfaceRequirementError
from pathlib import Path
import sys

def _has_constant(filename, cname):
  try:
    sh.bash("-c", f". {filename}; [ -z ${{{cname}+x}} ]")
    return False
  except sh.ErrorReturnCode_1:
    return True

def _get_constant(filename, cname, required):
  if _has_constant(filename, cname):
    return sh.bash("-c", f". {filename}; echo -e ${cname}").rstrip()
  elif required:
    raise InterfaceRequirementError(
            f"Constant '{cname}' not defined in Bash module '{filename}'")
  else:
    return None

def _import_constants(m, filename, api_config, required):
  imported = {True: [], False: []}
  for key in api_config.get("constants", {}).keys():
    for cname in api_config["constants"][key]:
      if key == "list" or key == "nested":
        cvalue = _get_constant(filename, f"{{{cname}[@]}}", required)
      else:
        cvalue = _get_constant(filename, cname, required)
      if cvalue is None or key == "strings":
        setattr(m, cname, cvalue)
      elif key == "lists":
        setattr(m, cname, cvalue.split(" "))
      elif key == "nested":
        setattr(m, cname, [e.split("\t") for e in cvalue.split("\n")])
      imported[cvalue is not None].append(cname)
  return imported

def _has_function(filename, funcname):
  try:
    sh.bash("-c", f". {filename}; [[ $(type -t {funcname}) == function ]]")
    return True
  except sh.ErrorReturnCode_1:
    return False

def _wrap_function(filename, funcname, required):
  if _has_function(filename, funcname):
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
  elif required:
    raise InterfaceRequirementError(
            f"Function '{funcname}' not defined in Bash module '{filename}'")
  else:
    return None

def _import_functions(m, filename, api_config, required):
  imported = {True: [], False: []}
  for funcname in api_config.get("functions", []):
    f=_wrap_function(filename, funcname, required)
    setattr(m, funcname, f)
    imported[f is not None].append(funcname)
  return imported

def bash(filename, api_config = {}, verbose = True):
  """
  Creates a Python module which wraps a shell script.
  The functions and constants to be imported must be listed in the api_config
  dictionary (see library documentation for the api_config syntax).
  """
  modulename=Path(filename).stem
  spec=importlib.machinery.ModuleSpec(modulename, None)
  m = importlib.util.module_from_spec(spec)

  imported_r_f = \
    _import_functions(m, filename, api_config.get("required", {}), True)
  imported_o_f = \
    _import_functions(m, filename, api_config.get("optional", {}), False)
  imported_r_c = \
    _import_constants(m, filename, api_config.get("required", {}), True)
  imported_o_c = \
    _import_constants(m, filename, api_config.get("optional", {}), False)

  if verbose:
    sys.stderr.write(
        f"# bash module {modulename} imported from file {filename}\n")
    found_f = imported_r_f[True] + imported_o_f[True]
    not_found_f = imported_o_f[False]
    if len(found_f) > 0:
      sys.stderr.write("# imported functions: {}\n".\
              format(", ".join(found_f)))
    if len(not_found_f) > 0:
      sys.stderr.write("# optional functions not defined (set to None): {}\n".\
              format(", ".join(not_found_f)))
    found_c = imported_r_c[True] + imported_o_c[True]
    not_found_c = imported_o_c[False]
    if len(found_c) > 0:
      sys.stderr.write( "# imported constants: {}\n".\
          format(", ".join(found_c)))
    if len(not_found_c) > 0:
      sys.stderr.write( "# optional constants not defined (set to None): {}\n".\
          format(", ".join(not_found_c)))
  m.__lang__ = "bash"
  return m
