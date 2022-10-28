#!/usr/bin/env python3

"""
Runs a plugin passing the parameters obtained from a dump file,
passing the <task_id>-th line of the <input_list_file> file
as input entity ID/filename

Usage:
  prenacs array-task [options] <plugin> <dumped_params> \
                               <dumped_input_list> <task_id> \
                               <output_dir>

Options:
  --quiet, -q              suppress output
  --debug, -d              debug mode
  --verbose, -v            be verbose
  --version, -V            show script version
  --help, -h               show this help message
"""

import docopt
import multiplug
import dill
from pathlib import Path
from prenacs import plugins_helper, __version__

def validated(args):
  return args

def main(args):
  args = validated(args)
  plugin = multiplug.importer(args["<plugin>"],
               **plugins_helper.COMPUTE_PLUGIN_INTERFACE)

  params_file = open(args["<dumped_params>"], "rb")
  params = dill.load(params_file)
  params_file.close()

  input_list_file = open(args["<dumped_input_list>"], "rb")
  input_list = dill.load(input_list_file)
  unit_id = input_list[int(args["<task_id>"])]
  input_list_file.close()

  results, *logs = plugin.compute(unit_id, **params)

  Path(args["<output_dir>"]).mkdir(parents=True, exist_ok=True)
  outfile = open(Path(args["<output_dir>"])/args["<task_id>"], "wb")
  dill.dump((results, logs), outfile)
  outfile.close()

if __name__ == "__main__":
  args = docopt.docopt(__doc__, version=__version__)
  main(args)
