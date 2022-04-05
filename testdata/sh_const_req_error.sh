ID="sh_requirement_err_fn"
VERSION="0.1.0"
INPUT="nothing"
# OUTPUT is missing

function compute {
  filename=$1
  shift
  kwargs=$*
  keys=()
  for kw in $kwargs; do eval $kw; keys+=(${kw%%=*}); done
  echo -e -n "$filename\n"
  for k in ${keys[@]}; do echo -e -n "$k\t${!k}\n"; done
}
