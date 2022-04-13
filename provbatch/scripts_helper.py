from schema import Or, And, Use
import sys
import yaml
from provbatch.report import Report

yamlfile = Or(And(None, Use(lambda n: {})),
              And(Use(open), Use(lambda fn: yaml.safe_load(fn))))
outfile_or_stderr = Or(And(None, Use(lambda f: sys.stderr)),
                    Use(lambda f: open(f, "w")))

report_args_schema = {"--report": outfile_or_stderr, "--user": Or(str, None),
                      "--reason": Or(None, lambda r: r in Report.REASONS),
                      "--system": Or(str, None), "--params": yamlfile}

report_args_doc = """\
  --report, -r FN   computation report file (default: stderr)
  --user U          user_id for the report (default: getpass.getuser())
  --system S        system_id for the report (default: socket.gethostname())
  --reason R        reason field for the report (default: None)
  --params FNAME    YAML file with additional parameters (default: None)"""

report_snake_args = {"input": ["--params"], "output": ["--report"],
                     "params": ["--user", "--system", "--reason"]}
