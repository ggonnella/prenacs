#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Create attribute definition records and attribute columns in the
attribute_value tables according to the definitions in a given YAML file.
Optionally remove attribute columns and definition records which are not
present in the YAML file.

Usage:
  prenacs manage-attributes [options] \
      <dbuser> <dbpass> <dbname> <dbsocket> <definitions>

Arguments:
  dbuser:       database user to use
  dbpass:       password of the database user
  dbname:       database name
  dbsocket:     connection socket file
  definitions:  YAML file containing the attribute definitions

Options:
  --drop          drop columns and delete definition record for all attributes
                  not present in the YAML file (be careful, DANGEROUS!)
  --check         check consistency of definition records and attribute columns
  --update        update definitions if changed
  --testmode      use the parameters for tests
  --dbpfx PFX     database tablenames prefix to use (default: prenacs_)
  --quiet, -q     suppress output
  --debug, -d     debug mode
  --verbose, -v   be verbose
  --version, -V   show script version
  --help, -h      show this help message
"""
from schema import And, Or, Use
import yaml
from sqlalchemy import create_engine
import snacli
from attrtables import AttributeValueTables
from prenacs import AttributeDefinitionsManager,\
                    AttributeDefinition, __version__
from prenacs.database import DEFAULT_AVT_PREFIX
from prenacs.commands import helpers as scripts_helpers

def validated(args):
  args = scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA,
      {"<definitions>": And(str, Use(open), Use(yaml.safe_load)),
       "--update":      Or(None, True, False),
       "--testmode":    Or(None, True, False),
       "--drop":        Or(None, True, False),
       "--check":       Or(None, True, False),
       "--dbpfx":       Or(None, str)})
  args["--dbpfx"] = args["--dbpfx"] or DEFAULT_AVT_PREFIX
  return args

def main(args):
  args = validated(args)
  engine = create_engine(scripts_helpers.database.connection_string_from(args),
                         echo=args["--verbose"],
                         future=True)
  with engine.connect() as connection:
    with connection.begin():
      kwargs = {"target_n_columns": 9} if args["--testmode"] else {}
      avt = AttributeValueTables(connection,
                                 attrdef_class=AttributeDefinition,
                                 tablename_prefix=args["--dbpfx"], **kwargs)
      if args["--check"]:  avt.check_consistency()
      adm = AttributeDefinitionsManager(avt)
      if args["--update"]: adm.update_changed(args["<definitions>"])
      if args["--drop"]:   adm.drop_missing(args["<definitions>"])
      adm.insert_new(args["<definitions>"])

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 input=["<definitions>"],
                 params=["--drop", "--check", "--update", "--testmode",
                         "--verbose", "--dbpfx"],
                 version=__version__) as args:
  if args:
    main(args)
