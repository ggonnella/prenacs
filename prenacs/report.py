#
# (c) 2021-2023 Giorgio Gonnella, University of Goettingen, Germany
#

import yaml
import uuid
from datetime import datetime
import sys
import socket
import getpass

class Report():
  """
  A class for creating and writing reports to a file.

  Attributes:
    data (dict): A dictionary containing the report data.
    rfile (file): The file object to write the report to.
    n_steps (int): The number of steps in the report.
  """

  REASONS = ["new_entities", "new_attributes", "recompute"]
  """
    A list of valid reasons for running a computation.

    The reasons are:
      - new_entities: add new entities to the database
      - new_attributes: add new attributes to the database
      - recompute: recompute attributes for existing entities
                   (e.g. with a different parameter setting or method)
  """

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
    """
    Increments the number of steps in the report by 1.
    """
    self.n_steps += 1

  def finalize(self):
      """
      Finalizes the report by adding the end time, number of units, and
      computation status to the report data. Then, it dumps the report data to
      the report file, flushes the file, and closes it.
      """
      self.data["time_end"] = str(datetime.now())
      self.data["n_units"] = self.n_steps
      self.data["comp_status"] = "completed"
      yaml.dump(self.data, self.rfile)
      self.rfile.flush()
      if self.rfile != sys.stderr:
        self.rfile.close()

  def error(self, err, unitname):
    """
    Adds an error message to the report data and finalizes the report.

    Args:
      err (Exception): The exception object containing the error message.
      unitname (str): The name of the unit where the error occurred.
    """
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

