#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#
##
## Compute simple sequence statistics for a Fasta file
##

import strutils, os
import math
import nimpy
import zip/gzipfiles
import tables
import multiplug_nim/exportpy_consts

const
  ID =             "fas_stats_nim"
  VERSION =        "0.1.0"
  INPUT =          "genome sequence (Fasta, optionally gzipped)"
  OUTPUT =         @["genome_size", "GC_content"]
  METHOD =         "count bases"
  IMPLEMENTATION = "implemented in Nim, using a lookup table"
  PARAMETERS =     @[("force_uncompressed", "bool", "false",
                        "do not use the zip library to open the input file")]
  REQ_SOFTWARE =   "nim >= 1.2.8; nimble libraries: zip >= 0.3.1"
  ADVICE =         "preferred over fasgz_stats_posix, if nim is available, " &
                   "since it is faster"

exportpy_consts(ID, VERSION, INPUT, OUTPUT, METHOD, IMPLEMENTATION, PARAMETERS,
                REQ_SOFTWARE, ADVICE)

const bufsize = 2 ^ 16

type fas_state = enum indesc, newline, inseq

const isalphatab = block:
  var tmp: array[256, uint8]
  for i in 0 .. 255:
    tmp[i] = if isalphaascii(chr(i)): 1 else: 0
  tmp

const isgctab = block:
  var tmp: array[256, uint8]
  for i in 0 .. 255:
    tmp[i] = if chr(i) in ['G', 'C', 'g', 'c']: 1 else: 0
  tmp

template process_buffer2(buffer: array[bufsize, char], nread: int,
                    count_a: var uint,
                    count_b: var uint,
                    state: var fas_state,
                    tab_a: array[256, uint8],
                    tab_b: array[256, uint8]) =
  for i in 0 ..< nread:
    var char = buffer[i]
    if state == indesc:
      if char == '\n':
        inc(state)
    elif state == newline:
      if char == '>':
        dec(state)
      else:
        inc(state)
        count_a += tab_a[ord(char)]
        count_b += tab_b[ord(char)]
    else:
      if char == '\n':
        dec(state)
      else:
        count_a += tab_a[ord(char)]
        count_b += tab_b[ord(char)]

proc process_gzipped2(fasfile: string, tab_a: array[256, uint8],
                      tab_b: array[256, uint8]): tuple[a:uint, b:uint] =
  var
    f = newGzFileStream(fasfile)
    buffer: array[bufsize, char]
    state: fas_state = indesc
  while true:
    var nread = f.readData(addr buffer, bufsize)
    if nread == 0:
      break
    process_buffer2(buffer, nread, result.a, result.b, state, tab_a, tab_b)
  f.close()

proc process_file2(fasfile: string, tab_a: array[256, uint8],
                   tab_b: array[256, uint8]): tuple[a:uint, b:uint] =
  var
    f: File
  if open(f, fasfile):
    var
      state: fas_state = indesc
      buffer: array[bufsize, char]
    while true:
      var nread = f.read_buffer(addr buffer, bufsize)
      if nread == 0:
        break
      process_buffer2(buffer, nread, result.a, result.b, state, tab_a, tab_b)
    f.close()

proc compute(filename: string, force_uncompressed: bool = false):
             tuple[results: seq[string], logs: seq[string]] {.exportpy.} =
  let (gc, total) = block:
    if force_uncompressed:
      process_file2(filename, isgctab, isalphatab)
    else:
      process_gzipped2(filename, isgctab, isalphatab)
  result.results = @[$(total), $(gc.int/total.int)]
