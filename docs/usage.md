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
constant importing mechanisms.

The definition of constants in the plugin modules is explained in
the ``constants.md`` document, and the definition of functions
in the ``functions.md`` document.

# Limitations of Bash plugins

Bash plugins have some limitations, compared to Python, Rust and Nim plugins:
- a list of required and optional constants and functions _must_ be provided
  in ``api_config`` -- this is usually not a big limitation, since the calling
  code will usually know this information anyway in order to use those functions
  and constants
- the return type can only be string, a list of strings or a list of lists
  of strings

If this limitations are undesired in an application, bash plugins can be
switched off by setting ``api_config["disable_bash"]`` (see below).

# API Configuration

The API configuration parameter ``api_config`` of the importer functions
is a dictionary. It may contain the following keys (any other key is ignored):
  - ``required``: section definining the required constants and functions;
    if they are not found, an exception is raised
  - ``optional``: section definining the optional constants and functions;
    if they are not found, they are set to None
  - ``disable_bash``: disable support of bash plugins
  - ``nim_const_pfx``: a string, the prefix used for
    the Nim module constants definition mechanism (see below); the default
    value is ``py_const_``
  - ``rust_const_klass``: a string, the class name used for
    the Rust module constants definition mechanism (see below); the default
    value is ``Constants``

The values for the two keys ``required`` and ``optional``
are dictionaries which may contain the following keys:
  - functions: a list of function names to be imported
  - constants: a dictionary of lists of "constants" to be imported.
    The keys are "strings", "lists" and "nested".
    The values are lists of names of constants.

For Bash plugins any other function or variable defined in the script is
not imported. Plugin developed in other languages import also any
other defined function or constant.

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
