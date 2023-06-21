#
# (c) 2021-2023 Giorgio Gonnella, University of Goettingen, Germany
#

import multiplug
import yaml
import os
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from prenacs import plugins_helper, PluginDescription, ComputationReport

class ResultsLoader():
  """
  Loads computation results and reports into a database.

  It provides methods to process the plugin description, the computation report,
  and the results file, and store them in the database. The class also checks
  for consistency between the plugin metadata, the computation report, and the
  results file, and raises an error if inconsistencies are found.

  Attributes:
    plugin: A `PluginDescription` object representing the plugin metadata.
    connection: A SQLAlchemy `Connection` object representing the database
      connection.
    avt: An `AttributeValueTables` object representing the attribute-value
      tables of the database.
  """

  @staticmethod
  def _different_fields(obj1, obj2):
    result = []
    for c in inspect(obj1).mapper.c:
      v1 = getattr(obj1, c.name)
      v2 = getattr(obj2, c.name)
      if v1 != v2:
        if hasattr(c, "default"):
          if (v1 is None and v2 == c.default.arg) or \
             (v2 is None and v1 == c.default.arg):
            continue
        result.append((c, v1, v2))
    return result

  def _insert_update_or_compare(self, session, klass, newdata,
                                primarykeys, replace, msg):
    newrow = klass(**newdata)
    oldrow = session.get(klass, primarykeys)
    if oldrow:
      if replace:
        session.merge(newrow)
      else:
        diff = self._different_fields(newrow, oldrow)
        if diff:
          raise RuntimeError(f"{msg}\nDifferences:\n"+\
          "\n".join([f"  new {c}: {v1}\n  old {c}: {v2}" \
                     for c, v1, v2 in diff]))
    else:
      session.add(newrow)

  def _process_plugin_description(self, session, plugin, replace):
    self._insert_update_or_compare(session, PluginDescription,
        plugins_helper.plugin_metadata_str(plugin),
        [self.plugin.ID, self.plugin.VERSION], replace,
        "Plugin metadata changed, without a version change\n"+\
        "Please either set the replace-plugin-record option or increase the "+\
        "plugin version number")

  def __init__(self, attribute_value_tables, plugin_fn,
               replace_plugin_record=False, verbose=False):
    self.plugin = multiplug.importer(plugin_fn, verbose=verbose,
                                     **plugins_helper.COMPUTE_PLUGIN_INTERFACE)
    self.connection = attribute_value_tables.connectable
    self.avt = attribute_value_tables
    session = Session(bind=self.connection)
    self._process_plugin_description(session, self.plugin,
                                     replace_plugin_record)
    session.commit()

  def _check_plugin_key(self, report_data):
    for key in ["ID", "VERSION"]:
      report_value = report_data["plugin_"+key.lower()]
      exp_value = getattr(self.plugin, key)
      if report_value != exp_value:
        raise RuntimeError(f"Plugin {key} mismatch\n"+\
            f"{key} from the plugin module: {exp_value}\n"+\
            f"{key} from the computation report: {report_value}\n")

  def _process_computation_report(self, report_file, replace):
    session = Session(bind=self.connection)
    with open(report_file) as report:
      report_data = yaml.safe_load(report)
    self._check_plugin_key(report_data)
    uuid = report_data["uuid"]
    self._insert_update_or_compare(session,\
        ComputationReport, report_data, uuid,
        replace, "A computation report with the same ID "+\
            "({uuid}) "+\
            "was already stored in the database\n"+\
            "Please set the replace-report-record option or "+\
            "use a different computation report ID.")
    session.commit()
    return uuid

def run(self, results_file, report_file, replace_report_record=False,
    verbose=False):
  """
  Loads computation results and reports into a database.

  It first checks that the results file is not empty, and then processes the
  computation report to extract the computation ID. Finally, it loads the
  computation results into the database using the `load_computation` method of
  the `AttributeValueTables` object.

  Args:
    results_file (str): The path to the file containing the computation
      results.
    report_file (str): The path to the file containing the computation
      report.
    replace_report_record (bool, optional): If `True`, replaces any
      existing computation report with the same ID in the database.
      Defaults to `False`.
    verbose (bool, optional): If `True`, prints additional information
      during the loading process. Defaults to `False`.

  Raises:
    RuntimeError: If the results file is empty.
  """
  def run(self, results_file, report_file, replace_report_record=False,
          verbose=False):
    if os.stat(results_file).st_size == 0:
      raise RuntimeError("The results file is empty")
    else:
      computation_id = self._process_computation_report(\
                         report_file, replace_report_record)
      self.avt.load_computation(computation_id,
                                self.plugin.OUTPUT,
                                results_file)

