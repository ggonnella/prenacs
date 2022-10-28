ID="sh_return_list_newline"
VERSION="0.1.0"
INPUT="nothing"
OUTPUT="blabla"

function compute {
  filename=$1
  shift
  kwargs=$*
  keys=()
  for kw in $kwargs; do eval $kw; keys+=(${kw%%=*}); done
  echo -e -n "$filename\n"
  for k in ${keys[@]}; do echo -e -n "$k\n${!k}\n"; done
  echo -e -n "\n"
}
