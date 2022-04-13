#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Does nothing, for test purposes
"""

ID =      "fake4"
VERSION = "0.1.0"
INPUT = "test"
OUTPUT =  ["g2b"]

def compute(filename, **kwargs):
  return [10], ["test\tthis is a test by fake4"]

def fake_data():
  for acc in ["A1","A2","A3","A4"]:
    print("\t".join([acc]+[str(e) for e in compute(acc)[0]]))

if __name__ == "__main__":
  fake_data()
