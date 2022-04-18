#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#
from prenacs.dbschema.attribute_definition import AttributeDefinition
from prenacs.dbschema.plugin_description import PluginDescription
from prenacs.dbschema.computation_report import ComputationReport

DEFAULT_AVT_PREFIX = "prenacs_attribute_value_t"

def create(connection):
  AttributeDefinition.metadata.create_all(connection)
  PluginDescription.metadata.create_all(connection)
  ComputationReport.metadata.create_all(connection)

def drop(connection, attribute_value_tables=None):
  AttributeDefinition.metadata.drop_all(connection)
  PluginDescription.metadata.drop_all(connection)
  ComputationReport.metadata.drop_all(connection)
  if attribute_value_tables:
    attribute_value_tables.drop_all()
