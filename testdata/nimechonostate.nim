## Echoes the input, for test purposes
## no state (initializer/state param in compute/finalizer)

import nimpy
import os
import plugin_helpers

const
  ID =      "nimechonofi"
  VERSION = "1.0"
  INPUT =   "anything"
  OUTPUT =  @["echo"]

export_plugin_metadata()

proc compute(filename: string):
      tuple[results: seq[string], logs: seq[string]] {.exportpy.} =
  result.results = @[filename]
