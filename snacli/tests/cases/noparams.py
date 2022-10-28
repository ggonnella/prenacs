#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Usage:
  noparams.py [options] <i1> I2 <o1> O2

Options:
  --i3 FN   the i3 input filename option
  -x FN     the X input filename option
  --o3 FN   the o3 output filename option
  -y FN     the Y output filename option
"""
import snacli
with snacli.args(input=["<i1>","I2","--i3","-x"],
                 output=["<o1>","O2","--o3","-y"]) as args:
  print(args["<i1>"])
  print(args["I2"])
  print(args["--i3"])
  print(args["-x"])
  print(args["<o1>"])
  print(args["O2"])
  print(args["--o3"])
  print(args["-y"])
