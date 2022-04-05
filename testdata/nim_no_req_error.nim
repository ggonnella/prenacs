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
proc py_const_OUTPUT(): seq[string] {.exportpy.} = OUTPUT

const ADVICE = "advice"
proc py_const_ADVICE(): string {.exportpy.} = ADVICE

const UNDECLARED_CONST = "imported"
proc py_const_UNDECLARED_CONST(): string {.exportpy.} = UNDECLARED_CONST

proc initialize(): string {.exportpy.} = "init"

proc compute(filename: string):
      tuple[results: seq[string], logs: seq[string]] {.exportpy.} =
  result.results = @[filename]

proc undeclared_func(): string {.exportpy.} = "imported"
