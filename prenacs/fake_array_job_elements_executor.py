#!/usr/bin/env python3

"""
Computes something on the array

At the moment it just displays the content of the files

Usage:
  fake_array_job_elements_executor.py <plugin_file> <parameters_file> <input_list_file>

"""

import docopt

args = docopt.docopt(__doc__, version="0.1")
for key in ["plugin_file", "parameters_file",
            "input_list_file"]:
  print("="*50)
  filename = args["<"+key+">"]
  print(key + ": " + filename)
  print()
  print("-"*50)
  print()
  with open(filename) as file:
    print(file.read())
