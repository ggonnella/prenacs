"""
Compute sequence statistics using Posix command line tools
"""
import sh

ID =      "fas_stats_posix"
VERSION = "0.1.0"
INPUT =   "genome sequence; Fasta; optionally Gzip-compressed"
OUTPUT =  ["genome_size","GC_content"]
METHOD =  "count bases"
IMPLEMENTATION = "pipe of posix tools, called from python using sh library"
REQ_SOFTWARE   = "grep, tr, wc, zcat"
PARAMETERS     = [("uncompressed", "bool", "False", "input is not gzipped")]

def compute(filename, **kwargs):
  results = {}
  countchars = sh.wc.bake(c=True)
  gc_only = sh.tr.bake("-dc", "[GCgc]", _piped=True)
  non_space = sh.tr.bake(d="[:space:]", _piped=True)
  vgrep = sh.grep.bake(_piped=True, v=True)
  uncompressed = sh.zcat.bake(_piped=True)
  if kwargs.get("uncompressed", False):
    genomelen = int(countchars(non_space(vgrep("^>", filename))))
    gclen = int(countchars(gc_only(vgrep("^>", filename))))
  else:
    genomelen = int(countchars(non_space(vgrep(uncompressed(filename), "^>"))))
    gclen = int(countchars(gc_only(vgrep(uncompressed(filename), "^>"))))
  return [genomelen, gclen/genomelen], []
