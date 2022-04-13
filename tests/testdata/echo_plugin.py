#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Echoes the input, for test purposes
"""

from pathlib import Path

ID =      "echo"
VERSION = "1.0"
INPUT = "anything"
OUTPUT =  ["echo"]

class EchoState():
  def __init__(self):
    self.state = 0
    print(f"initializing echo state: {self.state}...")

  def __str__(self):
    self.inc()
    return f"echo state: {self.state}"

  def inc(self):
    self.state += 1

  def finalize(self):
    self.inc()
    print(f"finalizing echo state: {self.state}...")

def initialize():
  return EchoState()

def finalize(state):
  state.finalize()

def compute(unit, state=None, **kwargs):
  if state:
    print(str(state))
  return [unit], None

def compute_id(filename):
  return Path(filename).stem
