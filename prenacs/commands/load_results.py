#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Load computation results into DB from a TSV file and a computation report.

Usage:
  prenacs load-results [options] \
      <dbuser> <dbpass> <dbname> <dbsocket> \
                             <results> <report> <plugin>

Arguments:
  dbuser:       database user to use
  dbpass:       password of the database user
  dbname:       database name
  dbsocket:     connection socket file
  results:      results file, tsv with columns:
                accession, attr_class, attr_instance, value[, score]
  report:       computation report file (yaml format)
  plugin:       plugin used for the computation

Options:
  --replace-plugin-record  replace existing db record for current version of the
                           plugin, if changed (default: fail if changed)
  --replace-report-record  replace existing db record for the computation
                           report, if changed (default: fail if changed)
  --dbpfx PFX              database tablenames prefix to use (default: prenacs_)
  --verbose, -v            be verbose
  --version, -V            show script version
  --help, -h               show this help message
"""
from schema import And, Or
import sys
import os
from sqlalchemy import create_engine
import snacli
from attrtables import AttributeValueTables
from prenacs import ResultsLoader, AttributeDefinition, \
                    __version__
from prenacs.database import DEFAULT_AVT_PREFIX
from prenacs.commands import helpers as scripts_helpers

def main(args):
  if os.stat(args["<results>"]).st_size == 0:
    if args["--verbose"]:
      sys.stderr.write("# nothing to load, as results file is empty \n")
    return
  engine = create_engine(scripts_helpers.database.connection_string_from(args),
                         echo=args["--verbose"],
                         future=True)
  with engine.connect() as connection:
    with connection.begin():
      avt = AttributeValueTables(connection,
                               attrdef_class=AttributeDefinition,
                               tablename_prefix=args["--dbpfx"])
      results_loader = ResultsLoader(avt, args["<plugin>"],
                                     args["--replace-plugin-record"],
                                     args["--verbose"])
      results_loader.run(args["<results>"], args["<report>"],
                         args["--replace-report-record"], args["--verbose"])

def validated(args):
  args = scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA,
                  {"<results>": And(str, open),
                   "<report>": And(str, open),
                   "<plugin>": And(str, open),
                   "--replace-plugin-record": Or(None, True, False),
                   "--replace-report-record": Or(None, True, False),
                   "--dbpfx":      Or(None, str)})
  args["--dbpfx"] = args["--dbpfx"] or DEFAULT_AVT_PREFIX
  return args

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 input=["<results>", "<report>", "<plugin>"],
                 params=["--replace-plugin-record", "--replace-report-record",
                         "--verbose"],
                 version=__version__) as args:
  if args: main(validated(args))
