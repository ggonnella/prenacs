#!/usr/bin/env python3
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
  check_plugin.py <plugin> <definitions> [options]

Arguments:
  plugin:       Python or Nim batch_compute.py plugin module
  definitions:  YAML file containing the attribute definitions

Options:
{common}
"""

from schema import And, Use, Or
import yaml
import os
from lib import scripts
import snacli
from provbatch import PluginInterfaceAnalyser

def main(args):
  analyser = PluginInterfaceAnalyser(args["<plugin>"],
                                     verbose=args["--verbose"])
  return analyser.run(args["<definitions>"])

def validated(args):
  return scripts.validate(args, {"<plugin>": os.path.exists,
    "<definitions>": Or(None, And(str, Use(open), Use(yaml.safe_load)))})

with snacli.args(input=["<plugin>", "<definitions>"],
                 docvars={"common": scripts.args_doc},
                 version="0.1") as args:
  if args: main(validated(args))
