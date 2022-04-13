from schema import Or, And, Use, Optional, Schema
import sys
import yaml
from provbatch.report import Report

YAMLFILE_VALIDATOR = Or(And(None, Use(lambda n: {})),
              And(Use(open), Use(lambda fn: yaml.safe_load(fn))))

OUTFILE_OR_STDERR_VALIDATOR = Or(And(None, Use(lambda f: sys.stderr)),
                              Use(lambda f: open(f, "w")))

COLNUM_VALIDATOR = And(Use(int), lambda n: n>0)
OPTCOLNUM_VALIDATOR = Or(And(None, Use(lambda n: 1)), COLNUM_VALIDATOR)

COMMON_ARGS_DOC = """\
  --verbose, -v  be verbose
  --version, -V  show script version
  --help, -h     show this help message"""

COMMON_ARGS_SCHEMA = {Optional("--verbose", default=None): \
                         Or(None, True, False),
                      Optional(str): object}

REPORT_ARGS_SCHEMA = {"--report": OUTFILE_OR_STDERR_VALIDATOR,
                      "--user": Or(str, None),
                      "--reason": Or(None, lambda r: r in Report.REASONS),
                      "--system": Or(str, None),
                      "--params": YAMLFILE_VALIDATOR}

REPORT_ARGS_DOC = """\
  --report, -r FN   computation report file (default: stderr)
  --user U          user_id for the report (default: getpass.getuser())
  --system S        system_id for the report (default: socket.gethostname())
  --reason R        reason field for the report (default: None)
  --params FNAME    YAML file with additional parameters (default: None)"""

REPORT_SNAKE_ARGS = {"input": ["--params"], "output": ["--report"],
                     "params": ["--user", "--system", "--reason"]}

def validate(args, *dicts):
  s = COMMON_ARGS_SCHEMA.copy()
  for d in dicts:
    s.update(d)
  return Schema(s).validate(args)
