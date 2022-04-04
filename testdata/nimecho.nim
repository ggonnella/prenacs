## Echoes the input, for test purposes

import nimpy
import os
import plugin_helpers

const
  ID =      "nimecho"
  VERSION = "1.0"
  INPUT =   "anything"
  OUTPUT =  @["echo"]

export_plugin_metadata()

type
  EchoState = ref object of RootObj
    state*: int

proc initialize(s: int = 0): EchoState {.exportpy.} =
  result = EchoState(state: s)
  echo("initializing nimecho state: " & $result.state & "...")

proc incr(s: EchoState) =
  s.state += 1

proc `$`(s: EchoState): string =
  s.incr()
  "nimecho state: " & $s.state

proc finalize(s: EchoState) {.exportpy.} =
  #s.incr()
  echo("finalizing nimecho state: " & $s.state & "...")

proc compute(filename: string, state: EchoState):
      tuple[results: seq[string], logs: seq[string]] {.exportpy.} =
  if not isNil(state):
    echo($state)
  result.results = @[filename]

proc compute_id(filename: string): string {.exportpy.} =
  splitFile(filename).name
