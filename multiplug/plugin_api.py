#
# (c) Giorgio Gonnella, 2021-2022
#
# Check the API of a plugin module
#

from multiplug.error import InterfaceRequirementError

def _enforce_section(m, mname, units, unit_type, required):
  found_units = {True: [], False: []}
  for u in units:
    found = hasattr(m, u)
    if not found:
      if required:
        raise InterfaceRequirementError(
            "Plugin module '{}' does not define the required {} '{}'".format(
                mname, unit_type, u))
      else:
        setattr(m, u, None)
    found_units[found].append(u)
  info = []
  lbl = "required" if required else "optional"
  info.append("# imported {} {}: {}\n".format(lbl, unit_type,
                                              ", ".join(found_units[True])))
  info.append("# non defined {} {} (set to None): {}\n".format(lbl, unit_type,
                                                  ", ".join(found_units[False])))
  return info

def enforce_plugin_api(m, mname, req_const=[], req_func=[],
                                 opt_const=[], opt_func=[]):
  """
  - checks if required functions and constants are defined in the module
  - if optional functions and constants are not defined, they are set to None
  - messages showing the list of found and not found
    functions and constants are collected in the returned list
  """
  info = _enforce_section(m, mname, req_const, "constant", True)
  info += _enforce_section(m, mname, opt_const, "constant", False)
  info += _enforce_section(m, mname, req_func, "function", True)
  info += _enforce_section(m, mname, opt_func, "function", False)
  return info

