
# Constants

Actually, Python does not really have constants. However, by convention,
variables names written in ``UPPER_CASE`` are considered constants.

Module-level constants are useful e.g. for defining special values,
for defining hard-coded module parameters, or for storing metadata
(for example, a plugin version number, or a description of possible
plugin parameters).

Constants supported by all languages implementations are of 3 types:
- "strings": scalar values of type string
- "lists": lists/tuples of strings
- "nested": lists/tuples of lists/tuples of strings.

In Python plugins, the constants are simply defined in the module code.
For the other languages, some conventions are described below.

## Bash

Constants are defined by setting a variable and adding
the variable name to the ``api_config[<K>]["constants"][<T>]`` list,
where ``<K>`` is ``required`` or ``optional`` and ``<T>`` is
one of: ``strings``, ``lists`` or ``nested``.

For strings the variable is set to the string value of the constant.
For lists, an array is used.
For nested, an array is used, where each group of elements (the top level)
is separated by a newline and the single elements (the bottom level)
are separated by a tabulator.

Examples:
```
STRING_FOO1="bar1"
LIST_FOO2=( "bar21" "bar22" )
NESTED_FOO3=( "bar311\tbar312\n"
              "bar321\tbar322" )
```

## Nim

Since the ``nimpy/nimporter`` system does not allow to export Nim constants
directly to Python, a workaround is used instead. The constants are defined
as the return value of functions (which are exportable to Python).

The constant-defining functions take no arguments, return the value
which must be assigned to the constant and are idenfied by a prefix of
their name. By default they start with ``py_const_`` - but the prefix can be
changed in the API configuration (see above). When the module is imported,
the function is called and the constant - named after the function
with the prefix stripped - is assigned to its return value.
The function itself is then deleted from the module.

An example would be:
``proc py_const_FOO(): string = "bar"``

### Using the ``exportpy_consts`` macro

The directory ``pyplugins_nim`` contains a nimble package, with the module
``exportpy_consts``, which simplifies the definition of constants.

The macro ``exportpy_consts`` takes the name of one or multiple macros
and generates the necessary procs with the prefix `py_const_`, e.g.:
```
import pyplugins_nim/exportpy_consts
const
  FOO="foo"
  BAR="bar"
exportpy_consts(FOO, BAR)
```

If the prefix is set in the API configuration to a different string
(`<pfx>`), the macro ``exportpy_consts_wpfx(<pfx>, FOO, BAR)`` is used instead.

## Rust

Since the ``PyO3/maturin`` system does not allow to export Rust module-level
constants to Python, a workaround is used instead. The constants are defined
in a struct called ``Constants`` and exported as Python class
(a different name for the class can be
alternatively set by using the API configuration, see above).

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
