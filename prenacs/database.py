#
# (c) 2021-2023 Giorgio Gonnella, University of Goettingen, Germany
#
from prenacs.dbschema.attribute_definition import AttributeDefinition
from prenacs.dbschema.plugin_description import PluginDescription
from prenacs.dbschema.computation_report import ComputationReport

DEFAULT_AVT_PREFIX = "prenacs_attribute_value_t"

def create(connection):
  """
  Creates the necessary tables in the database for all classes of this module.

  Args:
      connection: A SQLAlchemy connection object to the database.
  """
  AttributeDefinition.metadata.create_all(connection)
  PluginDescription.metadata.create_all(connection)
  ComputationReport.metadata.create_all(connection)

def drop(connection, attribute_value_tables=None):
  """
  Drops the tables in the database.

  Args:
      connection: A SQLAlchemy connection object to the database.
      attribute_value_tables: Optional.
         A SQLAlchemy Table object for the attribute value tables to be dropped.
  """
  AttributeDefinition.metadata.drop_all(connection)
  PluginDescription.metadata.drop_all(connection)
  ComputationReport.metadata.drop_all(connection)
  if attribute_value_tables:
    attribute_value_tables.drop_all()
