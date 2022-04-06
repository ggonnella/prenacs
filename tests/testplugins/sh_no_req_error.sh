ID="sh_requirement_err_fn"
VERSION="0.1.0"
INPUT="nothing"
OUTPUT=( "bla" "bla" )
ADVICE="advice"
UNDECLARED_CONST="imported"

function initialize {
  echo -n "init"
}

function compute {
  filename=$1
  shift
  kwargs=$*
  keys=()
  for kw in $kwargs; do eval $kw; keys+=(${kw%%=*}); done
  echo -e -n "$filename\n"
  for k in ${keys[@]}; do echo -e -n "$k\t${!k}\n"; done
}

function undeclared_func {
  echo -n "imported"
}
