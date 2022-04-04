#!/usr/bin/env python3
"""
Echoes the input, for test purposes
"""

import sys

ID =      "echo"
VERSION = "1.0"
INPUT = "anything"
OUTPUT =  ["echo"]

class EchoState():
  def __init__(self):
    self.state = 0
    sys.stderr.write(f"initialized echo state: {self.state}\n")

  def __str__(self):
    self.inc()
    return f"echo state: {self.state}"

  def inc(self):
    self.state += 1

  def finalize(self):
    self.inc()
    sys.stderr.write(f"finalized echo state: {self.state}\n")

def initialize():
  return EchoState()

def finalize(state):
  state.finalize()

def compute(unit, state=None, **kwargs):
  if state:
    sys.stderr.write(str(state) + "\n")
  return [unit], None
