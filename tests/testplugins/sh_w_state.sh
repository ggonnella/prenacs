ID="sh_w_state"
VERSION="0.1.0"
INPUT="nothing"
OUTPUT="blabla"

function initialize {
  local state_file=$(mktemp)
  echo local count=0 > $state_file
  echo "initialized state, count=0" >&2
  echo -n "$state_file"
}

function inc_count {
  local state_file=$1
  eval $(cat $state_file)
  echo local count=$((count+1)) > $state_file
}

function finalize {
  local state_file=$1
  eval $(cat $state_file)
  count=$((count+1))
  echo "finalized state, count="$count >&2
  rm -f $state_file
}

function compute {
  local filename=$1; shift
  for kw in $*; do eval $kw; done
  if [ ! -z ${state+x} ]; then
    inc_count $state
    eval $(cat $state)
    echo "count=$count" >&2
  fi
  echo -e -n "$filename"
}
