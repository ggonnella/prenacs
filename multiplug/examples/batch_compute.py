#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Perform computations on multiple files, using the compute function of the
specified Python/Nim/Rust/Shell plugin module.

Usage:
  batch_compute.py <plugin> <globpattern> [options]

The plugin module shall define a compute(filename, **kwargs) function,
which is applied to each input filename. The function shall return
an array of values.

The output is a TSV file, where in the first column is the filename
and in the following columns are the values returned by applying compute().

Options:
  --params FNAME  YAML file with additional parameters (default: None)
  --verbose, -v  be verbose
  --version, -V  show script version
  --help, -h     show this help message
"""

from docopt import docopt
from schema import Or, And, Use, Schema
import os
import sys
from pathlib import Path
from glob import glob
import yaml
import multiplug

PLUGIN_API_CONFIG = {}
PLUGIN_API_CONFIG["req_func"] = ["compute"]
PLUGIN_API_CONFIG["opt_func"] = ["initialize", "finalize"]
PLUGIN_API_CONFIG["req_const"] = ["ID", "VERSION", "INPUT", "OUTPUT"]
PLUGIN_API_CONFIG["opt_const"] = ["METHOD", "IMPLEMENTATION", "PARAMETERS",
                                  "ADVICE","REQ_SOFTWARE", "REQ_HARDWARE"]

def main(args):
  plugin = multiplug.importer(args["<plugin>"], verbose=args["--verbose"],
                              **PLUGIN_API_CONFIG)
  params = args["--params"]
  if plugin.initialize is not None:
    params["state"] = plugin.initialize()
  all_ids = glob(args["<globpattern>"])
  for unit_id in all_ids:
    results = [unit_id, str(plugin.compute(unit_id, **params))]
    print("\t".join(results))
  if plugin.finalize is not None:
    plugin.finalize(params["state"])

def validated(args):
  s = {"<globpattern>": str, "<plugin>": os.path.exists,
      "--help": bool, "--verbose": bool, "--version": bool,
       "--params": Or(And(None, Use(lambda n: {})),
              And(Use(open), Use(lambda fn: yaml.safe_load(fn))))}
  return Schema(s).validate(args)

if __name__ == "__main__":
  args = docopt(__doc__, version="1.0")
  main(validated(args))
