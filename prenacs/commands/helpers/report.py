#
# (c) 2022, Giorgio Gonnella, University of Goettingen, Germany
#

from schema import Or, And, Use
import sys
import yaml
from prenacs.report import Report

YAMLFILE_VALIDATOR = Or(And(None, Use(lambda n: {})),
                        And(Use(open), Use(lambda fn: yaml.safe_load(fn))))

OUTFILE_OR_STDERR_VALIDATOR = Or(And(None, Use(lambda f: sys.stderr)),
                              Use(lambda f: open(f, "w")))

ARGS_SCHEMA = {"--report": OUTFILE_OR_STDERR_VALIDATOR,
               "--user": Or(str, None),
               "--reason": Or(None, lambda r: r in Report.REASONS),
               "--system": Or(str, None),
               "--params": YAMLFILE_VALIDATOR}

ARGS_DOC = """\
  --report, -r FN   computation report file (default: stderr)
  --user U          user_id for the report (default: getpass.getuser())
  --system S        system_id for the report (default: socket.gethostname())
  --reason R        reason field for the report (default: None)
  --params FNAME    YAML file with additional parameters (default: None)"""

SNAKE_ARGS = {"input": ["--params"], "output": ["--report"],
              "params": ["--user", "--system", "--reason"]}

