#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
optstr="""
  --common1-input FN    input file common1
  --common1-output FN   output file common1
  --common1-param       common1 parameter
  -x                    defined in mod1 as input, in mod2 as param
"""

optmap={
  "input": ["--common1-input", "-x"],
  "output": ["--common1-output"],
  "params": ["--common1-param"]
}
