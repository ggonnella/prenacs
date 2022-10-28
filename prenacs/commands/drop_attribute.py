#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Drop an attribute definition record and attribute columns in the
attribute_value tables.

Usage:
  prenacs destroy-database [options] \
      <dbuser> <dbpass> <dbname> <dbsocket> <name>

Arguments:
  dbuser:       database user to use
  dbpass:       password of the database user
  dbname:       database name
  dbsocket:     connection socket file
  name:         name of the attribute

Options:
  --dbpfx PFX              database tablenames prefix to use (default: prenacs_)
  --verbose, -v            be verbose
  --version, -V            show script version
  --help, -h               show this help message
"""
from schema import And, Or
from sqlalchemy import create_engine
import snacli
from attrtables import AttributeValueTables
from prenacs import AttributeDefinitionsManager,\
                    AttributeDefinition, __version__
from prenacs.database import DEFAULT_AVT_PREFIX
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
      adm = AttributeDefinitionsManager(avt)
      adm.drop(args["<name>"])

def validated(args):
  args = scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA,
      {"<name>": And(str, len),
       "--testmode":   Or(None, True, False),
       "--dbpfx":      Or(None, str)})
  args["--dbpfx"] = args["--dbpfx"] or DEFAULT_AVT_PREFIX
  return args

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 input=["<name>"],
                 params=["--verbose"],
                 version=__version__) as args:
  if args: main(validated(args))
