PLUGIN_METADATA_SCALAR_KEYS = ["ID", "VERSION", "INPUT",
                               "METHOD", "IMPLEMENTATION", "REQ_SOFTWARE",
                               "REQ_HARDWARE", "ADVICE"]
PLUGIN_METADATA_LIST_KEYS = ["OUTPUT"]
PLUGIN_METADATA_TUPLES_LIST_KEYS = ["PARAMETERS"]

def check_metadata_keys_defined():
  """
  Check that plugin metadata key definitions have been provided.
  """
  if "PLUGIN_METADATA_SCALAR_KEYS" and "PLUGIN_METADATA_LIST_KEYS" and \
      "PLUGIN_METADATA_TUPLES_LIST_KEYS" not in globals():
    raise Exception("Plugin metadata keys not defined.\n" \
                "Please define at least one of the following constants:\n" \
                "PLUGIN_METADATA_SCALAR_KEYS, PLUGIN_METADATA_LIST_KEYS, " \
                "PLUGIN_METADATA_TUPLES_LIST_KEYS\n")

def metadata_str(plugin):
  """
  Returns a dictionary with string representations of the metadata of the
  plugin, based on constants defined in the plugin code.
  """
  check_metadata_keys_defined()
  result_s = {k.lower(): getattr(plugin, k) for \
      k in PLUGIN_METADATA_SCALAR_KEYS if hasattr(plugin, k)}

  result_l = {k.lower(): getattr(plugin, k) for \
      k in PLUGIN_METADATA_LIST_KEYS if hasattr(plugin, k)}
  for k in result_l.keys():
    result_l[k] = ",".join([str(x) for x in result_l[k]])

  result_t = {k.lower(): getattr(plugin, k) for \
      k in PLUGIN_METADATA_TUPLES_LIST_KEYS if hasattr(plugin, k)}
  for k in result_t.keys():
    result_t[k] = ";".join([",".join(str(x)) for x in result_t[k]])

  return {**result_s, **result_l, **result_t}
