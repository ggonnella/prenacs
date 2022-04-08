#!/usr/bin/env bash

SCRIPT_DIR=$(readlink -f $(dirname $0))
INPUT_DIR=$SCRIPT_DIR/../tests/testdata
OUTPUT_DIR=$SCRIPT_DIR/example_out

INPUT1=$INPUT_DIR/input1
FOO=$INPUT_DIR/input2
OUTPUT1=$OUTPUT_DIR/o1
BAR=$OUTPUT_DIR/o2

echo "Running example script from the command line"
echo
$SCRIPT_DIR/snacli-example.py 1 $INPUT1 $FOO $OUTPUT1 $BAR \
                              --verbose -x 3
echo
echo "Running example script using snakemake"
echo
snakemake -j 1 -s <(cat << EOF
rule all:
  input: input1="$INPUT1", foo="$FOO"
  output: output1="$OUTPUT1", bar="$BAR"
  params: verbose=True, x=3
  script: "$SCRIPT_DIR/snacli-example.py"

# touch the input files, so that the rule is executed again next time
onsuccess: shell("touch $INPUT1 $FOO")
EOF
)
