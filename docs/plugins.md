# ProvBatch: Plugin implementation guide

This document describes the interface of plugins for ProvBatch.

Plugins are used for computing _attributes_, i.e. values associated to each
_entity_. Each plugin computes one or multiple attributes. Each attribute can
consist in a single value or a group of values (e.g. a computation result and a
score).

Plugins can be written in Python, Nim, Rust and Bash.
The plugins system is implemented as a separated package (MultiPlug).

## Public Interface of ProvBatch plugins

A plugin must provide the following attributes:
- ``ID``, ``VERSION``, ``INPUT``, ``OUTPUT``:
  constants describing the plugin itself,
  the data returned by it and the resources necessary for the computation
- ``compute()``: a function which computes the value of the attribute(s) for
  a given entity; it may accept computation parameters

Furthermore, a plugin may provide additiional attributes:
- ``METHOD``, ``IMPLEMENTATION``, ``REQ_SOFTWARE``,
  ``REQ_HARDWARE``, ``ADVICE``, ``PARAMETERS``: further metadata constants for
   plugin description
- ``initialize()`` and ``finalize()``: functions for setting up and deleting
  resources used for an entire batch computation (e.g. library or database
  initializations); these functions are called only once (at the beginning and
  end of the batch computation), while ``compute`` is callled for each entity
  of the batch

### Compute function

The plugin shall export the `compute(entity, **kwargs)` function:
- `entity`: identifier of the input data, or name of the file with the input data
- `kwargs`: additional optional named parameters (described in the PARAMETERS
            constant, see "Metadata constants section" below); note the
            special role of the `state` keyword argument if initialize()
            is defined, see "Shared resources for batch computations" below)

The return value of the method is a 2-tuple `(results, logs)`
where:
 - `results`: list of values, in the order specified by
              the `OUTPUT` constant (see below),
 - `logs`: a possibly empty strings list, containing messages to be displayed
           to the user or stored in a log file;
           suggested format: "{key}\t{message}",
           where key identifies the type of log message.

### Metadata constants

The plugin communicates its purpose, version and interface by defining
the following constants.

Mandatory (their combination must be unique among all plugins):
 - `ID`:      name of the plugin              [str, max len 256]
 - `VERSION`: a version number or name        [str, max len 64]

Mandatory:
 - `INPUT`:   short description of the input (type of data, format, source)
              [str, max len 512]
 - `OUTPUT`:  list of strings (attribute ids), describing the order or the
              attributes in the output; each of them must be defined in
              `attribute_definitions.yaml`.

Required if compute() accepts named parameters:
 - `PARAMETERS`: optional named parameters of the compute function;
                 list of 4-tuples of strings:
                 (name, datatype, default_value, documentation)

Optional: (string, max len 4096)
 - `METHOD`:         how the results are computed, conceptually
 - `IMPLEMENTATION`: how the method is implemented, technically
 - `REQ_SOFTWARE`:   required tools or libraries
 - `REQ_HARDWARE`:   required hardware resources (memory, GPUs...)
 - `ADVICE`:         when should this method used instead of others

### Common resources for batch computations

Sometimes common resources are needed by multiple instances of a batch
computation For example, it could be necessary to parse data files, to load
some data into memory, or to initialize a connection to a database. Or some
statistics could be collected during the computation and output at the end.

The convention in Prenacs is that such resources are passed around (if they
exist) as a variable called ``state``. Due to the dynamic nature of Python
variables, this can be a single resource or a container (e.g. a dictionary)
to access multiple heterogenous resources.

#### Creating common resources

There are different ways to create resources which are accessed by all
instances of the batch computation.

First, the (initial) value of the ``state`` variable can be passed as one of the
parameters (called ``state``) of the batch computation.

Second, an initialization function can be implemented, with the signature
``initialize(**kwargs)``. If this is provided, the function is called before the
first instance of the batch computation. The batch computation parameters are
passed to it as keyword arguments. The return value of the ``initialize``
function is passed to the ``compute`` function as a keyword argument
called ``state``.

Third, these two approaches can be combined: i.e. a value for a ``state``
variable can be specified in the batch computation parameters. If an
``initialize`` function is provided, this reads the ``state`` variable, along
with any other parameter. The original value of ``state``
is then overwritten with the return value of the ``initialize`` function
and can be accessed by the ``compute`` functions.

#### Accessing common resources

The common resources are accessed by the plugins ``compute`` function
using a keyword parameter called ``state``. Thus if common resources are needed,
the function will take the signature: ``compute(entity, state=None, **kwargs)``.

While accessing the common information (in particular when this is not
read-only), it should be considered, that the computation can be started in
parallel (this is the default mode in the prenacs-batch-compute script).

#### Finalizing common resources

In some cases, it is necessary to do finalization operations at the end of the
batch computation - e.g. close some files or connections, or write some
information, collected during the computation.
In such cases a ``finalize(state)`` function can be implemented in the plugin.
It takes the final value of the ``state`` variable, and it is executed
after the last instance of ``compute``.

## Non-Python plugins

For details on how to implement plugins in Nim, Rust and Bash,
please refer to the MultiPlug package user manual.
This section provides some additional information which applies specifically
to ProvBatch plugins.

### Nim plugins

The compute function has the following signature, if there are no
optional parameters:

```
proc compute(entity: string):
             tuple[results: seq[string]], logs: seq[string]] {.exportpy.}
```

Any accepted optional parameter must be defined in the signature.
E.g. given two optional named parameters p1 of type t1 and default value d1
and p2 of type t2 and default value d2, the signature becomes:
```
proc compute(entity: string, p1: t1 = d1, p2: t2 = d2):
             tuple[results: seq[string]], logs: seq[string]] {.exportpy.}
```

Shared resources can be e.g. stored in a ref object, which is then passed
back and forth to Python:

```
type
  PluginState = ref object of RootObj
    state: int

# initialize returns the state
proc initialize(): PluginState {.exportpy.} = PluginState(state = 0)
# it can have optional keyword arguments
proc initialize(s: int = 0): PluginState {.exportpy.} = PluginState(state = s)

# if initialize is provided, then compute must have a mandatory `state`
#   keyword argument of the same type as the return value of initialize
proc compute(filename: string, state: PluginState, ...

# finalize is optional and takes the state as only argument
proc finalize(s: PluginState) {.exportpy.} = discard
```

### Rust plugins

The interface of the compute function when written in Rust is:
```rust
#[pyfunction] fn compute(filename: &str) -> PyResult<(...)> { ... Ok(...)
```
