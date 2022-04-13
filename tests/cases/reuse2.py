#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Usage:
  reuse2.py [options] <input_sp2> <output_sp2>

Options:
  --param_sp2     specific parameter
  {common1}
  {common2}
"""
import snacli
import mod1
import mod2
with snacli.args(mod1.optmap, mod2.optmap,
                 docvars={"common1": mod1.optstr, "common2": mod2.optstr},
                 input=["<input_sp2>"], output=["<output_sp2>"],
                 params=["--param_sp2", "-y"]) as args:
  print(args["<input_sp2>"])
  print(args["--common1-input"])
  print(args["--common2-input"])
  print(args["<output_sp2>"])
  print(args["--common1-output"])
  print(args["--common2-output"])
  print(args["--common1-param"])
  print(args["--common2-param"])
  print(args["-x"]) # defined in mod1 as input, in mod2 as param
  print(args["-y"]) # defined in mod2 as input, in kwargs as param
  print(args["--param_sp2"])
