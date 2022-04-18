#!/usr/bin/env bash

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

ID="wc"
VERSION="1.0"
INPUT="filename"
OUTPUT=( "lines" "words" "bytes" )
IMPLEMENTATION="based on Posix tool wc"
METHOD="takes a number N as input, and uses input<N>.data as input file"
REQ_SOFTWARE="wc"
PARAMETERS=( "testdatadir\tstr\t.\tdirectory containing the input files" )

function compute() { local entity_id=$1; shift; kwargs=$*
  for x in $kwargs; do eval $x; done
  if [ -z $testdatadir ]; then
    echo "testdatadir not set" > /dev/stderr;
    return 1;
  fi
  filename="$testdatadir/input${entity_id}.data"
  if [ ! -e "$filename" ]; then
    logs="$filename does not exist"
    echo -en "\n$logs"
  else
    wc_out=( $(wc $filename) )
    echo -en "${wc_out[0]}\t${wc_out[1]}\t${wc_out[2]}\n"
  fi
}
