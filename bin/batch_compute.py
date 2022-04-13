#!/usr/bin/env python3
"""
Perform computations on multiple files, using the compute function of the
specified Python/Nim/Rust plugin module (see plugins/README.md for the plugins
specification).

Usage:
  batch_compute.py <plugin> ids <idsfile> [<col>] [options]
  batch_compute.py <plugin> files <globpattern> [options]

The compute function is applied to each input ID or filename (see below).
Unless --skip is used and the input ID (or ID computed from the filename)
is present in the skip file.

Input:

  ids <idsfile> [<col>]

    (1a) IDs in a file, one per line => use "ids <idsfile>"
    (1b) IDs in a TSV file => use "ids <idsfile> <col>"; 1-based col number

  => to edit the ids (passed to compute() and used by --skip and
     in the results) use --idsproc

  files <globpattern>

    (2) Names of files matching a glob pattern => "files <globpattern>"

  => to compute the IDs (used by --skip and in the results), use --idsproc,
     otherwise the filenames are used as IDs;
     (note: the input to compute() are in this case the filenames,
      thus not affected by --idsproc)

Output:
- computation results: TSV file, where the first column contains the IDs,
  the following columns are the results in the order specified by the plugin
- logs: TSV file, first column are the unit IDs, followed by information
  messages returned by the plugin (each computation can generate zero, one
  or multiple lines)
- computation report: YAML file, computation time, status, plugin name,
  version, parameters, username, hostname, etc.

Options:
  --idsproc FNAME   Python/Nim/Rust module, providing compute_id(str)->str;
                    allows to edit the IDs/filenames used for (1) results;
                    (2) --skip option; (3) in "ids" mode only: input to the
                    compute() function
  --skip, -s FNAME  skip computations for which the ID is contained in this
                    file (one ID per line, or TSV with IDs in first column)
  --out, -o FNAME   output results to file (default: stdout);
                    if the file exists, the output is appended
                    and the file is used also for skipping previously computed
                    results (unless a different file is specified with --skip)
  --log, -l FNAME   write logs to the given file (default: stderr);
                    if the file exists, the output is appended
  --serial          run the computation serially (default: use multiprocessing)
{report_opts}
{common}
"""

from schema import Or
import os
import sys
from provbatch import BatchComputation, scripts_helper
import snacli

def main(args):
  batch_computation = BatchComputation(args["<plugin>"], args["--verbose"])
  if args["<globpattern>"]:
    batch_computation.input_from_globpattern(args["<globpattern>"],
        args["--idsproc"], args["--skip"], args["--verbose"])
  else:
    batch_computation.input_from_idsfile(args["<idsfile>"], args["<col>"],
        args["--idsproc"], args["--skip"], args["--verbose"])
  batch_computation.set_output(args["--out"], args["--log"])
  batch_computation.setup_computation(args["--params"], args["--report"],
      args["--user"], args["--system"], args["--reason"], args["--verbose"])
  try:
    batch_computation.run(not args["--serial"], args["--verbose"])
  except Exception as e:
    print("# The computation failed", file=sys.stderr)
    print(f"# Error message:\n  {e}", file=sys.stderr)
    sys.exit(1)
  batch_computation.finalize()

def validated(args):
  args = scripts_helper.validate(args, scripts_helper.REPORT_ARGS_SCHEMA,
      {"<globpattern>": Or(None, str),
       "<idsfile>": Or(None, os.path.exists),
       "--idsproc": Or(None, os.path.exists),
       "<col>": scripts_helper.OPTCOLNUM_VALIDATOR,
       "<plugin>": os.path.exists,
       "--out": Or(None, str),
       "--log": Or(None, str),
       "--skip": Or(None, os.path.exists)})
  if args["--skip"] is None and args["--out"]:
     args["--skip"] = args["--out"]
  return args

with snacli.args(scripts_helper.REPORT_SNAKE_ARGS,
                 input=["<plugin>", "--idsproc"],
                 log=["--out", "--log"],
                 params=["<globpattern>", "<idsfile>", "<col>", "--verbose",
                         "--skip", "--serial"],
                 docvars={"common": scripts_helper.COMMON_ARGS_DOC,
                          "report_opts": scripts_helper.REPORT_ARGS_DOC},
                 version="1.0") as args:
  if args: main(validated(args))
