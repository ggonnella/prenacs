#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Usage:
  custom_map.py [options] <i1> I2 <o1> O2 <p1> [P2]

Options:
  --i3 FN   the i3 input filename option
  -x FN     the X input filename option
  --o3 FN   the o3 output filename option
  -y FN     the Y output filename option
  --p3      the P3 parameter
  -z        the Z parameter
"""
import snacli
with snacli.args(input=[("<i1>", "input1"),"I2",("--i3", "input3"),"-x"],
                 output=["<o1>",("O2", "output2"),"--o3","-y"],
                 params=["<p1>","P2","--p3",("-z", "zeta")]) as args:
  print(args["<i1>"])
  print(args["I2"])
  print(args["--i3"])
  print(args["-x"])
  print(args["<o1>"])
  print(args["O2"])
  print(args["--o3"])
  print(args["-y"])
  print(args["<p1>"])
  print(args["P2"])
  print(args["--p3"] is True)
  print(args["-z"] is True)
