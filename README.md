The PyPlugins library is used for creating flexible plugin systems
for Python programs, supporting multiple programming languages.

For example, a CLI script based on this library can take the name of
a module as one of its command line arguments and import and use the module.
The user of the script will then select a plugin e.g. from a plugin collection
or writing it according to a given API specification.

# Features

Main features of the library:
- the library allows the dynamic import of a plugin module, given its filename
- plugins can be written in Python, Nim, Rust and Bash
- the calling code is (in most cases) independent of the plugin
  implementation language
- plugin modules are automatically (re-)compiled, when necessary
  (thanks to the _nimporter_ and _maturin_ libraries)
- a wrapper mechanism allows to support Bash plugins
- systems are provided for defining module-level constants when importing
  Nim and Rust modules
- basic aspects of the plugin interface (required and optional module-level
  public functions and constants) can be specified and
  automatically checked

# Requirements

This library is based on:
- the Python libraries listed in ``requirements.txt``
  (installable using ``pip``)
- for Nim plugins: the Nim compiler and the _nimpy_ library
  (installable using ``nimble``)
- for Rust plugins: the Rust compiled and the _PyO3_ library
  (installable using ``cargo``)

# Usage manual

See ``docs/usage.md``.
