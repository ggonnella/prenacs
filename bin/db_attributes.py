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
  db_attributes.py [options] {db_args_usage} <definitions>

Arguments:
{db_args}
  definitions:  YAML file containing the attribute definitions

Options:
  --drop           drop columns and delete definition record for all attributes
                   not present in the YAML file (be careful, DANGEROUS!)
  --check          check consistency of definition records and attribute columns
  --update         update definitions if changed
  --testmode       use the parameters for tests
{common}
"""
from schema import And, Or, Use
import yaml
from sqlalchemy import create_engine
import snacli
from attrtables import AttributeValueTables
from provbatch import scripts_helpers,\
                      AttributeDefinitionsManager,\
                      AttributeDefinition

def main(args):
  engine = create_engine(scripts_helpers.database.connection_string_from(args),
                         echo=args["--verbose"],
                         future=True)
  with engine.connect() as connection:
    with connection.begin():
      kwargs = {"target_n_columns": 9} if args["--testmode"] else {}
      avt = AttributeValueTables(connection,
                                 attrdef_class=AttributeDefinition,
                                 tablename_prefix="_".join(\
                                     args["--dbpfx"], "attribute_value_t"),
                                 **kwargs)
      if args["--check"]:  avt.check_consistency()
      adm = AttributeDefinitionsManager(avt, connection)
      if args["--update"]: adm.update_changed(args["<definitions>"])
      if args["--drop"]:   adm.drop_missing(args["<definitions>"])
      adm.insert_new(args["<definitions>"])

def validated(args):
  return scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA,
      {"<definitions>": And(str, Use(open), Use(yaml.safe_load)),
       "--update":      Or(None, True, False),
       "--testmode":    Or(None, True, False),
       "--drop":        Or(None, True, False),
       "--check":       Or(None, True, False)})

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 input=["<definitions>"],
                 params=["--drop", "--check", "--update", "--testmode",
                         "--verbose"],
                 docvars={"common": scripts_helpers.common.ARGS_DOC,
                          "db_args": scripts_helpers.database.ARGS_DOC,
                          "db_args_usage": scripts_helpers.database.ARGS_USAGE},
                 version="1.0") as args:
  if args: main(validated(args))