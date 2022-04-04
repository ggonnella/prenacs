import sh
import imp
from pyplugins.error import InterfaceRequirementError
from pathlib import Path

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
  for key in api_config["constants"].keys():
    for cname in api_config["constants"][key]:
      if key == "list" or key == "nested":
        cname = f"{{{cname}[@]}}"
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
      retvals = \
          sh.bash("-c", f". {filename}; {funcname} {args_str} {kwargs_str}").\
                 rstrip().split("\n", 1)
      if len(retvals) == 1:
        retvals.append("")
      return (retvals[0].split("\t"), retvals[1].split("\n"))
    return _fn
  elif required:
    raise InterfaceRequirementError(
            f"Function '{funcname}' not defined in Bash module '{filename}'")
  else:
    return None

def _import_functions(m, filename, api_config, required):
  imported = {True: [], False: []}
  for funcname in api_config["functions"]:
    f=_wrap_function(filename, funcname, required)
    setattr(m, funcname, f)
    imported[f is not None].append(funcname)
  return imported

def bash(filename, api_config = {}, verbose = False):
  """
  Creates a Python module which wraps a shell script.
  The functions and constants to be imported must be listed in the api_config
  dictionary (see library documentation for the api_config syntax).
  """
  modulename=Path(filename).stem
  m=imp.new_module(modulename)

  imported_r_f = _import_functions(m, filename, api_config["required"], True)
  imported_o_f = _import_functions(m, filename, api_config["optional"], False)
  imported_r_c = _import_constants(m, filename, api_config["required"], True)
  imported_o_c = _import_constants(m, filename, api_config["optional"], False)

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
