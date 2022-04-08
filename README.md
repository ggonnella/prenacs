SnaCLI is a library which simplifies writing scripts which can be both run
directly from the command line (based on docopt), as well as be called in a
Snakemake file.

# Background

## Snakemake external Python scripts

_Snakemake_ (https://snakemake.github.io/) is a popular Python-based workflow
management system. Tasks in Snakemake are defined as rules in _Snakefiles_.

Each rule may define input files, output files and non-file parameters.
Rule definitions in the Snakefiles can call an external command using the
shell, directly contain code to be executed (e.g. Python code) or invoke an
external script (in different programming languages, including Python),
to which the rule parameters are passed.

The following is an example of calling an external Python script:
```
rule a:
  input:
    inputfile1="i1", inputfile2="i2"
  output:
    outputfile1="o1", outputfile2="o2"
  params:
    f="oo", bar=True
  script:
    script(path/to/example.py)
```

Inside the script ``example.py``, the input, output and params are
accessible from the attributes ``input``, ``output`` and ``params``
of the global variable ``snakemake``.

## CLI scripts based on docopt

_Docopt_ (http://docopt.org/) is a command line interface description language
with implementations in different languages, including Python.

The syntax of the script and the available options are described in a string,
which is passed to the ``docopt()`` function. For example:
```
Usage:
  test_script.py <inputfile1> <outputfile1> [INPUTFILE2] [options]

Options:
  -2, --outputfile2 FNAME   Output file 2 (default: stdout)
  -f VALUE                  Option with a value
  --bar                     Boolean option
```

The return value of the function is a dictionary, which contains the values
of options and positional arguments. In this example it would contain
the keys ``"<inputfile1>", "INPUTFILE2", "--outputfile1", "-x", "--bar"``.

# SnaCLI

SnaCLI allows to easily combine the two approaches (docopt and snakemake) for
providing arguments to a script. Therefore the script can be invoked both from
the command line and from snakemake.

This is obtained by employing the ``snacli.args()`` context manager.
Lists are passed to ``args()`` describing how to obtain from the snakemake
rule the values of options and positional arguments described in the docopt
string.

For the examples given above:
```
with snacli.args(input=["<inputfile1>", "INPUTFILE2"],
                 output=["<outputfile1>", "--outputfile2"],
                 params=["--param1"]) as args:
   # code which does something with args, as if they would
   # come from docopt, e.g.
   print(args["<inputfile>"])
```

The value yielded from the context manager is then always equivalent to the
value returned by ``docopt()``, both in the case that the script is invoked
from the command line and that it is called from a Snakefile. Thus, the
same code can be used in both cases, without modifications.

## Mapping of docopt keys to snakemake names

Although Snakefiles support both named filenames (e.g. ``input:
input1="file1"``) and unnamed filenames (e.g. ``input: "file1"``) in the input
and output keys, for SnaCLI to work, all filenames must be named.

The docopt keys contain formatting: ``UPCASE`` or ``<angular>`` for
positional arguments, an initial ``-`` or ``--`` for options.
These cannot be used directly as names in the input, output and params
of snakemake rules. Thus the ``snacli.args()``
maps each docopt key value to a snakemake name value, by stripping the
initial ``-`` or ``--``, removing the angular brackets and making upcase-only
keys lowcase. If further ``-`` are present, they are replaced
by an underscore.

Examples of docopt keys and the corresponding snakemake name:
- ``<inputfile1>``: ``inputfile1``
- ``INPUTFILE2``: ``inputfile2``
- ``--param1``: ``param1``
- ``-x``: ``x``
- ``--long-name``: ``long_name``

### Customized docopt key to snakemake name mapping

It is possible to manually override the mapping of docopt keys
to snakemake names by using, in the lists passed to ``snacli.args()``,
a 2-tuple ``(docopt_key, snakemake_name)`` instead of a string.
Eg. to map ``--param-2`` to ``param2`` instead of ``param_2``:
```
# in the snakefile:
rule foo:
  params: param2: "value"
  script: "foo.py"

# in foo.py:
with snacli.args(params=["--param1", ("--param-2", "param2")]) as args:
  print (args["--param-2"])
  ...
```

## Passing options to docopt

By default, the docstring of the script (``__doc__``) is passed to ``docopt()``
as string. Another string can be used instead, by passing it to the keyword
argument ``doc``, e.g.
```
with snacli.args(doc=somestring, input= ...
```

Besides the lists of input, output and params, the ``snacli.args()`` also
accepts keyword arguments which are passed to ``docopt()``, i.e. ``argv``,
``help``, ``version``, ``options_first`` -- see the docopt documentation
for their meaning, e.g.
  ```
with snacli.args(version="1.0", input= ...
```

## Using a script also as a non-interactive module

Sometimes a script shall be also used as non-interactive, i.e. imported as module
in another Python module.

In case the script is imported as module, the value yielded by the
``snacli.args()`` context manager will be ``None``.
Thus to support inclusion as a module, an additional ``if`` condition
must be added, e.g.:
```
with snacli.args(...) as args:
  if args:
    ...
```

## Reusing argument definitions in multiple scripts

If the same arguments are used in multiple scripts, they can be collected in
a separate module and re-used.

For example, say that the optional arguments
``--input1`` and ``--param2`` are used in multiple scripts.
Then the docstring of a script could be set to:
```
  Usage:
    foo [options]

  Options:
    --specific    Specific option for this script only
    {}
```
The definition string for the options and the mapping of docopt strings
to snakemake could be provided in a module ``bar``, which can be reused
also in other scripts, e.g.:
```
optstr='''
    --input1         Input filename 1
    --param2 VALUE   Value of parameter 2
'''

optmap = {"input": ["--input1"], "params": ["--param2"]}
```

Then in the script, SnaCLI can be used as follows:
```
import bar
with snacli.args(bar.optmap, docvars=[bar.optstr]),
                 params = ["--specific"]) as args:
  ...
```

I.e. the common mapping is passed as positional argument to ``snacli.args``,
before any keyword argument, and the docvars keyword argument is used,
with the arguments which shall be passed to ``format()``
called on the docopt string.

This can be generalized over multiple re-usable modules, e.g.:
```
...
  Options:
    {bar_opts}
    {foo_opts}
...

import foo
import bar
with snacli.args(foo.optmap, bar.optmap,
                 docvars={"bar_opts": bar.optstr,
                          "foo_opts": foo.optstr},
                 params = ["--specific"]) as args:
  ...
```

### Multiple entries for the same key

It is possible to override the name mapping for a key passed with a
positional argument, using one of the following positional arguments, or in the
keyword arguments.

In the example above, if foo.optmap contains ``{inputs =
["--specific"]}``, the later setting in the keyword argument ``params`` would
be applied instead, i.e. ``specific`` would be taken from ``params`` and not
from ``inputs``.

Instead, using the same key in
different lists of the same positional argument, or in different keyword
arguments is an error, leading to unspecified behaviour.
