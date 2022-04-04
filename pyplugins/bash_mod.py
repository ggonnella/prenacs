import sh
import imp
import error
from pathlib import Path

def _has_constant(filename, cname):
  try:
    sh.bash("-c", f". {filename}; [ -z ${{{cname}+x}} ]")
    return True
  except sh.ErrorReturnCode_1:
    return False

def _get_constant(filename, cname, required):
  if _has_constant(filename, cname):
    return sh.bash("-c", f". {filename}; echo -e ${cname}").rstrip()
  elif required:
    raise ConstantMissingError(
            f"Constant '{cname}' not defined in Bash module '{filename}'")
  else:
    return None

def _import_constants(m, filename, api_config, required):
  for key in api_config["constants"].keys():
    for cname in api_config["constants"][key]:
      if key == "list" or key == "nested":
        cname = f"{{{cname}[@]}}"
      cvalue = _get_constant(filename, cname, required)
    if cvalue is not None:
      if key == "strings":
        setattr(m, cname, cvalue)
      elif key == "lists":
        setattr(m, cname, cvalue.split(" "))
      elif key == "nested":
        setattr(m, cname, [e.split("\t") for e in cvalue.split("\n")])

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
    raise FunctionMissingError(
            f"Function '{funcname}' not defined in Bash module '{filename}'")
  else:
    return None

def _import_functions(m, filename, api_config, required):
  imported = []
  for funcname in api_config["functions"]:
    f=_wrap_function(filename, funcname, required)
    if f is not None:
      setattr(m, funcname, f)
      imported.append(funcname)
  return imported

def bash(filename, api_config = {}, verbose = False):
  """
  Creates a Python module which wraps a shell script.
  The functions and constants to be imported must be listed in the api_config
  dictionary.

  """
  modulename=Path(filename).stem
  m=imp.new_module(modulename)

  required_functions = _import_functions(
      m, filename, api_config["required"], True)
  optional_functions = _import_functions(
      m, filename, api_config["optional"], False)
  required_constants = _import_constants(
      m, filename, api_config["required"], True)
  optional_constants = _import_constants(
      m, filename, api_config["optional"], False)

  if verbose:
    sys.stderr.write(
        f"# bash module {modulename} imported from file {filename}\n")
    if len(required_functions) > 0:
      sys.stderr.write(
          "# imported required functions: {}\n".\
              format(", ".join(required_functions)))
    if len(optional_functions) > 0:
      sys.stderr.write(
          "# imported optional functions: {}\n".\
              format(", ".join(optional_functions)))
    if len(required_constants) > 0:
      sys.stderr.write(
          "# imported required constants: {}\n".\
              format(", ".join(required_constants)))
    if len(optional_constants) > 0:
      sys.stderr.write(
          "# imported optional constants: {}\n".\
              format(", ".join(optional_constants)))
  m.__lang__ = "bash"
  return m
