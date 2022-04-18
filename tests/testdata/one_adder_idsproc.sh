#!/usr/bin/env bash

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

#
# Just increase the input ID by one
#

function compute_id { local input_id=$1;
  output_id=$[$input_id + 1];
  echo -n "$output_id";
}
