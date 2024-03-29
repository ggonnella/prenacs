#
# (c) 2021-2023 Giorgio Gonnella, University of Goettingen, Germany
#
COMPUTE_PLUGIN_INTERFACE = {}
COMPUTE_PLUGIN_INTERFACE["req_func"] = ["compute"]
COMPUTE_PLUGIN_INTERFACE["opt_func"] = ["initialize", "finalize"]
COMPUTE_PLUGIN_INTERFACE["req_const"] = ["ID", "VERSION", "INPUT", "OUTPUT"]
COMPUTE_PLUGIN_INTERFACE["opt_const"] = ["PARAMETERS", "METHOD",
                                         "IMPLEMENTATION", "ADVICE",
                                         "REQ_SOFTWARE", "REQ_HARDWARE"]

IDPROC_PLUGIN_INTERFACE = {}
IDPROC_PLUGIN_INTERFACE["req_func"] = ["compute_id"]

def plugin_metadata_str(plugin):
  """
  Collects the metadata of a plugin.

  Args:
    plugin: a plugin module

  Returns:
    A dictionary with string values, containing the metadata of the plugin.
  """
  metadata_keys = COMPUTE_PLUGIN_INTERFACE["req_const"] + \
                  COMPUTE_PLUGIN_INTERFACE["opt_const"]
  result = {k.lower(): getattr(plugin, k) \
              for k in metadata_keys if hasattr(plugin, k)}
  if "output" in result and result["output"] is not None:
    result["output"] = ",".join(result["output"])
  if "parameters" in result and result["parameters"] is not None:
    result["parameters"] = ";".join([",".join(e) for e in result["parameters"]])
  return result

