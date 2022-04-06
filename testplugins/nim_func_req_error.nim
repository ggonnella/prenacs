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

# no compute function
