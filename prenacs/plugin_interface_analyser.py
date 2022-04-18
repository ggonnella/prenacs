#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Analyses the interface of a computation plugin for compliance
with the interface specification.
"""

import sys
import inspect
import multiplug
from loguru import logger

class PluginInterfaceAnalyser():

  def __init__(self, plugin, verbose=True, outfile=sys.stdout, colorize=True):
    self.plugin = multiplug.importer(plugin, verbose=verbose)
    self.had_errors = False
    log_level = "INFO" if verbose else "WARNING"
    logger.add(outfile, colorize=colorize, level=log_level)

  def _error(self, msg):
    logger.error(msg)
    self.had_errors = True

  def _info(self, msg):
    logger.info(msg)

  def _success(self, msg):
    logger.success(msg)

  def _check_compute_function(self):
    if not hasattr(self.plugin, "compute"):
      self._error("plugin does not provide a compute function")
    else:
      self._success("plugin provides a compute function")
    if self.plugin.__lang__ == "python":
      compute_spec = inspect.getfullargspec(self.plugin.compute)
      if compute_spec.varargs is not None:
        self._error(\
            "plugin.compute() accepts variable positional arguments")
      if not hasattr(self.plugin, "initialize"):
        if len(compute_spec.args) != 1:
          self._error(\
              "plugin.compute() does not accept a single positional argument")
      else:
        if (len(compute_spec.args) != 2) or (compute_spec.args[1] != "state"):
          self._error(\
              "plugin.compute() in plugin with initialize function "+\
              "does not accept a state keyword argument")
      if compute_spec.varkw is None:
        self._error(\
            "plugin.compute() does not accept variable keywords arguments")

  def _check_initialize_function(self):
    if hasattr(self.plugin, "initialize"):
      self._success("plugin provides an initialize function")
    else:
      self._info("plugin does not provide an initialize function")
    init_spec = inspect.getfullargspec(self.plugin.initialize)
    if (init_spec.varargs is not None) or (len(init_spec.args) > 0):
      self._error(\
          "plugin.initialize() accepts positional arguments")
    if init_spec.varkw is None:
      self._error(\
          "plugin.initialize() does not accept variable keywords arguments")

  def _check_finalize_function(self):
    if hasattr(self.plugin, "finalize"):
      self._success("plugin provides a finalize function")
      if not hasattr(self.plugin, "initialize"):
        self._error(\
              "plugin.finalize() defined in plugin without plugin.initialize()")
    else:
      self._info("plugin does not provide a finalize function")
    f_spec = inspect.getfullargspec(self.plugin.finalize)
    if f_spec.varargs is not None:
      self._error(\
          "plugin.finalize() accepts variable positional arguments")
    if len(f_spec.args) != 1:
      self._error(\
          "plugin.finalize() does not accept a single positional argument")
    if f_spec.varkw is not None:
      self._error(\
          "plugin.initialize() accepts variable keywords arguments")

  def _check_mandatory_constants(self):
    for const in ["ID", "VERSION", "INPUT", "OUTPUT"]:
      if not hasattr(self.plugin, const):
        self._error(\
            f"plugin does not define a constant named '{const}'")
      else:
        self._success(f"plugin defines a constant named '{const}'")

  def _check_string_constants(self):
    for const, maxlen in {"ID": 256, "VERSION": 64, "INPUT": 512,
                          "METHOD": 4096, "IMPLEMENTATION": 4096,
                          "REQ_SOFTWARE": 4096, "REQ_HARDWARE": 4096,
                          "ADVICE": 4096}.items():
      if hasattr(self.plugin, const):
        v = getattr(self.plugin, const)
        if v is not None:
          if not isinstance(v, str):
            self._error(f"plugin.{const} must be a string")
          elif len(v) > maxlen:
            self._error(f"plugin.{const} length must <= {maxlen}")
          else:
            self._success(f"plugin.{const} type and format is valid")

  def _check_output_constant(self, definitions):
    if hasattr(self.plugin, "OUTPUT"):
      if not isinstance(self.plugin.OUTPUT, list):
        self._error("plugin.OUTPUT is not a list")
      notstr = [key for key in self.plugin.OUTPUT if not isinstance(key, str)]
      if notstr:
        self._error(\
            f"plugin.OUTPUT non-string elements found: {notstr}")
      else:
        self._success("all plugin.OUTPUT elements are strings")
      if definitions:
        notin = [key for key in self.plugin.OUTPUT \
                  if key not in notstr and key not in definitions]
        if notin:
          self._error("plugin.OUTPUT elements "+\
              f"not found in the attributes definitions file: {notin}")
        else:
          self._success("all plugin.OUTPUT elements are "+\
                "present in the attributes definitions file")
      else:
        self._info("no attributes definitions file provided")

  def _check_parameters_constant(self):
    if hasattr(self.plugin, "PARAMETERS") and \
        self.plugin.PARAMETERS is not None:
      if not isinstance(self.plugin.PARAMETERS, list):
        self._error("plugin.PARAMETERS is not a list")
      for element in self.plugin.PARAMETERS:
        if not isinstance(element, tuple) and not isinstance(element, list):
          self._error(\
              f"plugin.PARAMETER element not tuple: {element}")
        elif len(element) != 4:
          self._error(\
              f"plugin.PARAMETER element tuple length is not 4: {element}")
        else:
          for s in element:
            if not isinstance(s, str):
              self._error(\
                "plugin.PARAMETER tuple element is not a "+\
                f"string: {s} of {element}")

  def run(self, definitions=None):
    if self.plugin.__lang__ != "python":
      self._info("signature of plugin functions not analyzed, "+\
          " since it is a {} plugin", self.plugin.__lang__)
    self._check_compute_function()
    self._check_initialize_function()
    self._check_finalize_function()
    self._check_mandatory_constants()
    self._check_string_constants()
    self._check_output_constant(definitions)
    self._check_parameters_constant()
    return 1 if self.had_errors else 0

