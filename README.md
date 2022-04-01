PyPlugins is a Python library for supporting plugin modules for command line
scripts, written in different programming languages (Python, Nim, Rust).

The user writes a plugin module, according to a pre-defined interface.
Then the user passes the plugin module name to a CLI script, which supports
such plugins - based on the PyPlugins library. If necessary, the plugin module
is automatically compiled. The pre-defined interface of the plugin module
is then used by the CLI script.

