#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import yaml
import uuid
from datetime import datetime
import sys
import socket
import getpass

class Report():

  REASONS = ["new_entities", "new_attributes", "recompute"]

  def _init_plugin(self, plugin):
    if plugin is None:
      raise ValueError("A plugin module must be provided for creating a report")
    if not hasattr(plugin, "ID"):
      raise ValueError("The plugin module must have an ID attribute")
    if not hasattr(plugin, "VERSION"):
      raise ValueError("The plugin module must have a VERSION attribute")
    self.data["plugin_id"] = plugin.ID
    self.data["plugin_version"] = plugin.VERSION

  def _init_system(self, system):
    if system is None:
      system = socket.gethostname()
    self.data["system_id"] = system

  def _init_user(self, user):
    if user is None:
      user = getpass.getuser()
    self.data["user_id"] = user

  def _init_reason(self, reason):
    if reason is not None:
      if reason not in self.REASONS:
        raise ValueError("Invalid value for the computation reason; "+\
            "it must be one of: " + str(self.REASONS))
    self.data["reason"] = reason

  def _init_params(self, params):
    if params is not None:
      self.data["parameters"] = yaml.dump(params)

  def __init__(self, reportfile, plugin, user = None,
               system = None, reason = None, params = {}):
    self.data = {}
    self.rfile = reportfile
    self._init_plugin(plugin)
    self._init_system(system)
    self._init_user(user)
    self._init_reason(reason)
    self._init_params(params)
    self.data["uuid"] = uuid.uuid4().bytes
    self.data["time_start"] = str(datetime.now())
    self.n_steps = 0

  def step(self):
    self.n_steps += 1

  def finalize(self):
    self.data["time_end"] = str(datetime.now())
    self.data["n_units"] = self.n_steps
    self.data["comp_status"] = "completed"
    yaml.dump(self.data, self.rfile)
    self.rfile.flush()
    if self.rfile != sys.stderr:
      self.rfile.close()

  def error(self, err, unitname):
    self.data["time_end"] = str(datetime.now())
    self.data["n_units"] = self.n_steps
    self.data["comp_status"] = "aborted" if self.n_steps == 0 else "partial"
    remark = {}
    remark["error_input_unit"] = unitname
    remark["error_class"] = err.__class__.__name__
    remark["error_message"] = str(err)
    self.data["remarks"] = yaml.dump(remark)
    yaml.dump(self.data, self.rfile)
    self.rfile.flush()
    if self.rfile != sys.stderr:
      self.rfile.close()

