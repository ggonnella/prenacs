#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

ID="wc"
VERSION="1.0"
INPUT="filename"
OUTPUT=["lines", "words", "bytes"]
IMPLEMENTATION="based on Posix tool wc"
REQ_SOFTWARE="wc, pip library sh"

from sh import wc

def compute(filename, **kwargs):
  wc_out=wc(filename).split()
  return "\t".join(wc_out[0:3]), ""
