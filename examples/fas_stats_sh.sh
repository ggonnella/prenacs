#!/bin/bash
# Compute sequence statistics using Posix command line tools

ID="fas_stats_bash"
VERSION="0.1.0"
INPUT="genome sequence; Fasta; optionally Gzip-compressed"
OUTPUT=( "genome_size" "GC_content" )
METHOD="count bases"
IMPLEMENTATION="pipe of posix tools, called from python using sh library"
REQ_SOFTWARE="grep, tr, wc, zcat"
PARAMETERS=( "uncompressed\tbool\tFalse\tinput is not gzipped"
             "param2\tbool\tTrue\tbla bla")

function compute() { local filename=$1; shift; kwargs=$*
  for x in $kwargs; do eval $x; done
  if file $filename | grep 'gzip compressed' -q; then CAT=zcat; else CAT=cat; fi
  genomelen=$($CAT $filename | env -u GREP_OPTIONS grep -v '^>' | \
              tr -d '[:space:]' | wc -c)
  gclen=$($CAT $filename | env -u GREP_OPTIONS grep -v '^>' | \
          tr -dc '[GCgc]' | wc -c)
  gc_content=$(echo $gclen/$genomelen | bc -l)
  echo -en ${genomelen}"\t"${gc_content}
}
