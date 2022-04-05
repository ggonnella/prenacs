## Echoes the input, for test purposes

import nimpy
import os

const ID = "nim_w_state"
proc py_const_ID(): string {.exportpy} = ID
const VERSION = "1.0"
proc py_const_VERSION(): string {.exportpy.} = VERSION
const INPUT = "anything"
proc py_const_INPUT(): string {.exportpy.} = INPUT
const OUTPUT = @["bla"]
proc py_const_OUTPUT(): seq[string] {.exportpy.} = OUTPUT

type
  EchoState = ref object of RootObj
    count*: int

proc initialize(): EchoState {.exportpy.} =
  result = EchoState(count: 0)
  stderr.write("initialized state, count=" & $result.count & "\n")

proc finalize(s: EchoState) {.exportpy.} =
  s.count += 1
  stderr.write("finalized state, count=" & $s.count & "\n")

proc compute(filename: string, state: EchoState): string {.exportpy.} =
  if not isNil(state):
    state.count += 1
    stderr.write("count=" & $state.count & "\n")
  return filename
