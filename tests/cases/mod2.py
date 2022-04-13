#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
optstr="""
  --common2-input FN    input file common2
  --common2-output FN   output file common2
  --common2-param       common2 parameter
  -y                    defined in mod2 as input, in kwargs as param
"""

optmap={
  "input": ["--common2-input", "-y"],
  "output": ["--common2-output"],
  "params": ["--common2-param", "-x"]
}
