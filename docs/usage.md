# Importing a plugin module

To import a plugin module, the function
``pyplugins.importer(filename, api_config = {}, verbose = False)`` is used.
This automatically determines the plugin implementation language from the
file extension (``.rs`` for Rust, ``.sh`` for Bash).

If only modules of a given language are allowed, then the following functions
can be used instead:
- ``pyplugins.bash(filename, api_config = {}, verbose = False)``
- ``pyplugins.rust(filename, api_config = {}, verbose = False)``
- ``pyplugins.nim(filename, api_config = {}, verbose = False)``
- ``pyplugins.py(filename, api_config = {}, verbose = False)``

Listing functions and constants in the ``api_config`` parameters (see below)
is necessary for Bash plugins. For plugins implemented in other languages,
it is not necessary, but it can be employed for checking that the required
functions and constants are defined and for specifying parameters of the
constant importing mechanisms (see below).

# API Configuration

The API configuration is provided to the module importing functions
as the ``api_config`` parameter.

It may contain the following keys:
  - ``required``: section definining the required constants and functions
  - ``optional``: section definining the optional constants and functions
    (useful only for Bash plugins, see below)
  - ``nim_const_pfx``: a string, the prefix used for
    the Nim module constants definition mechanism (see below); the default
    value is ``py_const_``
  - ``rust_const_klass``: a string, the class name used for
    the Rust module constants definition mechanism (see below); the default
    value is ``Constants``

Any other key is ignored.

The two sections are dictionaries which may contain the following keys:
  - functions: a list of function names to be imported
  - constants: a dictionary of constants to be imported.
    The keys are "strings", "lists", "nested" and "lists".
    The values are lists of constant names.

For constants and functions are defined unded the key "required", an error
will be raised if they are not found. Constants and functions defined
under the key "optional" will be imported if they are found, while their
absence is silently ignored.

For Bash plugins any other function or variable defined in the script is
not imported. Plugin developed in other languages import also any
other defined function or constant: thus is this case it is not necessary
to list them under the ``optional`` key.

An example value of the ``api_config`` parameter:
```
  api_config = {
    "required": {
        "constants": {"strings": ["S1"], "lists": ["S2"], "nested": ["S3"]},
        "functions": ["F1", "F2"],
      },
    "optional": {
        "constants": {"strings": ["S4"], "nested": ["S6", "S7"]},
        "functions": ["F3"],
      },
    }
```

