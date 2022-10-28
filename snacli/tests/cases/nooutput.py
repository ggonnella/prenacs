#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Usage:
  nooutput.py [options] <i1> I2 <p1> [P2]

Options:
  --i3 FN   the i3 input filename option
  -x FN     the X input filename option
  --p3      the P3 parameter
  -z        the Z parameter
"""
import snacli
with snacli.args(input=["<i1>","I2","--i3","-x"],
                 params=["<p1>","P2","--p3","-z"]) as args:
  print(args["<i1>"])
  print(args["I2"])
  print(args["--i3"])
  print(args["-x"])
  print(args["<p1>"])
  print(args["P2"])
  print(args["--p3"] is True)
  print(args["-z"] is True)
