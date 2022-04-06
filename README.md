The MultiPlug library is used for creating flexible plugin systems
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
- basic aspects of the plugin interface (names of the required and optional
  module-level public functions and constants) can be specified and
  automatically checked

# Installation

The Python libraries listed in ``requirements.txt`` are installed automatically,
if MultiPlug is installed using ``pip``, and can otherwise be installed using
``pip install -r requirements.txt``.

For supporting plugins written in Nim, the Nim compiler must be installed in the
system and the _nimpy_ library installed, e.g. using ``nimble install nimpy``.

For supporting plugins written in Rust, the Rust compiler must be installed in
the system and the _PyO3_ library installed, e.g. using ``cargo install PyO3``.

# Usage

The usage of the library is explained in the
 [user manual](https://github.com/ggonnella/multi_plug/blob/main/docs/usage.md).
