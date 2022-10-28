#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Usage:
  noinput.py [options] <o1> O2 <p1> [P2]

Options:
  --o3 FN   the o3 output filename option
  -y FN     the Y output filename option
  --p3      the P3 parameter
  -z        the Z parameter
"""
import snacli
with snacli.args(output=["<o1>","O2","--o3","-y"],
                 params=["<p1>","P2","--p3","-z"]) as args:
  print(args["<o1>"])
  print(args["O2"])
  print(args["--o3"])
  print(args["-y"])
  print(args["<p1>"])
  print(args["P2"])
  print(args["--p3"] is True)
  print(args["-z"] is True)
