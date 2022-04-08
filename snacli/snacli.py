"""
Helper function for combining the use of snakemake and docopt in scripts.
"""

def _setargs(args, src, *keys):
  """
  For each key in <keys>, set args[key] to
  src.get(name), where name is a transformation of the key
  as decribed below.

  This is to facilitate scripts to be called directly
  with option parsing by docopt or via snakemake "script".

  The <keys> must be strings such those returned by docopt,
  i.e. starting with "-", "--", enclosed in "<>", or be completely upper case.
  The name is derived from the key by removing these formatting chars
  and replacing internal "-" with underscores, and turning to lower case
  if they are completely upper case.
  Alternatively instead of a string, a 2-tuple of strings
  can be passed (key, name).

  If a name is not available in src, args[key] is set to None.

  E.g. _setargs(args, snakemake.input, "<file>")
       => args["<file>"] = snakemake.input.get("file")
       _setargs(args, snakemake.params, "--long-opt")
       => args["--long-opt"] = snakemake.params.get("long_opt")
  """
  for key in keys:
    if isinstance(key, tuple):
      name = key[1]
      key = key[0]
    else:
      if key.startswith("--"):
        name = key[2:]
      elif key.startswith("-"):
        name = key[1:]
      elif key[0] == "<":
        assert key[-1] == ">"
        name = key[1:-1]
      else:
        assert key == key.upper()
        name = key.lower()
      name = name.replace("-","_")
    args[key] = src.get(name)

def snake_args(snakemake, *dicts, **kwargs):
  """
  Create a args dict similar to the result of docopt,
  using the snakemake variable.

  First usage: one provides named arguments, which are lists of strings,
  where the name of the argument is the property of "snakemake" where
  to take the value from. The values are arguments keys, from which the keys
  of the snakemake property are computed, by removing the "--" or "<>".

  e.g.
    snake_args(snakemake, input=["<a>, "--b"], params=["--c", "<d>"],
                    output=["--e", "<f>"], config=["<g>, "--h"],
                    log=["--i", "<j>"])

  Second usage: instead or in addition to the previous, one provides
  dicts which contains lists of strings with key strings which are the
  properties of "snakemake". This allows to pass pre-defined lists of
  argument keys.

  e.g.
    snake_args(snakemake, {"input": ["<a>"], "params": ["--b"]},
                    {"input": ["<c>, "--d"], "output": ["<e>"]},
                    input=["<f>, "--g"], params=["--h"])
  or:
    snake_args(snakemake, my_module.predefined_args_list,
                    other_module.other_list,
                    input=["<f>, "--g"], params=["--h"])

  It is possible to override a key passed as one of the dicts, in one of the
  following dicts, or in the kwargs. However, one should avoid to use the same
  key multiple times in the same dict or in the keyed args, as in this case
  the behaviour is random!
  """
  args = {}
  for d in dicts:
    for k, v in d.items():
      _setargs(args, getattr(snakemake, k), *v)
  for k, v in kwargs.items():
    _setargs(args, getattr(snakemake, k), *v)
  return args

from contextlib import contextmanager
from docopt import docopt
import inspect

@contextmanager
def args(*dicts, doc=None, docvars=None, argv=None, help=True,
         version=None, options_first=False, **kwargs):
  glob = inspect.stack()[2][0].f_globals
  if "snakemake" in glob:
    # This is executed when the script is invoked by Snakemake.
    yield snake_args(glob["snakemake"], *dicts, **kwargs)
  elif glob["__name__"] == "__main__":
    # This is executed when the script is invoked from the command line.
    if doc is None:
      doc = glob["__doc__"]
    if docvars:
      # formatting must be applied here, since __doc__ is None
      # when called in snakemake, thus the docvars keyword
      if isinstance(docvars, dict):
        doc = doc.format(**docvars)
      else:
        doc = doc.format(*docvars)
    yield docopt(doc, argv=argv, help=help, version=version,
                 options_first=options_first)
  else:
    yield None
