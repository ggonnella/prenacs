#!/usr/bin/env python3
"""
Load computation results into DB from a TSV file and a computation report.

Usage:
  db_load_results.py [options] {db_args_usage}
                               <results> <report> <plugin>

Arguments:
{db_args}
  results:   results file, tsv with columns:
             accession, attr_class, attr_instance, value[, score]
  report:    computation report file (yaml format)
  plugin:    plugin used for the computation

Options:
  --replace-plugin-record  replace existing db record for current version of the
                           plugin, if changed (default: fail if changed)
  --replace-report-record  replace existing db record for the computation
                           report, if changed (default: fail if changed)
{common}
"""
from schema import And, Or, Use
import sys
import os
from sqlalchemy import create_engine
import snacli
from provbatch import scripts_helpers, ResultsLoader

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
      results_loader = ResultsLoader(connection, args["<plugin>"],
                                     args["--replace-plugin-record"],
                                     "_".join(args["--dbpfx"],
                                              "attribute_value_t"),
                                     args["--verbose"])
      results_loader.run(args["<results>"], args["<report>"].
                         args["--replace-report-record"], args["--verbose"])

def validated(args):
  return scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA,
                  {"<results>": And(str, open),
                   "<report>": And(str, Use(open)),
                   "<plugin>": And(str, open),
                   "--replace-plugin-record": Or(None, True, False),
                   "--replace-report-record": Or(None, True, False)})

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 input=["<results>", "<report>", "<plugin>"],
                 params=["--replace-plugin-record", "--replace-report-record",
                         "--verbose"],
                 docvars={"common": scripts_helpers.common.ARGS_DOC,
                          "db_args": scripts_helpers.database.ARGS_DOC,
                          "db_args_usage": scripts_helpers.database.ARGS_USAGE},
                 version="1.0") as args:
  if args: main(validated(args))
