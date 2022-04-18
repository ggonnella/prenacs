#
# (c) 2022, Giorgio Gonnella, University of Goettingen, Germany
#

"""
Helper methods for working with the database
"""

import os
from sqlalchemy.engine.url import URL
from schema import And, Or

ARGS_DOC = """\
  dbuser:       database user to use
  dbpass:       password of the database user
  dbname:       database name
  dbsocket:     connection socket file\
"""

OPTS_DOC = """\
  --dbpfx PFX      database tablenames prefix to use (default: prenacs_)\
"""

ARGS_USAGE="<dbuser> <dbpass> <dbname> <dbsocket>"

ARGS_SCHEMA = {"<dbuser>": And(str, len),
               "<dbpass>": And(str, len),
               "<dbname>": And(str, len),
               "<dbsocket>": And(str, len, os.path.exists),
               "--dbpfx": Or(None, And(str, len))}

SNAKE_ARGS = {"config": ["<dbuser>", "<dbpass>", "<dbname>"],
              "params": ["--dbpfx"],
              "input": ["<dbsocket>"]}

DB_DRIVER="mysql+mysqldb"
DB_HOST="localhost"

def connection_string_from(args) -> str:
  """
  MySQL/MariaDB connection string based on the values of the args
  '<dbuser>', '<dbpass>', '<dbname>' and '<dbsocket>'
  """
  if not(args["<dbsocket>"]):
    raise RuntimeError("DB unix socket not provided")
  elif not os.path.exists(args["<dbsocket>"]):
    raise RuntimeError(f"DB unix socket does not exist: {args['<dbsocket>']}")
  elif not(args["<dbuser>"]):
    raise RuntimeError("Database user name not provided")
  elif not(args["<dbpass>"]):
    raise RuntimeError("Database password for user '{}' not provided".\
                      format(args["<dbuser>"]))
  elif not(args["<dbname>"]):
    raise RuntimeError("Database name not provided")
  return URL.create(drivername=DB_DRIVER,
                    username=args["<dbuser>"],
                    password=args["<dbpass>"],
                    database=args["<dbname>"],
                    host=DB_HOST,
                    query={"unix_socket":args["<dbsocket>"]})
