#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Check that a computation plugin respects the specification
given in plugins/README.md.

The following is checked:
- the signature of the compute function and, optionally of
  the initialize, finalize (for Python plugins only)
- the existance, type and value of the plugin constants
- all the attributes declared in the OUTPUT constant must be
  contained in the given attribute definitions file

Usage:
  prenacs check-plugin <plugin> <definitions> [options]

Arguments:
  plugin:       Python or Nim batch_compute.py plugin module
  definitions:  YAML file containing the attribute definitions

Options:
  --quiet, -q              suppress output
  --debug, -d              debug mode
  --verbose, -v            be verbose
  --version, -V            show script version
  --help, -h               show this help message
"""

from schema import And, Use, Or
import yaml
import os
import snacli
from prenacs import PluginInterfaceAnalyser, __version__
from prenacs.commands import helpers as scripts_helpers

def validated(args):
  return scripts_helpers.validate(args, {"<plugin>": os.path.exists,
    "<definitions>": Or(None, And(str, Use(open), Use(yaml.safe_load)))})

def main(args):
  args = validated(args)
  analyser = PluginInterfaceAnalyser(args["<plugin>"],
                                     verbose=args["--verbose"])
  return analyser.run(args["<definitions>"])

with snacli.args(input=["<plugin>", "<definitions>"],
                 version=__version__) as args:
  if args:
    main(args)
