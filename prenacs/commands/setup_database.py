#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Create the tables for storing attribute, plugin and computation metadata.

Usage:
  prenacs setup-database [options] \
      <dbuser> <dbpass> <dbname> <dbsocket>

Arguments:
  dbuser:       database user to use
  dbpass:       password of the database user
  dbname:       database name
  dbsocket:     connection socket file

Options:
  --dbpfx PFX     database tablenames prefix to use (default: prenacs_)
  --quiet, -q     suppress output
  --debug, -d     debug mode
  --verbose, -v   be verbose
  --version, -V   show script version
  --help, -h      show this help message
"""
from sqlalchemy import create_engine
import snacli
import prenacs.database
from prenacs import __version__
from prenacs.commands import helpers as scripts_helpers

def validated(args):
  return scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA)

def main(args):
  args = validated(args)
  engine = create_engine(scripts_helpers.database.connection_string_from(args),
                         echo=args["--verbose"],
                         future=True)
  with engine.connect() as connection:
    with connection.begin():
      prenacs.database.create(connection)

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 params=["--verbose"],
                 version=__version__) as args:
  if args:
    main(args)
