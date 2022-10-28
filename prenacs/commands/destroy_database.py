#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Destroy the entire database

Usage:
  prenacs destroy-database [options] \
      <dbuser> <dbpass> <dbname> <dbsocket>

Arguments:
  dbuser:       database user to use
  dbpass:       password of the database user
  dbname:       database name
  dbsocket:     connection socket file

Options:
  --dbpfx PFX              database tablenames prefix to use (default: prenacs_)
  --quiet, -q              suppress output
  --debug, -d              debug mode
  --verbose, -v            be verbose
  --version, -V            show script version
  --help, -h               show this help message
"""
from schema import Or
from sqlalchemy import create_engine
import snacli
from attrtables import AttributeValueTables
import prenacs.database
from prenacs import AttributeDefinition, __version__
from prenacs.commands import helpers as scripts_helpers

def main(args):
  engine = create_engine(scripts_helpers.database.connection_string_from(args),
                         echo=args["--verbose"],
                         future=True)
  with engine.connect() as connection:
    with connection.begin():
      avt = AttributeValueTables(connection,
                                 attrdef_class=AttributeDefinition,
                                 tablename_prefix=args["--dbpfx"])
      prenacs.database.drop(connection, avt)

def validated(args):
  args = scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA,
                                  {"--dbpfx": Or(None, str)})
  args["--dbpfx"] = args["--dbpfx"] or "prenacs_attribute_value_t"
  return args

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 params=["--verbose"],
                 version=__version__) as args:
  if args: main(validated(args))
