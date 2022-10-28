#!/usr/bin/env python3
#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Echoes the input, for test purposes
"""

import sys

ID = "py_w_state"
VERSION = "1.0"
INPUT = "anything"
OUTPUT = ["bla"]

class EchoState():
  def __init__(self):
    self.count = 0
    sys.stderr.write(f"initialized state, count={self.count}\n")

  def finalize(self):
    self.count += 1
    sys.stderr.write(f"finalized state, count={self.count}\n")

def initialize():
  return EchoState()

def finalize(state):
  state.finalize()

def compute(filename, state=None, **kwargs):
  if state:
    state.count += 1
    sys.stderr.write(f"count={state.count}\n")
  return filename
