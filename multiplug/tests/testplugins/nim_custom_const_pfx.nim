## Echoes the input, for test purposes

import nimpy
import os

const ID = "nimechonofi"
proc python_constant_ID(): string {.exportpy} = ID

const VERSION = "1.0"
proc python_constant_VERSION(): string {.exportpy.} = VERSION

const INPUT = "anything"
proc python_constant_INPUT(): string {.exportpy.} = INPUT

const OUTPUT = @["echo"]
proc python_constant_OUTPUT(): seq[string] {.exportpy.} = OUTPUT

proc compute(filename: string):
      tuple[results: seq[string], logs: seq[string]] {.exportpy.} =
  result.results = @[filename]
