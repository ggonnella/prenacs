#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Echoes the input, for test purposes
"""

import sys

ID =      "echo"
VERSION = "1.0"
INPUT = "anything"
OUTPUT = ["bla", "bla"]
ADVICE = "advice"
UNDECLARED_CONST = "imported"

def initialize():
  return "init"

def compute(unit, state=None, **kwargs):
  return [unit], None

def undeclared_func():
  return "imported"
