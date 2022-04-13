# SnaCLI

SnaCLI is a library which simplifies writing scripts which can be both run
directly from the command line (based on docopt), as well as be called in a
Snakemake file.

## Introduction

In the _Snakemake_ workflow management system, tasks can call Python scripts
and pass them input, output and log filenames as well as global configuration
values and non-filename parameters.

The system for passing and accessing these arguments is different to that
adopted by command line tools (for example using the _docopt_ library).

SnaCLI allows to easily combine the two approaches (docopt and snakemake) for
providing arguments to a script. Script based on SnaCLI can be invoked both from
the command line and from snakemake. Inside the script, the
same code can be used in both cases, without modifications.

## Usage

The usage of the library is explained in the
 [user manual](https://github.com/ggonnella/snacli/blob/main/docs/usage.md).
