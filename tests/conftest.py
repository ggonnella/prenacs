#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from attrtables import AttributeValueTables
import prenacs.database
from prenacs import AttributeDefinition
import yaml

VERBOSE_CONNECTION = True
DEBUG_MODE = False

def connection_data_from_config():
  # if config.yaml does not exist, raise an error
  config_file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
  if not os.path.exists(config_file_path):
    raise FileNotFoundError(\
        'Connection configuration file config.yaml not found')
  with open(config_file_path) as f:
    config = yaml.safe_load(f)
  return config

@pytest.fixture(scope="session")
def connection_string():
  config = connection_data_from_config()
  args = {k: v for k, v in config.items() if k in ['drivername',
                                           'host', 'port', 'database',
                                           'username', 'password']}
  if 'socket' in config:
    args['query'] = {'unix_socket': config['socket']}
  return URL.create(**args)

@pytest.fixture()
def connection_args():
  config = connection_data_from_config()
  return [config['username'], config['password'],
          config['database'], config['socket']]

def drop_all(connection):
  avt = AttributeValueTables(connection,
                             attrdef_class=AttributeDefinition,
                             tablename_prefix="pvt_attribute_value_t")
  prenacs.database.drop(connection, avt)

@pytest.fixture()
def connection_creator(connection_string):
  def get_connection():
    engine = create_engine(connection_string, echo=VERBOSE_CONNECTION,
                           future=True)
    connection = engine.connect()
    return connection
  return get_connection

@pytest.fixture(scope="session")
def connection(connection_string):
  engine = create_engine(connection_string, echo=VERBOSE_CONNECTION,
                         future=True)
  with engine.connect() as conn:
    drop_all(conn)
    conn.commit()
    prenacs.database.create(conn)
    conn.commit()
    yield conn
    if not DEBUG_MODE:
      drop_all(conn)
    conn.commit()
