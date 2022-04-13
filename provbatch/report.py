import yaml
import uuid
from datetime import datetime

class Report():

  @classmethod
  def __init__(self, rfile, plugin, user, system, reason, params):
    self.rfile = rfile
    self.data = {}
    self.data["plugin_id"] = plugin.ID
    self.data["plugin_version"] = plugin.VERSION
    self.data["system_id"] = system
    self.data["user_id"] = user
    if reason:
      self.data["reason"] = reason
    if params:
      self.data["parameters"] = yaml.dump(params)
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

