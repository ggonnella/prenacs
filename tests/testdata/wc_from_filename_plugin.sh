#!/usr/bin/env bash

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

ID="wc"
VERSION="1.0"
INPUT="filename"
OUTPUT=( "lines" "words" "bytes" )
IMPLEMENTATION="based on Posix tool wc"
REQ_SOFTWARE="wc"

function compute() { local filename=$1; shift; kwargs=$*
  for x in $kwargs; do eval $x; done
  if [ ! -e "$filename" ]; then
    logs="$filename does not exist"
    echo -en "\n$logs"
  else
    wc_out=( $(wc $filename) )
    echo -en "${wc_out[0]}\t${wc_out[1]}\t${wc_out[2]}\n"
  fi
}
