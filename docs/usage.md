# Importing a plugin module

To import a plugin module, the function ``multiplug.importer(filename)`` is
used. The function automatically determines the plugin implementation
language from the file extension (``.rs`` for Rust, ``.sh`` for Bash, ``.nim``
for Nim, ``.py`` for Python).
To load a plugin with a specific language only, use one of the functions
``bash(filename)``, ``rust(filename)``, ``py(filename)`` or ``nim(filename)``.

Additionally to the filename the following named parameters are available:
- ``verbose``: output verbose messages
- ``disable_bash`` (``importer()`` function):
  if set, only Rust, Python and Nim plugins are supported
- ``req_const``, ``req_func``: list of names of constants and functions,
  which _must_ be provided by the module; an exception is raised otherwise
- ``opt_const``, ``opt_func``: list of names of constants and functions,
  which _may_ be provided by the module and are set to ``None`` if not provided
- ``nim_const_pfx``: prefix to use in the Nim constants export system
  (default: ``py_const_``)
- ``rust_const_cls``: name of the class to use in the Rust constants export
  system (defailt: ``Constants``)

# Bash plugins limitations

For plugins written in Bash there are some limitations:
- the return type of the functions, and the constants type is limited to:
  - strings
  - lists of strings
  - lists of lists of string
- the function arguments are not checked, i.e. the wrapped function interface
  is always ``(*args, **kwargs)``
- the script code is sourced multiple times in order to collect information
  about the defined functions and constants

If this limitations are undesired in an application, bash plugins can be
disabled by setting ``disable_bash``.

# Plugin Functions

In Python plugins, functions are just defined as in any Python module.
In Nim plugins, the ``{.exportpy.}`` pragma from the  ``nimpy`` Nim library
is used. Consult the ``nimpy`` documentation for more information.
In Rust plugins, the ``PyO3`` library is used. Consult the library
documentation for more information.
In Bash plugins, functions are defined using some conventions, described
below, which allow to automatically create their Python wrappers.

## Bash functions arguments

All exported functions defined in Bash plugins are wrapped in a function
which accepts any number of arguments and keyword arguments
(``(**args, **kwargs)``).

The Bash function, however, may only accept a defined number of positional
arguments. An eval-based system is used for passing the keyword arguments, e.g.:
```
function foo() {
  arg1=$1; shift; arg2=$1; shift # shift after each positional argument

  # the remaining arguments are the keyword arguments
  kwargs=$*; for kw in $kwargs; do eval $kw; done
  ...
}
```

## Bash function return value

To return a value from Bash, a string is printed using "echo".
For that reason function shall not print anything else than the return value
(however, it may use the standard error freely).

If the returned string contains multiple lines or tabs, the wrapper
splits it into an list of strings. If both newlines and tabs are returned,
the string is splitted first by newline, then by tabs, and a list of lists of
strings is returned by the wrapper. Examples:
```
  echo "123" # ==> "123" is returned (string)
  echo "1/t2" # ==> ["1", "2"] is returned (list)
  echo "1/n2/t3" # => [["1"], ["2", "3"]] is returned (nested list)
```

# Constants

Actually, Python does not really have constants. However, by convention,
variables names written in ``UPPER_CASE`` are considered constants.

Module-level constants are useful e.g. for defining special values,
for defining hard-coded module parameters, or for storing metadata
(for example, a plugin version number, or a description of possible
plugin parameters).

In Python plugins, the constants are simply defined in the module code.
For the other languages, some conventions are described below.

## Bash

Constants are defined as variables in the script code.
Only variables whose name does not start with an underscore are imported.

Scalar variables are imported as string constants.
Arrays are imported as lists of strings.
If any element of the array contain a tab, each of the elements
is splitted by tab, so that the constant value is a list of lists.

Examples:
```
STRING_FOO1="bar1"
LIST_FOO2=( "bar21" "bar2 2" )
NESTED_FOO3=( "bar311"
              "bar3 21\tbar322" )
```

## Nim

Since the ``nimpy/nimporter`` system does not allow to export Nim constants
directly to Python, a workaround is used instead. The constants are defined
as the return value of functions (which are exportable to Python).

The easiest way to import constants is to install the nimble package
``multiplug_nim`` (distributed with the source code of PyPlugins) and
use the macro ``exportpy_consts()``, e.g.:
```
import multiplug_nim/exportpy_consts
const
  FOO="foo"
  BAR="bar"
exportpy_consts(FOO, BAR)
```

### Implementation details

For each constant, a proc with no arguments is defined in the Nim code,
which returns the value of the constant. The proc name has a prefix
(by default ``py_const_`` which allows to recognize it and is stripped
in the definition of the Python module attribute.
E.g.: ``proc py_const_FOO(): string {.exportpy.} = "bar"``
defines the attribute ``FOO`` with value ``"bar"`` in Python.

### Using a custom prefix

The prefix used in the proc names (by default ``py_const_``) can be changed by
setting the ``nim_const_pfx`` parameter of the importer function. In this case
in the Nim code, the macro ``exportpy_consts_wpfx(pfx, ...)`` is used in place
of the ``exportpy_consts()`` macro, where the first parameter is the same
prefix used in the ``nim_const_pfx`` parameter in the importer function in
the Python code.

## Rust

Since the ``PyO3/maturin`` system does not allow to export Rust module-level
constants to Python, a workaround is used instead. The constants are defined
in a struct called ``Constants`` and exported as Python class

For example:
```
#[pyclass] struct Constants {}
#[pymethods]
impl Constants { #[classattr] const FOO: &'static str = "bar"; }

...

#[pymodule]
fn my_module(_py: Python, m: &PyModule) -> PyResult<()> {
  m.add_class::<Constants>()?;
  ...
```

### Using a custom class name

Instead of ``Constants`` a different class name can be specified,
by setting the ``rust_const_cls`` keyword parameter in the importer function
to a different string.

# Persistant state between function calls

To implement a state which shall persist between function calls, the plugin
shall implement an initialization function, creating the state, a
finalization function, destroying the state (if necessary). The other function
calls shall then take the state as an argument.

Examples of plugins using a persistant state in all supported programming
languages are in the ``tests/testplugins`` directory.

For Python and Nim it is not particularly challenging to have an initialization
function, which creates a new state object, and pass the state as an argument
to other functions.

## Rust

In Rust the state can be implemented as a ``struct``, e.g. ``struct State``.
The initialization function will return a ``PyResult<Py<State>>``. Thereby the
state is created using ``Py::new(py, State {...})``, where ``py`` is obtained
using ``Python::acquire_gil().python()``.

The state is passed then to other functions (including the finalization
function, if any) as the ``state: Py<State>`` argument. To change the state
``let mut state = state.borrow_mut(py)`` can be used, where ``py`` is obtained
as explained above.

## Bash

In Bash the state can be implemented by storing it to file. The initialization
function can create a state file using $(mktemp) and storing some information
to the file, then returning the filename.
Other functions then get the state filename as an argument.

For example the information can be
stored in form of variable assignments (e.g. ``x=1``). Functions other than
the initialization get then the state filename as argument. The contents
of the file can be executed using ``eval $(cat $state_file)``.
If the variable are modified, the previous state file can be overwritten
with new variable assignment statements (e.g. ``x=2``).


