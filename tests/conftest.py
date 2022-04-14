#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import pytest
from collections import defaultdict
import os
from sqlalchemy import create_engine, inspect, exc
from sqlalchemy.orm import Session
from sqlalchemy.engine.url import URL
from attrtables import AttributeValueTables
import provbatch.database
from provbatch import AttributeDefinition
import yaml

VERBOSE_CONNECTION = True
DEBUG_MODE = False

@pytest.fixture(scope="session")
def connection_string():
  # if config.yaml does not exist, raise an error
  config_file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
  if not os.path.exists(config_file_path):
    raise FileNotFoundError(\
        'Connection configuration file config.yaml not found')
  with open(config_file_path) as f:
    config = yaml.safe_load(f)
  args = {k: v for k, v in config.items() if k in ['drivername',
                                           'host', 'port', 'database',
                                           'username', 'password']}
  if 'socket' in config:
    args['query'] = {'unix_socket': config['socket']}
  return URL.create(**args)

def drop_all(connection):
  avt = AttributeValueTables(connection,
                             attrdef_class=AttributeDefinition,
                             tablename_prefix="pr_attribute_value_t")
  provbatch.database.drop(connection, avt)

@pytest.fixture(scope="session")
def connection(connection_string):
  engine = create_engine(connection_string, echo=VERBOSE_CONNECTION,
                         future=True)
  with engine.connect() as conn:
    with conn.begin():
      drop_all(conn)
      provbatch.database.create(conn)
      yield conn
      if not DEBUG_MODE:
        drop_all(conn)
      conn.commit()
