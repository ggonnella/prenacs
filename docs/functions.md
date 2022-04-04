This document explains how to export functions to Python for plugins
which are not implemented in Python.

## Nim

For Nim plugins, the ``.exportpy.`` pragma from the  ``nimpy`` Nim library
is used. Consult the ``nimpy`` documentation for more information.

A minimal example is given here:
```
import nimpy
proc foo(bar: string): seq[string] {.exportpy.} = @["foo", "bar"]
```

## Rust

For Rust plugins, the ``PyO3`` library is used. Consult the library
documentation for more information.

A minimal example is given here:
```
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn foo(bar: &str) -> PyResult<Vec(String)> { Ok(vec!["foo", "bar"]) }

#[pymodule]
fn fas_stats_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    Ok(())
}

```

## Bash

Bash functions are defined using some conventions, which allow to automatically
create their Python wrappers.

### Supported arguments

The supported interface is the following:
- the function has a given, predefined, number of positional arguments
- optional keyword arguments are accepted - but can be provided only if
  all positional arguments have been specified

To achieve this interface, shifts are used on each positional argument,
then an eval-based system is used for setting the keyword arguments
from the remaining arguments:
```
function foo() {
  arg1=$1; shift; arg2=$1; shift # shift after each positional argument ...

  # ...so that the remaining arguments are the keyword arguments
  kwargs=$*; for kw in $kwargs; do eval $kw; done
  ...
}
```

In Python, this is wrapped in code, which accepts any number of positional
arguments - it's the caller responsibility to make sure that the right
number of positional arguments is provided. After the positional arguments,
any number of keyword arguments is accepted.

Correcting calling the function defined above:
```
foo(val1)
foo(val1, val2)
foo(val1, val2, key3=val3)
foo(val1, val2, key3=val3, key4=val4)
```

Wrong calls:
```
foo(val1, val2, val3) # too many positionals
foo(val1, key3=val3) # actually arg2 is set to "key3=val3" by this...
```

### Return value

Differently than with the other languages, Bash does not
allow to easily support any kind of return value.
Instead, the wrapped code will always return strings.

The value to be returned is printed by the Bash function to the
standard output using ``echo``.

In order to support multiple return values, the following convention
is used:
- if no newlines and tabulators are present, then a scalar string
  value is returned
- if newlines or tabulators are present, but not both, the standard
  output is split by them and a list of strings is returned
- if both newlines and tabulators are present, a list of lists is
  returned, by first splitting by newlines and then splitting each of
  the elements by tabulators

Examples
```
  echo "123" # ==> "123" is returned (string)
  echo "1/t2" # ==> ["1", "2"] is returned (list)
  echo "1/n2/t3" # => [["1"], ["2", "3"]] is returned (nested list)
```

