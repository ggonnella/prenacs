#
# (c) 2022, Giorgio Gonnella, University of Goettingen, Germany
#

from schema import Or, And, Use, Optional, Schema

COLNUM_VALIDATOR = And(Use(int), lambda n: n>0)
OPTCOLNUM_VALIDATOR = Or(And(None, Use(lambda n: 1)), COLNUM_VALIDATOR)

ARGS_DOC = """\
  --verbose, -v    be verbose
  --version, -V    show script version
  --help, -h       show this help message"""

ARGS_SCHEMA = {Optional("--verbose", default=None): Or(None, True, False),
                                                    Optional(str): object}

def validate(args, *dicts):
  s = ARGS_SCHEMA.copy()
  for d in dicts:
    s.update(d)
  return Schema(s).validate(args)
