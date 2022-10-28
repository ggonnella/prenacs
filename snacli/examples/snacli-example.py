#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Example script for showing the functionality of SnaCLI.

Usage:
  snacli-example.py [options] <ntimes> <input1> <output1> [<foo> BAR]

Arguments:
  ntimes    number of times to repeat the operation
  input1    required, input file 1
  output1   required, output file 1
  foo       optional, the foo input
  bar       optional (required if foo), the bar output

Options:
  -h --help            show this help message and exit
  -v, --verbose        a short- and long-form flag option
  -x X                 a short-form only option with value
  --input2=<string>    input file 2 (long-form only option)
  --output2=<string>   output file 2
"""

from docopt import docopt
import snacli
from pathlib import Path

def touch_output(path):
  if path is not None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).touch()

def main(args):
  # Print the arguments
  print('ntimes: {}'.format(args['<ntimes>']))
  print('input1: {}'.format(args['<input1>']))
  print('output1: {}'.format(args['<output1>']))
  print('foo: {}'.format(args['<foo>']))
  print('bar: {}'.format(args['BAR']))
  print('verbose: {}'.format(args['--verbose']))
  print('x: {}'.format(args['-x']))
  print('input2: {}'.format(args['--input2']))
  print('output2: {}'.format(args['--output2']))
  print(args)
  # touch output files
  touch_output(args['<output1>'])
  touch_output(args['--output2'])
  touch_output(args['BAR'])

with snacli.args(version="1.0",
                 input=["<input1>", "<foo>", "--input2"],
                 output=["<output1>", "BAR", "--output2"],
                 params=["<ntimes>", "-x", "--verbose"]) as args:
  if args: main(args)

