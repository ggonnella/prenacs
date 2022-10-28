## Echoes the input, for test purposes

import nimpy
import os

const ID = "nimechonofi"
proc py_const_ID(): string {.exportpy} = ID

const VERSION = "1.0"
proc py_const_VERSION(): string {.exportpy.} = VERSION

const INPUT = "anything"
proc py_const_INPUT(): string {.exportpy.} = INPUT

const OUTPUT = @["echo"]
# OUTPUT not exported

proc compute(filename: string):
      tuple[results: seq[string], logs: seq[string]] {.exportpy.} =
  result.results = @[filename]
