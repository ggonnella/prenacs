#
# (c) Giorgio Gonnella, 2021-2022
#

from pyplugins.error import InterfaceRequirementError

def _join_values(d):
  retval = []
  for k,v in d.items():
    retval += v
  return retval

def _apply_api_config_section(m, modulename, api_config, section_name):
  imported_units = {True: [], False: []}

  required_units = api_config.get("required", {}).get(section_name, [])
  if section_name == "constants":
    required_units = _join_values(required_units)
  for unit_name in required_units:
    if not hasattr(m, unit_name):
      raise InterfaceRequirementError(
          "Module '{}' does not define all required {}, missing: '{}'".\
          format(modulename, section_name, unit_name))
    imported_units[True].append(unit_name)

  optional_units = api_config.get("optional", {}).get(section_name, [])
  if section_name == "constants":
    optional_units = _join_values(optional_units)
  for unit_name in optional_units:
    imported_units[hasattr(m, unit_name)].append(unit_name)
    if not hasattr(m, unit_name):
      setattr(m, unit_name, None)

  info = []
  info.append("# imported {}: {}\n".format(section_name, imported_units[True]))
  info.append("# non defined {} (set to None): {}\n".\
        format(section_name, imported_units[False]))
  return info

def apply_api_config(m, modulename, api_config, handle_constants=True):
  """
  Apply API configuration to a Python module
  - checks if required functions and constants are defined in the module
  - if optional functions and constants are not defined, they are set to None
  - messages showing the list of found and not found
    functions and constants are collected in the returned list
  - if "handle_constants" is set to False, only functions are handled
  """
  info = _apply_api_config_section(m, modulename, api_config, "functions")
  if handle_constants:
    info += _apply_api_config_section(m, modulename, api_config, "constants")
  return info

